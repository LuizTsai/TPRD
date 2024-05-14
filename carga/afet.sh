#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



run_dir="/home/capta/run/afet"
bin_dir="/home/capta/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		echo "Tratando arquivo $i"
		fl=`file -L $i`
		if [ -n "`echo $fl | grep 'HTML'`" ]; then
			echo "Arquivo $i é HTML"
			carrega_arquivo "afet_html" "$i" 
		else
			xls=`echo $i | grep -P "\.[Xx][Ll][Ss]$"`
			if [ -n "$xls" ]; then
				echo "Arquivo $i é XLS"
			carrega_arquivo "afet" "$i" "XLS"	
			else
				echo "Arquivo $i não é de nenhum formato esperado"
				mail -s "afet.sh: Arquivo $i não é de nenhum formato esperado"  carga <<FIM
	$fl
FIM
				mv $i erro/
			fi
		fi
		echo ""
	fi
done
