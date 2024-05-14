#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

home=/devel/diego/TPRD

run_dir="/devel/diego/TPRD/run/cme_agro"
bin_dir="${home}/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		/devel/diego/TPRD/carga/cme_agro.py "$i"	
		echo ""
	fi
done
