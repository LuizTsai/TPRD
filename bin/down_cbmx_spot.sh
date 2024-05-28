#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/cbmx"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da CBMX para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da CBMX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
mes_a=`date -d $data +%b`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir


obtem_base_price_link () {
	baixa "$1/article/bp/" "bp" "html" 
	ret_b=$?
	if [ $ret_b -ne 0 ]; then
		echo "`date`: wget retornou problemas ($ret_b) ao procurar link dos Base Prices" 1>&2
		rm "tudo/bp_${data}_${download}.html"
		echo ""
	else
		mv "tudo/bp_${data}_${download}.html" "tudo/bp_${data}.html"
		link=`cat tudo/bp_${data}.html | grep "<a title=\"Base Prices of China Iron Ore Spot Trading Platform\"" | sed -n "s/.*href=\"\([^\"]*\)\".*/\1/p"`
		echo "$link"
	fi
}


obtem_spot_link () {
	baixa "$1/article/chinairon/" "spot" "html"
	ret_b=$?
	if [ $ret_b -ne 0 ]; then
		echo "`date`: wget retornou problemas ($ret_b) ao procurar link do Spot Trading Data" 1>&2
		rm "tudo/spot_${data}_${download}.html"
		echo ""
	else
		echo "Procurando link para o dia $data em tudo/spot_${data}.html" 1>&2
		mv "tudo/spot_${data}_${download}.html" "tudo/spot_${data}.html"
		echo "cat tudo/spot_${data}.html | grep \"<a title=\"China Iron Ore Spot Trading Data(${mes_a} ${dia}, ${ano})\"\" | sed -n \"s/.*href=\"\([^\"]*\)\".*/\1/p\"" 1>&2
		link=`cat tudo/spot_${data}.html | grep -P "<a title=\"China Iron Ore Spot Trading Data\(${mes_a} ${dia},? ${ano}\)\"" | sed -n "s/.*href=\"\([^\"]*\)\".*/\1/p"`
		echo "$link"
		echo "$link" 1>&2
	fi
}





#delay


#l=`obtem_base_price_link "http://en.cbmx.com.cn"`

#if [ -n "$l" ]; then
#	echo "`date`: Baixando arquivo de Base Prices"
#	baixa "http://en.cbmx.com.cn/$l" "CBMX_Base_Price" "html"
#else
#	echo "`date`: ERRO: não foi possível obter link dos Base Prices"
#fi 

l=`obtem_spot_link "http://en.cbmx.com.cn"`
if [ -n "$l" ]; then
	echo "`date`: Baixando arquivo de Spot Trading Data ($l)"
	baixa_arquivo "http://en.cbmx.com.cn/$l" "CBMX_Spot_Trading" "html"
else
	echo "`date`: ERRO: não foi possível obter link dos Spot Trading Data"
fi 


