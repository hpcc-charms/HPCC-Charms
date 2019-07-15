#!/usr/bin/env python3

import os,stat
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
        plugins_install = PluginsInstallation()
        plugins_install.install_all()


        # Install modules: ganglia-monitoring, nagios-monitoring
        # module_install = ModuleInstalltion()
        # for each module in list
        #    if <module-version> definedin config.yaml
        #       module_install.install("<module name>","<module name>", <plugin_version>)

        # Install additonal prerequisites
        basic_install =  InstallationBasic()
        basic_install.additional_prerequisites()

        if self.config['node-type'] == 'dali':
           log(' create ' +   HPCCEnv.CLUSTER_CURRENT_IPS_DIR, INFO)
           if not os.path.exists(HPCCEnv.CLUSTER_CURRENT_IPS_DIR):
              os.makedirs(HPCCEnv.CLUSTER_CURRENT_IPS_DIR)
              os.system("rm " + HPCCEnv.CLUSTER_CURRENT_IPS_DIR + "/*")

           try:
               output = check_output(['chmod', '-R', '777'])
               log(output, INFO)
               return True
           except CalledProcessError as e:
               log(e.output, INFO)
               return False

           #os.chmod(HPCCEnv.CLUSTER_CURRENT_IPS_DIR, stat.S_IWOTH)

class InstallationBasic (object):
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

        self.install_prerequisites(self.name) 
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
        checksum_key = self.name + '-checksum'
        if checksum_key in self.config:
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

    def install_additional_prerequistites(self):
        pass

    def install_prerequisites(self, name):
        charm_dir = hookenv.charm_dir()

        prereq_dir =  charm_dir + '/dependencies/' + platform.linux_distribution()[2]
        with open(os.path.join(prereq_dir, name + '.yaml')) as fp:
            workload = yaml.safe_load(fp)
        packages = workload['packages']
        hookenv.status_set('maintenance', 'Installing prerequisites')

        return batch_install(packages)

    def additional_prerequisites(self):
        if 'additional-packages' in self.config:
           additional_packages = self.config['additional-packages']
           if additional_packages:
              rc = self.install_prerequisites(additional_packages)
              if rc != True:
                 return False

        if 'additional-install' in self.config:
           additional_install = self.config['additional-install']
           if additional_install:
              charm_dir = hookenv.charm_dir()
              cmd =  charm_dir + '/dependencies/' + platform.linux_distribution()[2] + '/' + additional_install
              try:
                 output = check_output([cmd, 'status'])
                 log(output, INFO)
                 return True
              except CalledProcessError as e:
                 log(e.output, INFO)
                 return False

        return True


class PlatformInstallation (InstallationBasic):

    def __init__(self):
        InstallationBasic.__init__(self)

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

    def install_prerequisites(self, name=None):
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


class PluginsInstallation (InstallationBasic):

    def __init__(self):
        InstallationBasic.__init__(self)


    def install_all(self):

        plugins = ['mysqlembed', 'javaembed', 'kafka', 'redis', 'couchbaseembed']
        for plugin in plugins:
           version = plugin + '-version'
           if version in self.config:
              plugin_version = self.config[version]
           else:
              continue
           self.install(plugin, 'plugins', plugin_version)

    def get_package_name(self):
        return "hpccsystems-plugin-" + self.name + "_" +  \
               self.version + package_extension()
