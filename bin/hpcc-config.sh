#!/bin/bash

dali_app_name=dali
[ -n "$1" ] && dali_app_name=$1
juju config ${dali_app_name} update-envxml=$(echo $(($(date +%s%N)/1000000)))
