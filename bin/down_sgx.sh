#!/bin/bash

#
# Copyright 2016 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/sgx"
#data_dir="$HOME/tmp"

echo ""
if [ $# -eq 0 ]; then
        data=`date -d yesterday "+%Y%m%d"`
        echo "Baixando arquivo da SGX para ontem ($data)"
else
        data=$1
        echo "Baixando arquivo da SGX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#mes_a=$(($mes-1))
mes_a=$((`echo $mes | sed -n "s/^0*//p"` - 1))

delay

cd $data_dir
download=`date "+%Y%m%d%H%M"`
baixa "http://infopub.sgx.com/Apps?A=COW_Infopubdtstat_Content&B=DailyDataDownload&F=4837&G=${mes}${dia}FUT.zip" "SGX" "zip" 

ret=$?
if [ $ret -eq 0 ]; then
	fl=`file "tudo/SGX_${data}_${download}.zip" | grep "Zip archive data"`
	if [ -z "$fl" ]; then
		echo "`date`: Arquivo tudo/SGX_${data}_${download}.zip não é ZIP, descartando"
		mailx -s "arquivo SGX para $data inválido (não é ZIP!)"  capta <<FIM
			`file tudo/SGX_${data}_${download}.zip`
		        `head -n 3 tudo/SGX_${data}_${download}.zip`
FIM
		mv "tudo/SGX_${data}_${download}.zip" "tudo/SIGX_${data}_${download}.lixo"
		#        rm "tudo/MCX_${data}_${download}.csv"
		exit 1
	fi
	linka_se_novo "SGX" "zip"
	ret=$?
	exit $ret
fi
