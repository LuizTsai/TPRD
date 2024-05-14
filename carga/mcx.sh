#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



run_dir="/home/capta/run/mcx"
bin_dir="/home/capta/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		carrega_arquivo "mcx" "$i"	
		echo ""
	fi
done
