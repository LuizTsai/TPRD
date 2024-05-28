#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/liffe/eur"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da LIFFE-Eur para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da LIFFE-Eur para o dia $data"
fi

ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

baixa_local () {
	baixa $1 $2 $3
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "Problemas ao baixar arquivo!"
	else
		fl=`file tudo/${2}_${data}_${download}.${3}`
		echo "file retornou: $fl"
		html=`echo $fl|grep HTML`
		if [ -n "$html" ]; then
			echo "Arquivo baixado (tudo/${2}_${data}_${download}.${3}) é HTML, quando deveria ser CSV... descartando!"
			mv tudo/${2}_${data}_${download}.${3} /tmp
#			rm tudo/${2}_${data}_${download}.${3}
		else
			erro=`grep "The online users' count exceeds the license's permission. You need to purchase or upgrade your license." tudo/${2}_${data}_${download}.${3}`
			if [ -n "$erro" ]; then
				echo "Arquivo baixado (tudo/${2}_${data}_${download}.${3}) tem mensagem de erro de excesso de usuários... descartando!"
                                mailx -s "down_liffe_eur: arquivo LIFFE_EUR para $data inválido"  capta <<FIM
		                Mensagem de excesso do usuários em `echo tudo/${2}_${data}_${download}.${3}`

				`cat tudo/${2}_${data}_${download}.${3}`
FIM
				mv tudo/${2}_${data}_${download}.${3} /tmp
			
			else
				linka_se_novo $2 $3
			fi
		fi
	fi 
}

delay

#run_dir="/home/capta/run/liffe_eur_london"
#echo "LIFFE Europe London"
#baixa_local "www.liffe.com/data/ds${ano_2}${mes}${dia}xf.csv" "LIFFE-london" "csv"

run_dir="/home/capta/run/liffe_eur_paris"
echo "LIFFE Europe Paris"
baixa_local "derivatives.euronext.com/sites/derivatives.euronext.com/files/statistics/derivatives/daily/2014/Paris-DailyDerivativesStatistics%20${ano}-${mes}-$dia}.xls" "LIFFE-paris" "xls"
#baixa_local "www.liffe.com/data/p_ds${ano_2}${mes}${dia}xf.csv" "LIFFE-paris" "csv"

