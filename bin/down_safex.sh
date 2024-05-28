#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/safex"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da SAFEX para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da SAFEX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir


delay

prefix="SAFEX_Agro"
run_dir="/home/capta/run/safex"

#baixa_arquivo "www.jse.co.za/DownloadableDocuments/Safex/amdmtm/NEW%20DAYAGR.xls" "SAFEX_Diario" "xls"
#baixa "www.jse.co.za/DownloadableDocuments/Safex/agriculture.stats/${ano}/AMDFULL${mes}${dia}.xls" $prefix "xls"
baixa_arquivo "https://www.jse.co.za/_layouts/15/DownloadHandler.ashx?FileName=/Safex/agriculture.stats/${ano}/AMDFULL${mes}${dia}.xls" $prefix "xls"

#ret=$?
#if [ $ret -eq 0 ]; then
#	if [ -f "tudo/${prefix}_${ano}${mes}${dia}_${download}.xls" -a -s "tudo/${prefix}_${ano}${mes}${dia}_${download}.xls" ]; then
#		/usr/local/bin/xls2csv -q3 -d"utf-8" -f"%F" "tudo/${prefix}_${ano}${mes}${dia}_${download}.xls" > "tudo/${prefix}_${ano}${mes}${dia}_${download}.csv" 2>/tmp/safex_xls2csv.err
#		ret=$?
#		if [ $ret -ne 0 -o ! -s "tudo/${prefix}_${ano}${mes}${dia}_${download}.csv" ]; then
#			echo "PROBLEMAS ao converter de XLS para CVS"
#			mailx -s "down_safex: SAFEX: PROBLEMAS ao converter de XLS para CVS" capta <<FIM
#	Arquivo: tudo/${prefix}_${ano}${mes}${dia}_${download}.xls
#	xls2csv retornou $ret
#`ls -lh "tudo/${prefix}_${ano}${mes}${dia}_${download}.csv"`
#
#	stderr do xls2csv:
#`cat /tmp/safex_xls2csv.err`
#
#	stdout do xls2csv:
#`cat tudo/${prefix}_${ano}${mes}${dia}_${download}.csv`
#FIM
#			mv "tudo/${prefix}_${ano}${mes}${dia}_${download}.xls" tudo/lixo/
#			exit 1
#		else
#			linka_se_novo $prefix "csv"
#			ret=$?
#			if [ $ret -eq 1 ]; then
#				echo "PROBLEMAS com o arquivo baixado"
#			fi
#		fi
#	else
#		echo "`date`: arquivo obtido está zerado, removendo"
#		rm "tudo/${prefix}_${ano}${mes}${dia}_${download}.xls"
#	fi		
#fi



