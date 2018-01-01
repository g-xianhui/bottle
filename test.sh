#!/bin/sh

i=0
while [ $i -lt 10 ];
do
	echo "tick $i"
	sleep 1
	i=$((i+1))
done
