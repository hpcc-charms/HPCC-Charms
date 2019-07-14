#!/bin/bash

unit=hpcc/0
[ -n "$1" ] && unit=$1

echo "juju scp -- *mysql* ${unit}:/tmp/"
juju scp -- *mysql* ${unit}:/tmp/

echo "juju run --unit ${unit} sudo /tmp/run_mysqlembed.sh"
juju run --unit ${unit} sudo /tmp/run_mysqlembed.sh
