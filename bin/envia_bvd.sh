#!/bin/sh

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 2 ]; then
	echo "Uso: envia_bvd.sh <diretorio> <arquivo>"
fi

if [ ! -d "$1" ]; then
	echo "Erro: diretório não existe"
	exit 1
fi

cd $1

if [ ! -f "$2" ]; then
	echo "Erro: arquivo $2 não existe"
	exit 1
fi

rm /tmp/Done.txt
echo "1" > /tmp/Done.txt
ftp -in <<FIM
open ftp.bvdep.com
user tprd DqZaMc_5594
passive
binary 
put $2
delete Done.txt
lcd /tmp
put Done.txt
ls
quit
FIM
