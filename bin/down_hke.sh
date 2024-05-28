#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

HOME=/devel/diego/TPRD

. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/hke"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da HKE para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da HKE para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

delay

echo "www.hkex.com.hk/eng/stat/dmstat/dayrpt/lmef${ano_2}${mes}${dia}.zip"

baixa_arquivo "www.hkex.com.hk/eng/stat/dmstat/dayrpt/lmef${ano_2}${mes}${dia}.zip" "HKE" "zip"





