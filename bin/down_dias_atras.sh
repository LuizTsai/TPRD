#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 2 ]; then
	echo "Uso: down_dias_atras.sh <script> <dias>"
	echo "	<script>: script de download que aceita uma data (AAAAMMDD) como parâmetro"
	echo "	<dias>: número de dias no passado a ser baixado (0 é hoje)"
	exit
fi

dias=`echo $2 | sed -n "s/[^0-9]*\([0-9]*\).*/\1/p"`
data=`date -d "$dias days ago" "+%Y%m%d"`
echo ""
echo "------------------------------------"
echo "`date`: Chamando $1 para $dias atrás ($data)"
$HOME/bin/$1 $data
