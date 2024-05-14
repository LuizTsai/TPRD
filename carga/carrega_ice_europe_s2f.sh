#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -lt 1 ]; then
	echo "Uso: carrega_ice_europe_s2f.sh <arquivo pdf da ice europe s2f>"
	exit 1
fi

if [ ! -f $1 ]; then
	echo "Erro: $1 não existe ou não é arquivo"
	exit 1
fi

pdftotext -layout -nopgbrk $1
arq=`echo $1 | sed -n "s/pdf$/txt/p"`
echo $arq
/home/capta/carga/ice_europe_s2f.py  $arq
