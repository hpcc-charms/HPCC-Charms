# HPCC-Charms
Top level HPCC-Charms repository for build and deployment

# Build
##  Pre-requisites
- Ubuntu 16.04 amd64 Xenial
- Python 3.0
- juju-2.0 
- charm-tools

## Build charms
To build all charms: run ./build.sh. The build output will be in ../build directory

# Deploy
## Local Linux container
1. pre-requisite:
- lxd

1. bootstrap
```sh
 juju bootstrap lxd-test localhost
```
1. deploy platform charm
```sh
juju models | grep default
[ $? -ne 0 ] && juju add-model default
juju deploy <build dir>/trusty/hpccsystems-platform hpcc --series trusty
juju status
```

1. deploy plugin charm
make sure platfrom deployed and ready
```sh
juju deploy <build dir>/trusty/hpccsystems-plugins plugin --series trusty
#juju debug-log
#juju destroy-model default

sleep 3
juju add-relation hpcc plugin
juju status
```

1. deploy a roxie cluster
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


1. destroy charms
```sh
juju destroy-model default
```
