#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 

. $HOME/bin/funcoes_download

data_dir="$HOME/data/ice/europe-s2f"

echo ""
if [ $# -eq 0 ]; then
        data=`date -d yesterday "+%Y%m%d"`
        echo "Baixando arquivo da ICE-Europe-S2F para ontem ($data)"
else
        data=$1
        echo "Baixando arquivo da ICE-Europe-S2F para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir
run_dir="/home/capta/run/ice_europe_s2f"

delay

rm /tmp/cookies-ice-eur-s2f*

baixa "https://www.theice.com/marketdata/reports/ReportCenter.shtml#report/144" "lixo" "html" "--save-cookies /tmp/cookies-ice-eur-s2f-1 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\""

#tempo=`date +%s`
#baixa "https://www.theice.com/Login.shtml?t=${tempo}006" "lixo1" "html" "--load-cookies /tmp/cookies-ice-eur-s2f-1 --save-cookies /tmp/cookies-ice-eur-s2f-2 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\""

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml?selectionForm=?optionRequest=false?exchangeCode=IFES" "lixo2" "html" "--load-cookies /tmp/cookies-ice-eur-s2f-1 --save-cookies /tmp/cookies-ice-eur-s2f-2 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\""

SMPBSS=`cat $data_dir/tudo/lixo2_${data}_${download}.html | grep "name=\"smpbss\" value=" | tail -n 1 | sed -n 's/.*name="smpbss"  *value="\([^"]*\)".*/\1/p'`

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml" "lixo3" "html" "--load-cookies /tmp/cookies-ice-eur-s2f-2 --save-cookies /tmp/cookies-ice-eur-s2f-3 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\" --post-data=smpbss=$SMPBSS&exchangeCode=IFES&optionRequest=false&selectionForm=&selectedContract=ALLCONTRACTS&"
SMPBSS=`cat $data_dir/tudo/lixo3_${data}_${download}.html | grep "name=\"smpbss\" value=" | tail -n 1 | sed -n 's/.*name="smpbss"  *value="\([^"]*\)".*/\1/p'`

rm $data_dir/tudo/lixo*

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml" "ice_europe_s2f" "pdf" "--load-cookies /tmp/cookies-ice-eur-s2f-3 --save-cookies /tmp/cookies-ice-eur-s2f-4 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\" --header=DNT:1 --post-data=generateReport=&smpbss=${SMPBSS}&exchangeCode=IFES&optionRequest=false&exchangeCodeAndContract=ALLCONTRACTS&selectedDate=${mes}/${dia}/${ano}&submit=Download&"
ret=$?
if [ $ret -eq 0 ]; then
	fl=`file "tudo/ice_europe_s2f_${data}_${download}.pdf" | grep "PDF document"`
	if [ -z "$fl" ]; then
		echo "`date`: Arquivo tudo/ice_europe_s2f_${data}_${download}.pdf não é PDF, descartando"
		mailx -s "arquivo ICE Europe S2F para $data inválido (não é PDF)"  capta <<FIM
	`ls -l "tudo/ice_europe_s2f_${data}_${download}.pdf"`
	`file "tudo/ice_europe_s2f_${data}_${download}.pdf"`
	`head -n 3 "tudo/ice_europe_s2f_${data}_${download}.pdf"`
FIM
		exit 1
	else
		linka_se_novo "ice_europe_s2f" "pdf"
		ret=$?
		exit $ret
	fi
fi


