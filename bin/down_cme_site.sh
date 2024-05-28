#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

home=/devel/diego/TPRD

. ${home}/bin/http_proxy
. ${home}/bin/funcoes_download


data=`date "+%Y%m%d%H%M%S"`
baixa_arq() {
	echo ""
	echo "`date`: Baixando $1" 1>&2
	if [ -f "tudo/${1}_${data}_${download}.txt" ]; then
		rm tudo/${1}_${data}_${download}.txt
	fi
	saida=`baixa "ftp://ftp.cmegroup.com/pub/settle/${1}" $1 "txt"`
	ret_bx=$?
        if [ $ret_bx -ne 0 ]; then
                echo "`date`: wget retornou problemas ($ret)" 1>&2
                rm "tudo/${1}_${data}_${download}.txt"
		mailx -s "problemas no wget da CME/site" capta <<FIM
	Arquivo: $1
	wget retornou $ret
	Saída do wget:
$saida
FIM
                return 1
	fi
	echo $saida
	if [ -f tudo/${1}.last ]; then
		echo "Existe $1.last, verificando se mudou" 1>&2
		diff tudo/${1}_${data}_${download}.txt tudo/${1}.last > /dev/null 2>&1
		ret=$?
		if [ $ret -eq 0 ]; then
			echo "Arquivo $1 não mudou, descartando..." 1>&2
			rm tudo/${1}_${data}_${download}.txt
			return 2
		fi
	fi
	if [ -f tudo/${1}_${data}_${download}.txt ]; then
		mv tudo/${1}_${data}_${download}.txt tudo/${1}_${data}
		md5sum tudo/${1}_${data}
		rm tudo/${1}.last
		ln -s ${1}_${data} tudo/${1}.last
	fi
	return 0
}

trata_arq_texto() {
	echo "-----------------------------------"
	echo "arq=$1, string=$2"
	baixa_arq "$1"
	ret=$? 

	if [ $ret -eq 0 ]; then
		if [ ! -L tudo/${1}.last ]; then
			echo "ERRO: $1.last não é um link simbólico!" 1>&2 }
			return 0
		fi
		nome_arq=`ls -l tudo/${1}.last | sed -n "s/[^>]*> \(.*\)/\1/p"`
		data_arq=`cat "tudo/$1.last" | grep "$2" | sed -n "s/ *$2 \([0-9]*\)\/\([0-9]*\)\/\([0-9]*\) .*/\3\1\2/p"`

		if [ -z "$data_arq" ]; then
			echo "Arquivo $1 baixado não é final, ignorando"
			return 1
		fi
		if [ -f ${1}_${data_arq} ]; then
			diff tudo/${1}.last ${1}_${data_arq} > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				echo "Arquivo $1 para o dia $data_arq, não mudou" 1>&2
				return 1
			else
				echo "Novo arquivo $1 para o dia $data_arq, substituindo" 1>&2
				rm ${1}_${data_arq}
			fi
		else
			echo "Arquivo $1 para o dia $data_arq identificado, linkando"
		fi
		ln -fs $data_dir/tudo/$nome_arq ${1}_${data_arq}
		if [ -n "$run_dir" ]; then
			echo "Criando link em $run_dir"
			ln -fs $data_dir/tudo/$nome_arq $run_dir/${1}_${data_arq}
		fi
		return 1
	fi
}

trata_arq_csv() {
	echo "-----------------------------------"
	echo "arq=$1"
	baixa_arq "$1"
	ret=$? 

	if [ $ret -eq 0 ]; then
		if [ ! -L tudo/${1}.last ]; then
			echo "ERRO: $1.last não é um link simbólico!" 1>&2 }
			return 0
		fi
		nome_arq=`ls -l tudo/${1}.last | sed -n "s/[^>]*> \(.*\)/\1/p"`
		data_arq=`tail -n 1 "tudo/$1.last" | sed -n "s/.*,\([0-9]*\)\/\([0-9]*\)\/\([0-9]*\)$/\3\1\2/p"`
		echo "arquivo $nome_arq tem dados de $data_arq"

		if [ -f ${1}_${data_arq} ]; then
			diff tudo/${1}.last ${1}_${data_arq} > /dev/null 2>&1
			if [ $? -eq 0 ]; then
				echo "Arquivo $1 para o dia $data_arq, não mudou" 1>&2
				return 1
			else
				echo "Novo arquivo $1 para o dia $data_arq, substituindo" 1>&2
				rm ${1}_${data_arq}
			fi
		else
			echo "Arquivo $1 para o dia $data_arq identificado, linkando"
		fi
		ln -s $data_dir/tudo/$nome_arq ${1}_${data_arq}
		if [ -n "$run_dir" ]; then
			echo "Criando link em $run_dir"
			ln -fs $data_dir/tudo/$nome_arq $run_dir/${1}_${data_arq}
		fi
		return 1
	fi
}

echo "======================================================"
echo "`date`: Início"

delay

data_dir="${home}/data/cme/stlags"
run_dir="${home}/run/cme_agro"
cd $data_dir
trata_arq_texto "stlags_v2" "FINAL PRE-CLEARING PRICES AS OF"


data_dir="${home}/data/cme/comex"
run_dir="${home}/capta/run/comex"
cd $data_dir
trata_arq_texto "stlcomex_v2" "FINAL POST-CLEARING PRICES AS OF"
#trata_arq_csv "comex_future.csv"


data_dir="${home}/data/cme/nymex"
run_dir="${home}/capta/run/nymex"
cd $data_dir
#trata_arq_csv "nymex_future.csv"
#run_dir=""
trata_arq_texto "stlnymex_v2" "FINAL POST-CLEARING PRICES AS OF"

echo "`date`: Fim"
