#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/ncdex"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da NCDEX para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da NCDEX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
mes_a=`date -d $data +%b`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

delay
run_dir="/home/capta/run/ncdex"

baixa "https://www.ncdex.com/MarketData/BhavCopy.aspx" "lixo/lixo" "html" "--save-cookies /tmp/cookies-ncdex --keep-session-cookies" 
ret=$?
if [ $ret -eq 0 ]; then
	viewState=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__VIEWSTATE\"" | head -n 1 | sed -n "s/^.*name=\"__VIEWSTATE\" id=\"__VIEWSTATE\" value=\"\([^\"]*\)\".*/\1/p"`
        viewState=`echo -n $viewState | percent_encode`
	eventValidation=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__EVENTVALIDATION\"" | head -n 1 | sed -n "s/^.*name=\"__EVENTVALIDATION\" id=\"__EVENTVALIDATION\" value=\"\([^\"]*\)\".*/\1/p"`
	eventValidation=`echo -n $eventValidation | percent_encode `
	echo -n "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=${viewState}&__EVENTVALIDATION=${eventValidation}&ctl00%24ContentPlaceHolder3%24dtBhavCopy%24dtBhavCopy=${dia}%2F${mes}%2F${ano}&ctl00%24ContentPlaceHolder3%24btnExportCSV=cvs%2B+Format&" > tudo/post_data.txt

	baixa "https://www.ncdex.com/MarketData/BhavCopy.aspx" "NCDEX" "csv" "--load-cookies /tmp/cookies-ncdex --referer=\"http://www.ncdex.com/MarketData/BhavCopy.aspx\" --no-cache --header=DNT:1 --header=Upgrade-Insecure-Requests:1 --post-file=tudo/post_data.txt"
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "PROBLEMAS no download"
		return 1
	else
		fl=`file "tudo/NCDEX_${data}_${download}.csv" | grep "HTML document"`
		if [ -n "$fl" ]; then
			echo "`date`: Arquivo tudo/NCDEX_${data}_${download}.csv é HTML, descartando"
			rm "tudo/NCDEX_${data}_${download}.csv"
			exit 1
		fi
		fl=`grep "\"Symbol\",\"Expiry *Date *\",\"Commodity\"" "tudo/NCDEX_${data}_${download}.csv"`
		if [ -z "$fl" ]; then
			echo "PROBLEMAS: Linha de cabeçalho não encontrada no arquivo baixado, possível mudança de layout!"
			mailx -s "down_ncdex: arquivo NCDEX para $data inválido"  capta <<FIM
			Linha de cabeçalho não encontrada em `echo tudo/NCDEX_${data}_${download}.csv`

			`head -n 3 tudo/NCDEX_${data}_${download}.csv`
FIM
			exit 2
		fi
		linka_se_novo "NCDEX" "csv"
		ret=$?
		if [ $ret -ne 0 ]; then
			exit $ret
		fi
	fi
else
	echo "PROBLEMAS no download do session cookie"
	return 2
fi

