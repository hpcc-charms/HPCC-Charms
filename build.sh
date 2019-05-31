#!/bin/bash


SRC_DIR=$(dirname $0)
cd $SRC_DIR
SRC_DIR=$(pwd)

export JUJU_REPOSITORY=${SRC_DIR}/../build
export CHARM_LAYERS_DIR=$SRC_DIR/layers
export CHARM_INTERFACES_DIR=$SRC_DIR/interfaces

mkdir -p $JUJU_REPOSITORY


charms="layer-hpcc-platform \
        layer-hpcc-cluster-node \
        layer-hpcc-cluster-dali"

[ -d ${JUJU_REPOSITORY}/builds ] && rm -rf  ${JUJU_REPOSITORY}/builds  

for charm in ${charms}
do
   echo ""
   echo "build $charm"
   cd ${CHARM_LAYERS_DIR}/$charm
   #echo "Ubuntu 14.04 amd64 Trusty"
   #charm build -s trusty
   echo "Ubuntu 18.04 amd64 Boinic"
   charm build 
done


