# Charm Bundles:

Charm bundles can be used to integrate multiple charm layer together.
This folder contains a few example configurations to deploy hpcc.

Bundles are specified using a yaml file. The support a variety of configuration options. 
Some of the interesting ones are

- num_units : used to specify the number of units to be deployed for a particular layer.

- series : The underlying ubuntu distro series to be used. Valid options are xenial, bionic and trusty.

- constraints : this options is used to specify the constrains for a particular application/ machine. Through this one can define the amount of memory/ storage attached, the number of cpu's assigned etc. 

- expose : All nodes are by default exposed only on the private network. This is used to expose the node to the public network.


For more details please see the charm [bundle documentation](https://jaas.ai/docs/charm-bundles).

