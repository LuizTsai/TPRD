#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


for i in `ls stlags.last`; do
	echo $i
	l=`ls -l $i | sed "s/.* -> //"`
	echo $l
done

