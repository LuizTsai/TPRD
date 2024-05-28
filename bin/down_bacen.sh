#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download


echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da BACEN para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da BACEN para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
mes_a=`date -d $data +%b`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

delay
data_dir="$HOME/data/bacen"
run_dir="/home/capta/run/bacen"
cd $data_dir

baixa_arquivo "www4.bcb.gov.br/Download/fechamento/${ano}${mes}${dia}.csv" "BACEN" "csv"
