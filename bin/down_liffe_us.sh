#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/liffe/us"


echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da LIFFE-US para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da LIFFE-US para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

delay
#http_proxy=""

prefix="LIFFE-US"
#baixa_arquivo "http://www.liffe.com/nyseliffe/cfut${ano}${mes}${dia}.pdf" "LIFFE-US" "pdf"
ret=171
while [ $ret -eq 171 ]; do
	baixa "http://www.liffe.com/nyseliffe/cfut${ano}${mes}${dia}.txt" $prefix "txt"
	ret=$?
	if [ $ret -eq 0 ]; then
		erro=`grep "The online users' count exceeds the license's permission. You need to purchase or upgrade your license." "tudo/${prefix}_${ano}${mes}${dia}_${download}.txt"`
		if [ -n "$erro" ]; then
			echo "Arquivo é mensagem de excesso de usuários no proxy"
			rm "tudo/${prefix}_${ano}${mes}${dia}_${download}.txt"
			ret=171
		else
			linka_se_novo $prefix "txt"
		fi
	fi
done
exit

baixa "http://www.liffe.com/nyseliffe/cfut${ano}${mes}${dia}.pdf" $prefix "pdf"
ret=$?
if [ $ret -eq 0 ]; then
	if [ -f "tudo/${prefix}_${ano}${mes}${dia}_${download}.pdf" -a -s "tudo/${prefix}_${ano}${mes}${dia}_${download}.pdf" ]; then
		pdftotext -layout "tudo/${prefix}_${ano}${mes}${dia}_${download}.pdf"
		ret=$?
		if [ $ret -ne 0 ]; then
			echo "PROBLEMAS com pdftotext (ret=$ret)"
			exit 1
		fi
		rm "tudo/${prefix}_${ano}${mes}${dia}_${download}.pdf"
		linka_se_novo $prefix "txt"
		ret=$?
		if [ $ret -eq 1 ]; then
			echo "PROBLEMAS com o arquivo baixado"
		fi
	else
		echo "`date`: arquivo obtido está zerado, removendo"
		rm "tudo/${prefix}_${ano}${mes}${dia}_${download}.pdf"
	fi
fi




