#!/bin/bash
dali_app_name=dali
[ -n "$2" ] && dali_app_name=$1


get_status()
{
    juju scp -- ${dali_app_name}/0:/var/lib/HPCCSystems/charm/cluster/current_ips/units_and_ips /tmp/
    echo "${dali_app_name}/0"
    juju run --unit ${dali_app_name}/0 sudo /etc/init.d/hpcc-init status
    echo ""

    cat /tmp/units_and_ips | while read type unit ip
    do
       echo $unit
       juju run --unit ${unit} sudo /etc/init.d/hpcc-init status
       echo ""
    done
}

case "$1" in
  start)
    echo "start cluster"
    juju config ${dali_app_name} start-cluster=$(echo $(($(date +%s%N)/1000000)))
       ;;
  stop)
    echo "Stop cluster"
    juju config ${dali_app_name} stop-cluster=$(echo $(($(date +%s%N)/1000000)))

      ;;
  status)
    echo "Get status of cluster ..."
    get_status
      ;;
  *)
    echo ""
    echo "Missing or unknown action. Type one of start, stop or status"
    echo ""
    exit 1

esac
