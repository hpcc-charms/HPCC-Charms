#!/bin/bash


SRC_DIR=$(dirname $0)
cd $SRC_DIR
SRC_DIR=$(pwd)

export JUJU_REPOSITORY=${SRC_DIR}/../build
export LAYER_PATH=$SRC_DIR/layers
export INTERFACE_PATH=$SRC_DIR/interfaces

mkdir -p $JUJU_REPOSITORY


charms="layer-hpccsystems-platform \
        layer-hpccsystems-plugins \
        layer-hpccsystems-cluster-node \
        layer-hpccsystems-cluster-manager"

for charm in ${charms}
do
   echo ""
   echo "build $charm"
   cd ${LAYER_PATH}/$charm
   echo "Ubuntu 14.04 amd64 Trusty"
   charm build -s trusty
   echo "Ubuntu 16.04 amd64 Xenial"
   charm build -s xenial
done


