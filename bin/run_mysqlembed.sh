#!/bin/bash

WK_DIR=$(dirname $0)
echo "Source MySQL environment"
source /var/lib/HPCCSystems/charm/mysqlembed.cfg
#cat /var/lib/HPCCSystems/charm/mysqlembed.cfg

#echo "MYSQLDB_USER: $MYSQLDB_USER"
#echo "MYSQLDB_SERVER: $MYSQLDB_HOST"


echo "Compile ${WK_DIR}/my-simple-env.ecl"
eclcc ${WK_DIR}/mysql-simple-env.ecl -o ${WK_DIR}/mysql-simple-env

echo "Run my-simple-env"
${WK_DIR}/mysql-simple-env
