#!/bin/bash

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download


echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da Euronext para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da Euronext para o dia $data"
fi

ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

euronext () {
	rm tudo/lixo*html
	#baixa "http://derivatives.euronext.com/sites/derivatives.euronext.com/files/statistics/derivatives/daily/${ano}/${1}-DailyDerivativesStatistics%20${ano}-${mes}-${dia}.xls" "Euronext_${1}" "xls"
	baixa "http://www.euronext.com/sites/www.euronext.com/files/statistics/derivatives/daily/${ano}/${1}-DailyDerivativesStatistics%20${ano}-${mes}-${dia}.xlsx" "Euronext_${1}" "xls"


	ret=$?

	if [ $ret -eq 0 ]; then
        	fl=`file "tudo/Euronext_${1}_${data}_${download}.xls" | grep "Composite Document File V2 Document"`
        	fl2=`file "tudo/Euronext_${1}_${data}_${download}.xls" | grep "Microsoft Excel"`

	        if [ -z "$fl" || -z "$fl2" ]; then
        	        echo "`date`: Arquivo tudo/Euronext_${1}_${data}_${download}.xls não é XLS, descartando"
#                mailx -s "arquivo Euronext para $data inválido (não é XLS)" capta <<FIM
#        `ls -l "tudo/Euronext_${data}_${download}.xls"`
#        `file "tudo/Euronext_${data}_${download}.xls"`
#        `head -n 3 "tudo/Euronext_${data}_${download}.xls"`
#FIM
                	mv tudo/Euronext_${1}_${data}_${download}.xls /tmp/
	                return 1
        	else
                	linka_se_novo "Euronext_${1}" "xls"
	                ret=$?
        	        return $ret
	        fi
	fi
}


#delay
data_dir="$HOME/data/euronext/paris"

cd $data_dir
echo "Euronext"
#baixa "http://derivatives.euronext.com/statistics-files-ajax/derivatives~daily~2015/*/*" "lixo" "html" "--save-cookies /tmp/cookies-euronext_1 --keep-session-cookies --referer=\"http://derivatives.euronext.com/trading/reports-statistics/daily-statistics\""
baixa "http://www.euronext.com/en/reports-statistics/derivatives/daily-statistics" "lixo" "html" "--save-cookies /tmp/cookies-euronext_1 --keep-session-cookies --referer=\"http://derivatives.euronext.com/trading/reports-statistics/daily-statistics\""


run_dir="/home/capta/run/euronext_amsterdam"
data_dir="$HOME/data/euronext/amsterdam"
cd $data_dir

euronext "Amsterdam"

