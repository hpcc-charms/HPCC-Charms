#!/usr/bin/env python3

import os
import platform
import yaml
import re
#import Configparser
from subprocess import check_call,check_output,CalledProcessError

from charmhelpers import fetch
#from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG


from charms.reactive.helpers import is_state
from charms.reactive.bus import set_state
from charms.reactive.bus import get_state
from charms.reactive.bus import remove_state
from charms.reactive import hook, when, when_not

from charms.layer.hpcc_install import HPCCInstallation
from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig
from charms.layer.utils import SSHKey
from charms.layer.hpccenv import HPCCEnv

@when('mysql-db.available')
@when_not('mysql-db.configured')
def setup_mysqldb(mysql):

    if not os.path.exists(HPCCEnv.JUJU_HPCC_DIR):
              os.makedirs(HPCCEnv.JUJU_HPCC_DIR)
    mysql_cfg_file = HPCCEnv.JUJU_HPCC_DIR + '/mysqlembed.cfg'
    f = open(mysql_cfg_file, 'w')
    f.write('export MYSQLDB_HOST=' + mysql.host() + '\n')
    f.write('export MYSQLDB_DATABASE=' + mysql.database() + '\n')
    f.write('export MYSQLDB_USER=' + mysql.user() + '\n')
    f.write('export MYSQLDB_PASSWORD=' + mysql.password() + '\n')
    f.close()
    set_state('mysql-db.configured')
