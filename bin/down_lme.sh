#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

HOME=/devel/diego/TPRD

#. $HOME/bin/http_proxy 
#echo "incluiu http_proxy"
. $HOME/bin/funcoes_download 
echo "incluiu funcoes_download"

data_dir="$HOME/data/lme"
run_dir="$HOME/run/lme"
data=`date -d yesterday "+%Y%m%d"` 
echo ""
echo "`date`: Baixando arquivos da LME para ontem ($data)"

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir


baixa_arq () {
	echo "" 
	echo "Baixando arquivo $2"
	baixa $1 $2 "tmp"
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "`date`: wget retornou problemas ($ret)"
		rm "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"
	else
		if [ -f "tudo/${2}_${ano}${mes}${dia}_${download}.tmp" -a -s "tudo/${2}_${ano}${mes}${dia}_${download}.tmp" ]; then
			msg=`grep "The online users' count exceeds the license's permission. You need to purchase or upgrade your license" "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"`
			if [ -n "$msg" ]; then
				echo "Arquivo baixado (tudo/${2}_${ano}${mes}${dia}_${download}.tmp) tem mensagem de erro do proxy de excesso de usuários"
				rm "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"
				return 171
			else
				msg=`grep "<title>London Metal Exchange" "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"`
	                        if [ -z "$msg" ]; then
        	                        echo "Arquivo baixado (tudo/${2}_${ano}${mes}${dia}_${download}.tmp) não tem <title> London Metal Exchange"
#                	                rm "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"
                        	        return 2
				else
					# remover img que muda de um download pro outro
					cat "tudo/${2}_${ano}${mes}${dia}_${download}.tmp" | sed "s/<img id=[^>]*>//" | sed "s/\/en-gb\//\//" | sed "s/<input type=\"hidden\" [^>]*>//" | grep -v "<ul class=\"nav\"" | grep -v "<li><a href=" | $HOME/bin/retira_scripts.pl > "tudo/${2}_${ano}${mes}${dia}_${download}.html"
					mv "tudo/${2}_${ano}${mes}${dia}_${download}.tmp" tmp/
					# obter data dos dados baixados
					data_a=`cat "tudo/${2}_${ano}${mes}${dia}_${download}.html" | sed -n "s/.*prices for \([0-9]*\) \([A-Za-z]*\) \([0-9]*\)[^0-9].*/\1 \2 \3/p"`
					data_p=`date -d "$data_a" "+%Y%m%d"`
					if [ -n "$data_p" ]; then
						data_ant=$data
						if [ "$data" != "$data_p" ]; then
							mv "tudo/${2}_${ano}${mes}${dia}_${download}.html" "tudo/${2}_${data_p}_${download}.html"
						fi
						data=$data_p
						linka_se_novo $2 "html"
						ret=$?
						data=$data_ant
						if [ $ret -ne 0 ]; then
							return $ret
						fi
					else
						echo "Não achou data no arquivo"
						mv "tudo/${2}_${ano}${mes}${dia}_${download}.html" tudo/lixo/
						return 10
					fi
				fi
			fi
		else
			echo "`date`: arquivo obtido está zerado, removendo"
			rm "tudo/${2}_${ano}${mes}${dia}_${download}.tmp"
		fi
	fi
}

loop_baixa_arq () {
	echo "----------------------"
	echo "data=$data, anomesdia=$ano$mes$dia"
	delay
	ret_baixa=171
	while [ $ret_baixa -eq 171 ]; do
		baixa_arq $1 $2
		ret_baixa=$?
		sleep 1
###		obtem_proxy
	done
}


delay 1200
http_proxy=""
loop_baixa_arq "http://www.lme.com/metals/non-ferrous/" "LME-non-ferrous"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/aluminium" "LME-aluminium"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/aluminium-alloy" "LME-aluminium-alloy"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/copper" "LME-copper"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/lead" "LME-lead"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/nickel" "LME-nickel"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/tin" "LME-tin"
#loop_baixa_arq "http://www.lme.com/metals/non-ferrous/zinc" "LME-zinc"


loop_baixa_arq "http://www.lme.com/metals/minor-metals/" "LME-minor-metals"
#loop_baixa_arq "http://www.lme.com/en-gb/metals/ferrous/lme-steel-billet" "LME-steel-billet"
# não tem cotações...
loop_baixa_arq "http://www.lme.com/metals/ferrous/lme-steel-rebar" "LME-steel-rebar"
loop_baixa_arq "http://www.lme.com/metals/ferrous/lme-steel-scrap" "LME-steel-scrap"

