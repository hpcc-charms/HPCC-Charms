# Overview

[HPCC Systems,](http://HPCCSystems.com) an open source High Performance Computing Cluster, is a massive parallel-processing computing platform that solves Big Data problems. HPCC Systems is an enterprise-proven platform for manipulating, transforming, querying, and data warehousing Big Data. Built by LexisNexis, the HPCC platform has helped it grow to a $1.5 billion information solutions company.

The HPCC Systems architecture incorporates a data query engine (called Thor) and a data delivery engine (called Roxie), as well as common middleware support components, an external communications layer, client interfaces which provide both end-user services and system management tools, and auxiliary components to support monitoring and to facilitate loading and storing of file system data from external sources.

An HPCC environment can include only Thor clusters, or both Thor and Roxie clusters. The HPCC Juju charm creates a cluster which contains both, but you can customize it after deployment.

See [How it Works](http://www.hpccsystems.com/Why-HPCC/How-it-works)  for more details.

See [System Requirements](http://hpccsystems.com/download/docs/system-requirements) for hardware details.
> Please note, your Juju instance must have at least 4GB of RAM. To increase the memory for a unit, run this command:
   `juju set-constraints mem=4G`

The HPCC Juju Charm encapsulates best practice configurations for the HPCC  Systems Platform.  You can use a Juju Charm to stand up an HPCC Platform on:

- Local Provider (LXC)

- Amazon Web Services Cloud


# Usage

## General Usage

1. To deploy a single HPCC node:

    `juju deploy hpcc <name>`

    **For example:**

        'juju deploy hpcc myhpcc`

1. To check the status , run
        juju status

        You also can log into the node to check if HPCC is properly installed.

        `juju ssh myhpcc/0`

ECLWatch ip is the public ip of "master name"


1. You can expose the HPCC cluster by running:

       `juju expose <master_name>`

Once the service is deployed, running, and exposed, you can find the address for the ECL Watch Web interface by running juju status and looking for the public-address field. Type that address plus :8010 for the port.

For example, **nnn.nnn.nnn.nnn:8010**.


###To update from prior version

You can set the **hpcc-version** in the configuration file (config.yaml) or in the Juju canvas configuration settings.

Alternately, you can set these using this command:
    juju set <hpcc service name> hpcc-version=<new version> package-checksum=<checksum string>

### Verifying the checksum
The charm uses an md5sum to verify the checksum of the HPCC platform  package before installing.

For this version of the charm, it is set to check the md5sum for the Community Edition Version 5.4.2-1 for Ubuntu 14.04 amd64. To verify a different version, edition, or OS version, change the value of the md5sum in the package-checksum variable in config.yaml. You can get other package checksums from [http://hpccsystems.com/download](http://hpccsystems.com/download)

### Ports

The charm automatically opens for external access, the following ports:

- Port **8010** for ECLWatch access
- Port **8002** for WsECL access.
- Port **9876** for direct Roxie access
- Port **8015** for Configuration Manager access.

### Next Steps ###

After deploying and adding nodes, you can tweak various options to optimize your HPCC deployment to meet your needs.

See [HPCC Systems Web site](http://HPCCSystems.com) for more details.


# Implementation #
This charm inherit layer-hpccystems-platform-base charm. This is desgined to use as a single node HPCCSystems Platform with all supported HPCCSystems plugins and modules.

- plugin : an interface provided by interface-hpccsystems-plugin
- modules: an interface provided by interface-hpccsystems-moduel

![alt Hierarchy Diagram] (images/layer-hpccsystems-platform.jpg)


# HPCC Systems Contact Information

[HPCC Systems Web site](http://HPCCSystems.com)

For support, visit the HPCC Community Forums:
[HPCC Community Forums](http://hpccsystems.com/bb/index.php?sid=0bda2dddb2ea50418357171d33b11e5f)
