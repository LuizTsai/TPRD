#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 1 ]; then
	echo "Uso: verifica_download_afet.sh <dias>"
	echo "	<dias>: número de dias no passado do dia a ser verificado (0 é hoje)"
	exit
fi

dias=`echo $1 | sed -n "s/[^0-9]*\([0-9]*\).*/\1/p"`
data=`date -d "$dias days ago" "+%Y%m%d"`

cd $HOME/data/afet

problemas=""
for i in xls;  do
	echo "Verificando AFET.$i para $data (AFET_${data}.${i})"
	if [ -f "AFET_${data}.${i}" ]; then
		echo ".... OK, existe"
	else
		echo "Problemas, não existe"
		problemas=`echo $problemas; echo "AFET_${data}.${i}"`
	fi
done
if [ -n "$problemas" ]; then
	echo "Arquivos não encontrados: "
	echo $problemas
	mailx -s "Arquivos de AFET para $data não baixados"  capta <<FIM
`date`
		Arquivos não baixados: $problemas

`ls -lh *_${data}*`
FIM
fi
