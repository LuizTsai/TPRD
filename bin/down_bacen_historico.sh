#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/funcoes_download

obtem_proxy() {
	echo ""
}

data_dir="$HOME/data/bacen"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da BACEN para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da BACEN para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
mes_a=`date -d $data +%b`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir

#delay

saida=`wget  --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0"  --post-data="RadOpcao=2&DATAINI=${dia}%2F${mes}%2F${ano}&DATAFIM=----------------------&ChkMoeda=220&butao=Pesquisar&OPCAO=2&MOEDA=&DESCMOEDA=&TxtOpcao5=DOLAR-DOS-EUA&TxtOpcao4=220&BOLETIM=" "http://www4.bcb.gov.br/pec/taxas/port/PtaxRPesq.asp?idpai=TXCOTACAO" -O "tudo/TAB_${data}_${download}.html"`
ret=$?
if [ $ret -ne 0 ]; then
	echo "PROBLEMAS no download"
	mailx -s "Problemas no wget do BACEN para $data" capta <<FIM
        wget retornou $ret
        Saída do wget:
$saida
FIM
	exit 1 
else
	if [ -s "tudo/TAB_${data}_${download}.html" ]; then
		URL=`cat "tudo/TAB_${data}_${download}.html" | obtem_URL_bacen.pl`
		echo "URL: $URL"
		if [ -z "$URL" ]; then
			echo "URL do arquivo de download não encontrada em TAB_${data}_${download}.html"
			mailx -s "URL do arquivo de download do BACEN para $data não encontrada" capta <<FIM
	arquivo: TAB_${data}_${download}.html
FIM
			exit 2
		else
			saida=`baixa_arquivo "$URL" "BACEN" "csv"`
			ret=$?
			if [ $ret -ne 0 ]; then
				echo "PROBLEMAS no download do arquivo de cotações"
				mailx -s "Problemas no download das cotações BACEN para $data" cpta <<FIM
		URL: $URL
		retorno do baixa_arquivo: $ret
		Saída do baixa_arquivo:
$saida
FIM
			else
				rm "tudo/TAB_${data}_${download}.html"
			fi
		fi
	else
		echo "`date`: Arquivo tudo/TAB_${data}_${download}.html zerado, descartando"
		rm "tudo/TAB_${data}_${download}.html"
		exit 1
	fi
fi

