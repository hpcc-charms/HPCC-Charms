# HPCC-Charms
Top level HPCC-Charms repository for build and deployment. All the related projects are just prototypes. They are open for re-design and re-implementation. There two groups of charms: 1) Single HPCC Platform which has all supported plugins and module. The initial implementation includes layer-hpccsystems-platform and layer-hpccsystems-plugins 2) HPCC Cluster The initial implementation includes layer-hpccsystems-cluster-node and layer-hpccsystems-cluster-manager. Since both groups involved multiple charms we hope a group of charm bundles will be provided to easy deployment of various HPCC Charm setups. Each deployable charm also should have test using amulet APIs.


# Build
##  Pre-requisites
- Ubuntu 18.04 amd64 Xenial
- Python 3.0
- juju-2.5" sudo snap install juju 
- lxd : sudo snap install lxd
- charm-tools: sudo snap install charm

## Build charms
- git clone https://github.com/hpcc-charms/HPCC-Charms.git
- git submodule update --init
- create a build directory
- cd to HPCC-Charms and run ./build.sh. The build output will be in ../build directory

# Deploy
## Local Linux container
### pre-requisite: lxd
#lxd init --auto (probably already done)
#lxd init --auto --storage-backend zfs (probably already done)
lxc network set lxdbr0 ipv6.address none

#Check network: lxc network get lxdbr0 ipv4.address
#Sample output: 10.172.37.1/24

### bootstrap
# need this after system reboot
```sh
 lxc network get lxdbr0 ipv4.address
 juju bootstrap localhost lxd-test
```
### deploy platform charm
```sh
juju models | grep default
[ $? -ne 0 ] && juju add-model default
juju deploy <build dir>/builds/hpccsystems-platform hpcc --series bionic
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

### Debug
```sh
juju debug-log
```


### destroy charms
```sh
juju destroy-model default
```


##Troubleshooting
### Can't kill controller
juju kill-controllers <controller name>
ERROR getting controller environ: unable to get bootstrap information from client store or API
Solution: juju unregister -y <controller name>
