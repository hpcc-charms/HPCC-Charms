#!/usr/bin/env python3

import os
import platform
import yaml
import re
# python 2.7
#import ConfigParser
# python 3
#import Configparser
from subprocess import check_call,check_output,CalledProcessError
 
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv

from charmhelpers.fetch.archiveurl import (
    ArchiveUrlFetchHandler
)

   
class HPCCEnv:
   JUJU_HPCC_DIR    = '/var/lib/HPCCSystems/charm'
   CONFIG_DIR       = '/etc/HPCCSystems'
   ENV_XML_FILE     = 'environment.xml'
   ENV_CONF_FILE    = 'environment.conf'
   ENV_RULES_FILE   = 'genenvrules.conf'
   HPCC_HOME        = '/opt/HPCCSystems'
   HPCC_CLUSTER_DIR = JUJU_HPCC_DIR + '/cluster'
   CLUSTER_IPS_DIR  = HPCC_CLUSTER_DIR +  '/ips'
   CLUSTER_CURRENT_IPS_DIR  = HPCC_CLUSTER_DIR +  '/current_ips'

   CLUSTER_NODE_TYPES = ['dali',
                         'sasha', 
                         'dfuserver',
                         'eclagent',
                         'eclccserver',
                         'eclscheduler',
                         'esp',
                         'roxie',
                         'thormaster',
                         'thorslave',
                         'support']

   PLATFORM_COMPONENTS = ['dali',
                         'sasha', 
                         'dfuserver',
                         'eclagent',
                         'eclccserver',
                         'eclscheduler',
                         'esp',
                         'roxie',
                         'thor',
                         'dafilesrv']
