#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 1 ]; then
	echo "Uso: verifica_download_ice_eur-sf2.sh <dias>"
	echo "	<dias>: número de dias no passado do dia a ser verificado (0 é hoje)"
	exit
fi

dias=`echo $1 | sed -n "s/[^0-9]*\([0-9]*\).*/\1/p"`
data=`date -d "$dias days ago" "+%Y%m%d"`

cd $HOME/data/ice/europe-s2f

problemas=""
for i in ice_europe_s2f; do
	echo "Verificando $i para $data (${i}_${data}.pdf)"
	if [ -f "${i}_${data}.pdf" ]; then
		echo ".... OK, existe"
	else
		echo "Problemas, não existe"
		problemas=`echo $problemas; echo "${i}_${data}.pdf"`
	fi
done
if [ -n "$problemas" ]; then
	echo "Arquivos não encontrados: "
	echo $problemas
	mailx -s "Arquivos de ICE-Eur-s2f para $data não baixados"  capta <<FIM
		Arquivos não baixados: $problemas

`ls -lh *_${data}*`
FIM
fi
