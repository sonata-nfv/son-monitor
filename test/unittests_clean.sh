#!/bin/bash

echo "Deleting unittests containers"
cnts=$(docker ps --all -q -f network=son-mon-unittests)
if [ "$cnts" != '' ] 
then
   docker rm -fv $cnts
fi

