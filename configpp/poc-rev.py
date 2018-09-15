
from configpp.soil import Config, GroupMember, Group


# single, no change
def upgrade1(config: Config):
    config.data['key2'] = config.data['key1']
    del config.data['key1']


# multi, no change
def upgrade2(core: GroupMember, logger: GroupMember):
    core.data['key2'] = core.data['key1']
    del core.data['key1']


# multi, add one new config
def upgrade3(core: GroupMember, logger: GroupMember):
    regdata = GroupMember('regdata.json')

    regdata.data = {'id': 42}

    return (regdata, )


# multi, add one new config
def upgrade3b(core: GroupMember, logger: GroupMember, group: Group):
    regdata = GroupMember('regdata.json')

    regdata.data = {'id': 42}

    group.add_member(regdata)


######### 2



def upgrade4n(group: Group):
    # access group data
    pass
