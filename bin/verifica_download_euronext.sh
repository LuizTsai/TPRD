#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 1 ]; then
	echo "Uso: verifica_download_euronext.sh <dias>"
	echo "	<dias>: número de dias no passado do dia a ser verificado (0 é hoje)"
	exit
fi

dias=`echo $1 | sed -n "s/[^0-9]*\([0-9]*\).*/\1/p"`
data=`date -d "$dias days ago" "+%Y%m%d"`

cd $HOME/data/euronext

problemas=""
for i in Euronext; do
	echo "Verificando $i para $data (${i}_${data}.xls)"
	if [ -f "${i}_${data}.xls" ]; then
		echo ".... OK, existe"
	else
		echo "Problemas, não existe"
		problemas=`echo $problemas; echo "${i}_${data}.xls"`
	fi
done
if [ -n "$problemas" ]; then
	echo "Arquivos não encontrados: "
	echo $problemas
	mailx -s "Arquivos de Euronext para $data não baixados"  capta <<FIM
		Arquivos não baixados: $problemas

`ls -lh *_${data}*`
FIM
fi
