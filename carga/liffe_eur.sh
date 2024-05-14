#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



bin_dir="/home/capta/carga"
. $bin_dir/carga

run_dir="/home/capta/run/liffe_eur_london"
cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		carrega_arquivo "liffe_eur_london" "$i"	
		echo ""
	fi
done

run_dir="/home/capta/run/liffe_eur_paris"
cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		carrega_arquivo "liffe_eur_paris" "$i"	
		echo ""
	fi
done
