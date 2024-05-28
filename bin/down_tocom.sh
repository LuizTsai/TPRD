#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/tocom"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da TOCOM para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da TOCOM para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M%S"`

cd $data_dir


baixa_arq () {
	echo "`date`: Baixando arquivo do mês atual"
	baixa $1 "" "csv"
	ret=$?
	if [ $ret -ne 0 ]; then
		return 1
	fi
	if [ -f "tudo/_${ano}${mes}${dia}_${download}.csv" -a -s "tudo/_${ano}${mes}${dia}_${download}.csv" ]; then
		mv "tudo/_${ano}${mes}${dia}_${download}.csv" "tudo/${ano}-${mes}_${download}.csv"
		if [ -f "tudo/${ano}-${mes}.csv" ]; then
			diff "tudo/${ano}-${mes}.csv" "tudo/${ano}-${mes}_${download}.csv" >  /dev/null
			if [ $? -eq 0 ]; then
				echo "`date`: Arquivo do mês $ano-$mes idêntico do baixado anteriormente, removendo..."
                                rm "tudo/${ano}-${mes}_${download}.csv"
			else
				rm "tudo/${ano}-${mes}.csv"
				ln -s "${ano}-${mes}_${download}.csv" "tudo/${ano}-${mes}.csv"
			fi
		else
			ln -s "${ano}-${mes}_${download}.csv" "tudo/${ano}-${mes}.csv"
		fi

		# filtrar registros do dia procurado
		echo "`date`: Filtrando dados do dia $data"
		cat "tudo/${ano}-${mes}.csv" | sed -n /^$data,/p > "tudo/${2}_${ano}${mes}${dia}_${download}.csv"
		if [ -s "tudo/${2}_${ano}${mes}${dia}_${download}.csv" ]; then
	 		if [ -f "${2}_${ano}${mes}${dia}.csv" ]; then
				diff "${2}_${ano}${mes}${dia}.csv" "tudo/${2}_${ano}${mes}${dia}_${download}.csv" >  /dev/null
				if [ $? -ne 0 ]; then
		        	        echo "`date`: Arquivo do dia $data diferente do baixado anteriormente, mantendo!"
		                	rm ${2}_${ano}${mes}${dia}.csv
		        	        ln -s $data_dir/tudo/${2}_${ano}${mes}${dia}_${download}.csv ${2}_${ano}${mes}${dia}.csv
		                        if [ -n "$run_dir" ]; then
                		                echo "Criando link em $run_dir"
                                		ln -fs $data_dir/tudo/${1}_${data}_${download}.${2} $run_dir/${1}_${data}.${2}
		                        fi
				else
        		        	echo "`date`: Arquivo do dia $data indêntico ao baixado anteriormente, removendo..."
	                		rm "tudo/${2}_${ano}${mes}${dia}_${download}.csv"
			        fi
			else
        			echo "`date`: Arquivo do dia $data baixado pela primeira vez, mantendo..."
	        		ln -s "$data_dir/tudo/${2}_${ano}${mes}${dia}_${download}.csv" "${2}_${ano}${mes}${dia}.csv"
	                        if [ -n "$run_dir" ]; then
               		                echo "Criando link em $run_dir"
                               		ln -fs $data_dir/tudo/${2}_${data}_${download}.csv $run_dir/${2}_${data}.csv
	                        fi
			fi
		else
			echo "`date`: Dia $data sem dados"
			rm "tudo/${2}_${ano}${mes}${dia}_${download}.csv"
		fi
	else
		echo "`date`: arquivo obtido está zerado, removendo"
		rm "tudo/_${ano}${mes}${dia}_${download}.csv"
	fi
}

delay
run_dir="/home/capta/run/tocom"
baixa_arq "www.tocom.or.jp/data/yakujou/${ano}-${mes}.csv" "TOCOM"



