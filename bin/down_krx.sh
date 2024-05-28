#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/krx"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da KRX para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da KRX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir


delay
prefix="KRX"
baixa "http://eng.krx.co.kr/por_eng/servlets/FileDownload?type=mktcond_file&noti_no=${ano}${mes}${dia}&seq=2&ld_mkt_tp_cd=3" "$prefix" "pdf"
ret=$?

if [ $ret -eq 0 ]; then
	fl=`file "tudo/${prefix}_${data}_${download}.pdf" | grep "PDF"`
	if [ -z "$fl" ]; then
		echo "`date`: Arquivo tudo/${prefix}_${data}_${download}.pdf não é PDF, descartando"
		mailx -s "arquivo ${prefix} para $data inválido (não é PDF)" capta <<FIM
	        `ls -l "tudo/${prefix}_${data}_${download}.pdf"`
        	`file "tudo/${prefix}_${data}_${download}.pdf"`
	        `head -n 3 "tudo/${prefix}_${data}_${download}.pdf"`
FIM
		mv tudo/${prefix}_${data}_${download}.pdf /tmp/
	else
		linka_se_novo "${prefix}" "pdf"
		ret=$?
		exit $ret
	fi
else
	echo "Problemas no Download"
	exit $ret
fi





