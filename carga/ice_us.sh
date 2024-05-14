#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



run_dir="/home/capta/run/ice_us"
bin_dir="/home/capta/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		echo "Tratando arquivo $i"
		fl=`file -L $i`
		echo $fl
		if [ -n "`echo $fl | grep 'PDF'`" ]; then
			echo "Arquivo $i é PDF"
			carrega_arquivo "ice_us_pdf" "$i" "PDF"
		elif [ -n "`echo $fl | grep 'HTML'`" ]; then
			echo "Arquivo $i é HTML"
			carrega_arquivo "ice_us_html" "$i"	
		else
			echo "Arquivo $i não é de nenhum formato esperado"
			mail -s "ice_us.sh: Arquivo $i não é de nenhum formato esperado"  carga <<FIM
	$fl
FIM
			mv $i erro/
		fi
		echo ""
	fi
done
