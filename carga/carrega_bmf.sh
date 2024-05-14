#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -lt 1 ]; then
	echo "Uso: carrega_bmf.sh <arquivo zip da bmf>"
	exit 1
fi

if [ ! -f $1 ]; then
	echo "Erro: $1 não existe ou não é arquivo"
	exit 1
fi

tmp=`mktemp -d --tmpdir=/tmp BMF.XXXX`
dirtmp=`basename $tmp`
echo "$tmp $dirtmp"
unzip $1 -d $tmp
/home/capta/carga/bmf.py $tmp/BD_Final.txt
rm -rf /tmp/$dirtmp
