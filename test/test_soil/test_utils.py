
from pytest import raises, mark
from unittest.mock import patch

from configpp.soil import JSONTransform, YamlTransform, Transport, Config, GroupMember

from configpp.soil.utils import create_from_url, SoilUriParserException, Config, Group

def test_very_simple_uri():

    cfg = create_from_url('configpp://app.yaml')

    assert isinstance(cfg, Config)
    assert isinstance(cfg.transform, YamlTransform)
    assert cfg.name == 'app.yaml'

def test_url_with_hypen():

    cfg = create_from_url('configpp://app-teve.yaml')

    assert isinstance(cfg, Config)
    assert isinstance(cfg.transform, YamlTransform)
    assert cfg.name == 'app-teve.yaml'

def test_url_with_underscore():

    cfg = create_from_url('configpp://app_teve.yaml')

    assert isinstance(cfg, Config)
    assert isinstance(cfg.transform, YamlTransform)
    assert cfg.name == 'app_teve.yaml'

def test_very_simple_group_uri():

    grp = create_from_url('configpp://core.yaml&logger.json@app1')

    members = list(grp.members.values())

    assert isinstance(grp, Group)
    assert len(grp.members) == 2
    assert isinstance(members[0].transform, YamlTransform)
    assert isinstance(members[1].transform, JSONTransform)
    assert members[0].name == 'core.yaml'
    assert members[1].name == 'logger.json'
    assert grp.name == 'app1'


def test_single_uri_with_custom_transform():

    class FakeModule():
        @staticmethod
        def SpiderManTransform():
            return 42

    with patch('configpp.soil.utils.import_module', return_value = FakeModule):
        cfg = create_from_url('configpp://app.yaml%dummy:SpiderManTransform')
        assert isinstance(cfg, Config)
        assert cfg.transform == 42

def test_single_uri_with_custom_transport():

    class FakeModule():
        @staticmethod
        def JasonStathamTransport():
            return 42

    with patch('configpp.soil.utils.import_module', return_value = FakeModule):
        cfg = create_from_url('configpp://app.yaml/dummy:JasonStathamTransport')
        assert isinstance(cfg, Config)
        assert cfg._transport == 42

def test_single_uri_with_bad_custom_transform():

    with raises(SoilUriParserException):
        create_from_url('configpp://app.yaml%dummy')

def test_single_bad_uri():

    with raises(SoilUriParserException):
        create_from_url('app.yaml')

def test_single_uri_with_location():

    cfg = create_from_url('configpp://app.yaml#/etc/app.yaml')
    assert isinstance(cfg, Config)

def test_group_with_optional_member():

    grp = create_from_url('configpp://core.yaml&logger.json?@app1')

    assert isinstance(grp, Group)

    members = list(grp.members.values())

    assert len(grp.members) == 2
    assert isinstance(members[0].transform, YamlTransform)
    assert isinstance(members[1].transform, JSONTransform)
    assert members[0].name == 'core.yaml'
    assert members[1].name == 'logger.json'
    assert grp.name == 'app1'
    assert members[0].mandatory is True
    assert members[1].mandatory is False

@mark.parametrize('filename, transform', [
    ('appname', JSONTransform),
    ('appname.json', JSONTransform),
    ('appname.yaml', YamlTransform),
    ('appname.yml', YamlTransform),
])
def test_guessing_in_ctors(filename, transform):

    assert isinstance(Config(filename).transform, transform)
    assert isinstance(GroupMember(filename).transform, transform)
