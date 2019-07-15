#!/usr/bin/python3

import os
import random
from shutil import rmtree
import string
import subprocess
import sys

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charms.layer.hpccenv import HPCCEnv
from charms.layer.hpcc_init import HPCCInit
from charms.layer.hpcc_config import HPCCConfig

from charmhelpers.core import (
    hookenv,
    host,
)

from charms.layer.hpcc_config import HPCCConfig
from charms.layer.hpccenv import HPCCEnv

@hooks.hook("hpcc-config")
def create_envxml():
    hookenv.action_set("In action: create_envxml" )
    hpcc_config = HPCCConfig()
    hookenv.action_set("Create object HPCCConfig" )
    configs = hookenv.config()
    hookenv.action_set("get config object" )
    hookenv.action_set("call create_envxml through hpcc_config" )
    rc = hpcc_config.create_envxml(configs, HPCCEnv.CLUSTER_CURRENT_IPS_DIR,
        CONFIG_DIR + ENV_XML_FILE)
    if rc:
       hookenv.action_set("Generate environment.xml successfully." )
    else:
       hookenv.action_fail("Generate environment.xml failed.")


if __name__ == "__main__":
    hookenv.action_set("action main:" )
    hooks.execute(sys.argv)
