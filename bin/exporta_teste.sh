#!/bin/sh

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#


data=`date  "+%Y%m%d%H%M"`
dir="teste"
cd /tmp

mkdir $dir
for i in Categoria; do
	exporta_tabela.sh $dir $i
done

