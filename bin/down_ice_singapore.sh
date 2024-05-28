#!/bin/bash

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/ice/singapore"
#data_dir="$HOME/tmp"

echo ""
if [ $# -eq 0 ]; then
        data=`date -d yesterday "+%Y%m%d"`
        echo "Baixando arquivo da ICE-Singapore para ontem ($data)"
else
        data=$1
        echo "Baixando arquivo da ICE-Singapore para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#mes_a=$(($mes-1))
mes_a=$((`echo $mes | sed -n "s/^0*//p"` - 1))
download=` date "+%Y%m%d%H%M"`

delay
cd $data_dir

run_dir="/home/capta/run/ice_singapore"
echo $http_proxy
baixa "https://www.theice.com/marketdata/reports/ReportCenter.shtml#report/11" "lixo" "html" "--save-cookies /tmp/cookies-ice-sing_1 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\""

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml?selectionForm=?optionRequest=false?exchangeCode=IFSG" "lixo2" "html" "--load-cookies /tmp/cookies-ice-sing_1 --save-cookies /tmp/cookies-ice-sing_2 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\""

SMPBSS=`cat $data_dir/tudo/lixo2_${data}_${download}.html | grep "name=\"smpbss\" value=" | tail -n 1 | sed -n 's/.*name="smpbss"  *value="\([^"]*\)".*/\1/p'`

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml" "lixo3" "html" "--load-cookies /tmp/cookies-ice-sing_2 --save-cookies /tmp/cookies-ice-sing_3 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\" --post-data=smpbss=$SMPBSS&exchangeCode=IFSG&optionRequest=false&selectionForm=&selectedContract=ALLCONTRACTS&"

SMPBSS=`cat $data_dir/tudo/lixo3_${data}_${download}.html | grep "name=\"smpbss\" value=" | tail -n 1 | sed -n 's/.*name="smpbss"  *value="\([^"]*\)".*/\1/p'`
echo "smpbss=$SMPBSS"

rm $data_dir/tudo/lixo*

baixa "https://www.theice.com/marketdata/reports/datawarehouse/ConsolidatedEndOfDayReportPDF.shtml" "ice_singapore" "pdf" "--load-cookies /tmp/cookies-ice-sing_3 --save-cookies /tmp/cookies-ice-sing_4 --keep-session-cookies --referer=\"https://www.theice.com/marketdata/reports/ReportCenter.shtml\" --header=DNT:1 --post-data=generateReport=&smpbss=${SMPBSS}&exchangeCode=IFSG&optionRequest=false&exchangeCodeAndContract=ALLCONTRACTS&selectedDate=${mes}/${dia}/${ano}&submit=Download&"

ret=$? 

if [ $ret -eq 0 ]; then
        fl=`file "tudo/ice_singapore_${data}_${download}.pdf" | grep "PDF document"`
        if [ -z "$fl" ]; then
                echo "`date`: Arquivo tudo/ice_singapore_${data}_${download}.pdf não é PDF, descartando"
                mailx -s "arquivo ICE-Singapore  para $data inválido (não é PDF)" capta <<FIM
        `ls -l "tudo/ice_singapore_${data}_${download}.pdf"`
        `file "tudo/ice_singapore_${data}_${download}.pdf"`
        `head -n 3 "tudo/ice_singapore_${data}_${download}.pdf"`
FIM
                mv tudo/ice_singapore_${data}_${download}.pdf /tmp/
                exit 1
        else
                linka_se_novo "ice_singapore" "pdf"
                ret=$?
                exit $ret
        fi
fi
