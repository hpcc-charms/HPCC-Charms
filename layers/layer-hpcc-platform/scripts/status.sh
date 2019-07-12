#!/usr/bin/env bash

component=$(basename $BASH_SOURCE) 
/etc/init.d/hpcc-init status | grep -i $component| grep -ci 'is running'