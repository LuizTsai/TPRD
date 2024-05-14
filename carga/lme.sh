#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



run_dir="$HOME/run/lme"
bin_dir="$HOME/carga"
. $bin_dir/carga

cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="
		echo "Tratando arquivo $i"
		fl=`file -L $i`
		if [ -n "`echo $fl | grep 'HTML'`" ]; then
			echo "Arquivo $i é HTML"
			carrega_arquivo "lme" "$i" 
		else
			echo "Arquivo $i não é de nenhum formato esperado"
			mail -s "lme.sh: Arquivo $i não é de nenhum formato esperado"  carga <<FIM
	$fl
FIM
				mv $i erro/
		fi
		echo ""
	fi
done
