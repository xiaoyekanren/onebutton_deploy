#!/bin/bash

if [ "$1" == 'confignode' ]; then
    echo "start-confignode.sh"
    nohup ./start-confignode.sh > /dev/null 2>&1 &
    echo $!
elif [ "$1" == 'datanode' ]; then
    echo "start-datanode.sh"
    nohup ./start-datanode.sh > /dev/null 2>&1 &
    echo $!
fi