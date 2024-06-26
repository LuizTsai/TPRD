#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



run_dir="/home/capta/run/safex"
bin_dir="/home/capta/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		xls=`echo $i | grep -P "\.[Xx][Ll][Ss]$"`
		if [ -z "$xls" ]; then
			carrega_arquivo "safex" "$i"	
		else
			carrega_arquivo "safex" "$i" "XLS"
		fi
		echo ""
	fi
done
