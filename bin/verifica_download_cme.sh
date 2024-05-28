#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 1 ]; then
	echo "Uso: verifica_download_cme.sh <dias>"
	echo "	<dias>: número de dias no passado do dia a ser verificado (0 é hoje)"
	exit
fi

home=/devel/diego/TPRD

dias=`echo $1 | sed -n "s/[^0-9]*\([0-9]*\).*/\1/p"`
data=`date -d "$dias days ago" "+%Y%m%d"`

verifica() {
	pwd
	echo "Verificando $1 para $data (${i}_${data})"
	if [ -f "${1}_${data}" ]; then
		echo ".... OK, existe"
	else
		echo "Problemas, não existe"
		problemas=`echo $problemas; echo "${1}_${data}"`
	fi
}


problemas=""

cd ${home}/data/cme/stlags
for i in stlags_v2; do 
	verifica $i
done

cd ${home}/data/cme/comex
for i in stlcomex_v2; do
	verifica $i
done

cd ${home}/data/cme/nymex
for i in stlnymex_v2; do
	verifica $i
done

if [ -n "$problemas" ]; then
	echo "Arquivos não encontrados: "
	echo $problemas
	mailx -s "Arquivos de CME para $data não baixados"  capta <<FIM
		Arquivos não baixados: $problemas

`ls -lh *_${data}`
FIM
fi
