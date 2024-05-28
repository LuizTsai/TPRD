#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/asx"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da ASX para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da ASX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`


function obtem_data() {
	d=`cat $1 | grep "<title>SFE End of Day Data - Futures Total Traded<br> at close of trade date "| tail -n 1 | sed "s/.*trade date \(.*\)<\/title>.*/\1/"`
	di=`echo $d | sed "s/^\([0-9]*\)\/.*/\1/"`
	me=`echo $d | sed "s/^[0-9]*\/\([0-9]*\)\/.*/\1/"`
	an=`echo $d | sed "s/^[0-9]*\/[0-9]*\/\([0-9]*\)/20\1/"`
	echo ${an}${me}${di}
}


#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir
run_dir="/home/capta/run/asx"

delay

prefix="ASX"

#baixa "http://www.sfe.com.au/Content/reports/EODWebMarketSummary${ano_2}${mes}${dia}SFT.htm" "$prefix" "html"
baixa "http://www.asx.com.au/data/markets/futures/reports/EODWebMarketSummary${ano_2}${mes}${dia}SFT.htm" "$prefix" "html"
ret=$?

if [ $ret -eq 0 ]; then
        fl=`file "tudo/${prefix}_${data}_${download}.html" | grep "HTML document"`
        if [ -z "$fl" ]; then
                echo "`date`: Arquivo tudo/${prefix}_${data}_${download}.html não é HTML, descartando"
                mailx -s "arquivo ${prefix} para $data inválido (não é HTML)" capta <<FIM
        `ls -l "tudo/${prefix}_${data}_${download}.html"`
        `file "tudo/${prefix}_${data}_${download}.html"`
        `head -n 3 "tudo/${prefix}_${data}_${download}.html"`
FIM
                mv tudo/${prefix}_${data}_${download}.html /tmp/
                exit 1
	fi

	erro=`grep "The ASX website is temporarily unavailable due to scheduled maintenance" tudo/${prefix}_${data}_${download}.html`
	if [ -n "$erro" ]; then
               	echo "`date`: Arquivo tudo/${prefix}_${data}_${download}.html tem mensagem de manutenção, descartando"
                mailx -s "arquivo ${prefix} para $data é msg de manutenção" capta <<FIM
        `ls -l "tudo/${prefix}_${data}_${download}.html"`
        `file "tudo/${prefix}_${data}_${download}.html"`
        `head -n 3 "tudo/${prefix}_${data}_${download}.html"`
FIM
                mv tudo/${prefix}_${data}_${download}.html /tmp/
		exit 1
	fi	
	
	erro=`grep "Quoted figures are based on latest available information at the time of report generation" tudo/${prefix}_${data}_${download}.html`
	if [ -z "$erro" ]; then
               	echo "`date`: Arquivo tudo/${prefix}_${data}_${download}.html não está completo, descartando"
                mailx -s "arquivo ${prefix} para $data incompleto" capta <<FIM
        `ls -l "tudo/${prefix}_${data}_${download}.html"`
        `file "tudo/${prefix}_${data}_${download}.html"`
        `head -n 3 "tudo/${prefix}_${data}_${download}.html"`
FIM
                mv tudo/${prefix}_${data}_${download}.html /tmp/
		exit 1
	fi	
	
	data_arq=`obtem_data tudo/${prefix}_${data}_${download}.html`
	if [ "$data" != "$data_arq" ]; then
		echo "Arquivo tem dados de $data_arq, mudando data no nome do arquivo"
		mv tudo/${prefix}_${data}_${download}.html tudo/${prefix}_${data_arq}_${download}.html
		data=$data_arq
	fi

	cat tudo/${prefix}_${data}_${download}.html | grep -v "Report Generation Time:" | /$HOME/bin/limpar_script_final.pl > tudo/${prefix}_${data}_${download}.html.tmp
	mv tudo/${prefix}_${data}_${download}.html.tmp tudo/${prefix}_${data}_${download}.html
        linka_se_novo "${prefix}" "html"
        ret=$?
        exit $ret
fi




