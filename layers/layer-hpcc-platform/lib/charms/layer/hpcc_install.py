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
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG
#from charmhelpers.core import templating

import charms.layer.hpccenv
from charms.layer.hpccenv import HPCCEnv

from charms.layer.utils import (
   package_extension, package_install_local_cmd,
   package_install_repo_cmd, package_uninstall_cmd,
   batch_install
)

from charmhelpers.fetch.archiveurl import (
    ArchiveUrlFetchHandler
)

#import charm.apt
   
class HPCCInstallation (object):

    def __init__(self):
        super().__init__()
        self.config = hookenv.config()

    def install(self):
        platform_version = self.config['platform-version']
        if not platform_version:        
           return 1
        platform_install = PlatformInstallation()
        platform_install.install("platform", "platform", platform_version)
        
        # Install plugins

        # Install modules


class InstallationBase (object):
    def __init__(self):

        super().__init__()
        self.config = hookenv.config()
        self.name = ""
        self.version = ""
        self.package_type = ""

    def install(self, name, package_type, version):
        self.name = name
        self.version = version
        self.package_type = package_type

        self.install_prerequisites() 
        self.install_package()
        
        #self.nodes = {}

    def get_package_name(self):
        pass

    def get_package_url(self):
        version_mmp = self.version.split('-',1)[0]
        return self.config['base-url'] + "/" + self.config['platform-type'] + "-Candidate-" + \
            version_mmp + "/bin/" + self.package_type + "/" +  self.get_package_name()

    def install_package(self):
        package_file = self.download()
        install_cmd = package_install_local_cmd() + " "  + package_file
        hookenv.status_set('maintenance', 'Installing ' + self.name)
        check_call(install_cmd.split(), shell=False)
        hookenv.status_set('active', self.name + ' installed')

    def download(self):
        hookenv.status_set('maintenance', 'Downloading ' + self.name)
        url = self.get_package_url()
        package = self.get_package_name()
        log("Package url: " + url, INFO)
        aufh =  ArchiveUrlFetchHandler()
        dest_file = "/tmp/" + package
        aufh.download(url, dest_file)
        fetch.apt_update()
        checksum = self.config[self.name + '-checksum']
        if checksum:
            hash_type = self.config['hash-type']
            if not hash_type:
                hash_type = 'md5'
            host.check_hash(dest_file, checksum, hash_type)
        return dest_file

    def get_installed_package_name(self):
        pass

    def uninstall(self):
        hookenv.status_set('maintenance', 'Uninstalling ' + self.name)
        uninstall_cmd = package_uninstall_cmd() + " " + self.get_installed_package_name() 
        check_call(dpkg_uninstall_platform_deb.split(), shell=False)

    def install_prerequisites(self):
        charm_dir = hookenv.charm_dir()

        prereq_dir =  charm_dir + '/dependencies/' + platform.linux_distribution()[2] 
        with open(os.path.join(prereq_dir, self.name + '.yaml')) as fp:
            workload = yaml.safe_load(fp)
        packages = workload['packages']
        hookenv.status_set('maintenance', 'Installing prerequisites')

        batch_install(packages)


class PlatformInstallation (InstallationBase):

    def __init__(self):
        InstallationBase.__init__(self)

        
    def get_package_name(self):
        hpcc_type = self.config['platform-type']
        full_hpcc_type = {"CE":"community", "EE":"enterprise", "LN":"internal"}
        return "hpccsystems-platform-" + full_hpcc_type[hpcc_type] + "_" +  \
               self.version + package_extension()


    def get_installed_package_name(self):
        return 'hpccsystems-' + self.name


    #def installed_platform(self):
    #    p = re.compile(r".*hpccsystems-platform[\s]+([^\s]+)\s+([^\s]+)[\s]+hpccsystems-platform-([^\s]+)\\.*", re.M)
    #    try:
    #        hpcc_type = {"community":"CE", "enterprise":"EE", "internal":"LN"}
    #        output = check_output(['dpkg-query', '-l', 'hpccsystems-platform'])
    #        m = p.match(str(output))
    #        if m:
    #            return [m.group(1),hpcc_type[m.group(3)],m.group(3),m.group(2)]
    #        else:
    #
    #           return ['','','','']
    #    except CalledProcessError:
    #         return ['','','','']

    def install_prerequisites(self):
        hookenv.status_set('maintenance', 'Installing prerequisites')
        charm_dir = hookenv.charm_dir()

        prereq_dir =  charm_dir + '/dependencies/' + platform.linux_distribution()[2] 
        with open(os.path.join(prereq_dir,'community.yaml')) as fp:
            workload = yaml.safe_load(fp)
        packages = workload['packages']
        addition_file = ""
        hpcc_type = self.config['platform-type']
        if hpcc_type == "EE":
            addition_file = os.path.join(prereq_dir, "enterprise.yaml")
        elif hpcc_type == "LN":
            addition_file = os.path.join(prereq_dir, "internal.yaml")
        if addition_file:
            with open(addition_file) as fp:
                workload = yaml.safe_load(fp)
            packages.extend(workload['packages'])
        return batch_install(packages)
