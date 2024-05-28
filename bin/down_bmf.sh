#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

HOME=/devel/diego/TPRD

. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/bmf"

echo ""
if [ $# -eq 0 ]; then
        data=`date -d yesterday "+%Y%m%d"`
        echo "`date`: Baixando arquivos da BMF para ontem ($data)"
else
        data=$1
        echo "`date`: Baixando arquivos da BMF para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

#delay
http_proxy=""
run_dir="$HOME/capta/run/bmf"
#baixa_arquivo "ftp://ftp.bmf.com.br/ContratosPregaoFinal/BF${ano_2}${mes}${dia}.ex_" "BMF_ContratosPregaoFinal" "zip"
#baixa_arquivo "http://bvmf.bmfbovespa.com.br/download/BOLETINSDIARIOS/bd_07_${ano}${mes}${dia}.pdf" "bd_${ano}${mes}${dia}.pdf" "pdf"
baixa_arquivo "https://up2dataweb.blob.core.windows.net/bdi/BDI_00_${ano}${mes}${dia}.pdf" "bd_${ano}${mes}${dia}.pdf" "pdf"

# https://up2dataweb.blob.core.windows.net/bdi/BDI_00_20230915.pdf -> novo


