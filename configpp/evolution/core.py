import logging
import os
import random
import shutil
from collections import OrderedDict, defaultdict
from typing import Dict

from voluptuous import Schema
from configpp.soil import Config, ConfigBase, Group, GroupMember, YamlTransform, create_from_url

from .chain import Chain
from .exceptions import EvolutionException
from .revision import Revision
from .utils import decorate_logger_message

logger = logging.getLogger(__name__)

class Evolution():

    DEFAULT_FOLDER = 'evolution'

    CONFIG_SCHEMA = Schema({
        'script_location': str,
        'revision_template_file': str,
        'configpp_urls': Schema({
            str: str,
        })
    }, required = True)

    def __init__(self, config: dict = None):
        logger.info("Evolution started. (init config: %s)", config)
        self._config = config
        self._versions_folder = None # type: str
        self._versions_folder_name = 'versions'
        self._config_filename = 'evolution.yaml'
        self._yaml = YamlTransform()
        self._chain = None # type: Chain
        if config:
            self.load(config)

    @property
    def chain(self) -> Chain:
        return self._chain

    def init(self, folder):
        if os.path.exists(folder):
            logger.error("Target folder '%s' is already exists!", folder)
            return False

        os.mkdir(folder)
        logger.info("Create directory %s", folder)

        versions_folder = os.path.join(folder, self._versions_folder_name)
        os.mkdir(versions_folder)
        logger.info("Create directory %s", versions_folder)

        target_template_path = os.path.join(folder, os.path.basename(Revision.ORIGINAL_TEMPLATE_FILE_PATH))
        shutil.copyfile(Revision.ORIGINAL_TEMPLATE_FILE_PATH, target_template_path)

        self._config = {
            'script_location': folder,
            'revision_template_file': target_template_path,
            'configpp_urls': {},
        }

        self.save_config()

        return True

    def check(self):
        if self._config is None:
            raise EvolutionException("Config not loaded yet")

        if not os.path.isdir(self._versions_folder):
            raise EvolutionException("Folder not exists: {}".format(self._versions_folder))

    def load(self, config: dict = None):
        self._config = config

        if not self._config:
            if not os.path.exists(self._config_filename):
                logger.error("Config file '%s' not found!", self._config_filename)
                return False
            with open(self._config_filename) as f:
                self._config = self._yaml.deserialize(f.read())

        Evolution.CONFIG_SCHEMA(self._config)

        self._versions_folder = os.path.join(self._config['script_location'], self._versions_folder_name)

        if not os.path.isdir(self._versions_folder):
            logger.error("Versions file '%s' not found!", self._versions_folder)
            return False

        self._chain = Chain(self._versions_folder)
        self._chain.build()

        logger.debug("Chain has been built successfully. Length: %s", len(self._chain))

        return True

    def save_config(self):
        content = self._yaml.serialize(self._config)

        logger.debug("Config is serialized: \n%s", content)

        with open(self._config_filename, 'w') as f:
            f.write(content)

        logger.info("Config has been saved.")

    def revision(self, message: str, new_config_url: str = None) -> Revision:
        """Generate revsion

        limitations: invalid member collection: core.yaml AND core.json

        Args:
            message: revision message
            new_config_url: config url in configpp.soil format

        Returns:
            Revision: the created revision

        Raises:

        Scenarios:
             1. first rev, single config                ✔
             2. first rev, group config                 ✔
             3. single config not changed               ✔
             4. group config not changed                ✔
             5. single config change to group config    ✔
             6. group config change to single config    ✔
             7. group config add new member             ✔
             8. group config del member                 ✔
             9. single config change name               ✔
            10. group config change name                ✔
            11. group member config change name         ✔ (add/del)
            12. single config change transform          ✔
            13. group config member change transform    ✔
            14. use custom transform                    ✔
            15. use custom transport                    ✔
        """

        logger.info("Create revision, msg: '%s'", message)
        self.check_loaded()

        # TODO: handle url

        config_urls = self._config['configpp_urls']

        if len(config_urls) == 0 and new_config_url is None:
            logger.error("There is no config url configured in the %s!", self._config_filename)
            return None # TODO: raise instead of return None

        upgrade_args = []
        downgrade_args = []
        upgrade_ops = ['']
        downgrade_ops = ['']
        extra_imports = defaultdict(set)

        new_config = None
        old_config = None

        if new_config_url:
            new_config = create_from_url(new_config_url)

        def get_config_varname(member: GroupMember):
            return os.path.splitext(member.name)[0]

        def generate_group_member_creation_code(member: GroupMember):
            varname = get_config_varname(member)
            return varname, "GroupMember('{}', {}())".format(member.name, member.transform.__class__.__name__)

        def generate_config_creation_code(config, return_var_name = 'config'):
            ops = []

            if isinstance(config, Group):
                member_var_names = []
                for member in config.members.values():
                    varname, ctor = generate_group_member_creation_code(member)
                    member_var_names.append(varname)
                    ops.append("{} = {}".format(varname, ctor))

                ops.append("{} = Group('{}', [{}], {}())".format(return_var_name, config.name, ', '.join(member_var_names),
                                                                 config.transport.__class__.__name__))
            else:
                ops.append("{} = Config('{}', {}(), {}())".format(return_var_name, config.name, config.transform.__class__.__name__,
                                                                  config.transport.__class__.__name__))

            return ops

        def collect_transform_imports(config):
            if isinstance(config, Group):
                for member in config.members.values():
                    tr_cls = member.transform.__class__
                    extra_imports[tr_cls.__module__].update([tr_cls.__name__])
            else:
                tr_cls = config.transform.__class__
                extra_imports[tr_cls.__module__].update([tr_cls.__name__])

        def collect_transport_imports(config):
            tr_cls = config.transport.__class__
            extra_imports[tr_cls.__module__].update([tr_cls.__name__])

        if len(config_urls) == 0:

            upgrade_ops.append("# This is an auto generated code to create example config for your app. Remove if you want to.")

            # scenario #1, #2
            upgrade_ops += generate_config_creation_code(new_config)

            upgrade_ops.append("# Need to set some location, because this is the first revision. Modify it accordingly.")
            upgrade_ops.append("config.location = Location('/etc')")
            upgrade_ops.append("return config")

            config_urls['head'] = new_config_url

            collect_transform_imports(new_config)
            collect_transport_imports(new_config)

        else:
            old_config = create_from_url(config_urls['head'])
            collect_transform_imports(old_config)
            collect_transport_imports(old_config)

            def gen_args_for_config(cfg):
                if isinstance(cfg, Group):
                    return ['%s: GroupMember' % get_config_varname(m) for m in cfg.members.values()] + ['config: Group']
                else:
                    return ['config: Config']

            # scenario #3, #4
            upgrade_args += gen_args_for_config(old_config)

            if new_config:
                config_urls[self._chain.head] = config_urls['head']
                config_urls['head'] = new_config_url
                collect_transform_imports(new_config)
                collect_transport_imports(new_config)

                if type(new_config) != type(old_config): # scenario #5, #6
                    upgrade_ops += generate_config_creation_code(new_config, 'new_config')
                    upgrade_ops.append("new_config.location = config.location")
                    upgrade_ops.append("return new_config")

                else:
                    if isinstance(new_config, Group):
                        old_config_member_names = list(map(get_config_varname, old_config.members.values()))
                        new_config_member_names = list(map(get_config_varname, new_config.members.values()))

                        members_to_create = [m for m in new_config.members.values() if get_config_varname(m) not in old_config_member_names]
                        members_to_remove = [m for m in old_config.members.values() if get_config_varname(m) not in new_config_member_names]

                        for member in members_to_create: # scenario #7
                            varname, ctor = generate_group_member_creation_code(member)
                            upgrade_ops += [
                                "{} = {}".format(varname, ctor),
                                "%s.data = {} # put initial data here" % varname,
                                "config.add_member(%s)" % varname,
                            ]

                        for member in members_to_remove: # scenario #8
                            upgrade_ops += [
                                "config.members['%s'].remove()" % member.name,
                                "del config.members['%s']" % member.name,
                            ]

                        for name, member in new_config.members.items(): # scenario #13
                            if name in old_config.members:
                                continue
                            varname = get_config_varname(member)
                            if varname not in old_config_member_names:
                                continue
                            upgrade_ops.append("{}.transform = {}()".format(varname, member.transform.__class__.__name__))

                        if new_config.name != old_config.name: # scenario #10
                            upgrade_ops.append("config.name = '%s'" % new_config.name)

                    else:

                        if new_config.name != old_config.name:
                            if get_config_varname(old_config) == get_config_varname(new_config): # scenario #12
                                upgrade_ops.append("config.transform = %s()" % new_config.transform.__class__.__name__)
                            else: # scenario #9
                                upgrade_ops.append("config.name = '%s'" % new_config.name)


        extra_imports_lines = []
        for module_name, class_names in extra_imports.items():
            extra_imports_lines.append("from %s import %s" % (module_name, ', '.join(sorted(class_names))))

        extra_params = {
            'extra_imports': '\n'.join(extra_imports_lines),
            'upgrade_args': ', '.join(upgrade_args),
            'downgrade_args': ', '.join(downgrade_args),
            'upgrade_ops': '\n    '.join(upgrade_ops),
            'downgrade_ops': '\n    '.join(downgrade_ops),
        }

        rev = self._chain.add(message, self._config['revision_template_file'], extra_params)
        logger.info("Revison has been created (%s)", rev.id)

        if new_config:
            self.save_config()

        return rev

    def check_loaded(self):
        if self._versions_folder is None:
            raise EvolutionException("Evolution is not loaded yet!")

    @decorate_logger_message("UPGRADE - {original_message}")
    def upgrade(self, revision: str = 'head'):
        logger.info("target revision: '%s'", revision)
        self.check_loaded()

        if len(self._chain) == 0:
            logger.info("The chain is empty, exiting.")
            return

        if not self._config['configpp_urls']:
            logger.error("No configpp urls found. r u ok?")
            return

        logger.info("%s configpp urls has been found", len(self._config['configpp_urls']))

        target_version = self._chain.parse_revision(revision)

        logger.debug("parsed target revision: %s", target_version)

        unordered_configs = {}

        for raw_rev, url in self._config['configpp_urls'].items():
            rev = self._chain.parse_revision(raw_rev)
            unordered_configs[rev] = create_from_url(url)

        configs = OrderedDict() # type: Dict[str, Config]

        for rev in reversed(self._chain.links):
            if rev in unordered_configs:
                configs[rev] = unordered_configs[rev]

        logger.debug("Configpp urls ordered to: %s", configs.keys())

        def get_version_file_path(config: Config):
            if isinstance(config, Group):
                return os.path.join(config.path, '.version')
            else:
                return config.path + '.version'

        def get_version(config: Config):
            version_file = get_version_file_path(config)
            with open(version_file) as f:
                return f.read().strip()

        # try to load all the configs to find the actual config. the last loadable config url will be the actual
        current_config = None # type: Config
        current_version = 'tail'

        for rev, config in configs.items():
            if config.load():
                current_config = config

        if current_config:
            current_version = get_version(current_config)
            # need to search for the current config again
            for rev in self._chain.walk(new_rev = current_version, include_old=True):
                if rev.id in configs:
                    current_config = configs[rev.id]

        logger.debug("Current config: %s", current_config)

        if current_version == target_version:
            logger.info("The current and the target version is the same, exiting.")
            return

        logger.debug("the current version: %s", current_version)

        for rev in self._chain.walk(current_version, target_version, include_old = current_version == 'tail'):

            # if rev.id in configs:


            args = []
            if current_config:
                if isinstance(current_config, Group):
                    args = list(current_config.members.values()) + [current_config]
                else:
                    args = [current_config]


            logger.debug("revid: %s, current_conf: %s, args(%s): %s", rev.id, current_config, len(args), args)

            try:
                new_config = rev.upgrade(*args)
            except Exception as e:
                logger.error(e)
                raise

            logger.debug("new config received %s", new_config)

            if new_config:
                new_config.dump()
                current_config = new_config
            elif current_config:
                current_config.dump()

            current_version_file_path = get_version_file_path(current_config)

            logger.debug("current_version_file_path: %s", current_version_file_path)

            with open(current_version_file_path, 'w') as f:
                f.write(rev.id)
