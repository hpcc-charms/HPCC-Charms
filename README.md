# HPCC-Charms
Top level HPCC-Charms repository for build and deployment. All the related projects are just prototypes. They are open for re-design and re-implementation. There two groups of charms: 1) Single HPCC Platform which has all supported plugins and module. The initial implementation includes layer-hpccsystems-platform and layer-hpccsystems-plugins 2) HPCC Cluster The initial implementation includes layer-hpccsystems-cluster-node and layer-hpccsystems-cluster-manager. Since both groups involved multiple charms we hope a group of charm bundles will be provided to easy deployment of various HPCC Charm setups. Each deployable charm also should have test using amulet APIs.


# Build
##  Pre-requisites
- Ubuntu 16.04 amd64 Xenial
- Python 3.0
- juju-2.0 
- charm-tools

## Build charms
- git clone https://github.com/hpcc-charms/HPCC-Charms.git
- git submodule update --init
- create a build directory
- cd to HPCC-Charms and run ./build.sh <source dir>. For example ./build.sh layers/layer-hpccsystems-platform . The build output will be in ../build directory

# Deploy
## Local Linux container
### pre-requisite: lxd

### bootstrap
```sh
 juju bootstrap lxd-test localhost
```
### deploy platform charm
```sh
juju models | grep default
[ $? -ne 0 ] && juju add-model default
juju deploy <build dir>/trusty/hpccsystems-platform hpcc --series trusty
juju status
```

### deploy plugin charm
make sure platfrom deployed and ready
```sh
juju deploy <build dir>/trusty/hpccsystems-plugins plugin --series trusty
#juju debug-log
#juju destroy-model default

sleep 3
juju add-relation hpcc plugin
juju status
```

### deploy a roxie cluster
```sh
juju models | grep default
[ $? -ne 0 ] && juju add-model default
juju deploy <build dir>/trusty/hpccsystems-cluster-manager mgr --series trusty
juju status
#juju debug-log
juju deploy <build dir>/trusty/hpccsystems-cluster-node roxie --series trusty
juju status
```
When both are started add relation
```sh
juju add-relation mgr roxie
```


### destroy charms
```sh
juju destroy-model default
```
