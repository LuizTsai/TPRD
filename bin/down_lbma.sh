#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/lbma"

echo ""
if [ $# -eq 0 ]; then
	data=`date -d yesterday "+%Y%m%d"` 
	echo "`date`: Baixando arquivos da LBMA para ontem ($data)"
else
	data=$1
	echo "`date`: Baixando arquivos da LBMA para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
ano_2=`echo $data | sed -n "s/^[0-9]\{2\}\([0-9]\{2\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#echo "ano=$ano, mes=$mes, mes_a=$mes_a, dia=$dia"

download=` date "+%Y%m%d%H%M"`

cd $data_dir


delay

#baixa_arquivo "http://www.lbma.org.uk/pages/printerFriendly.cfm?thisURL=index.cfm&show=${ano}&title=gold_fixings&page_id=53&type=daily" "LBMA_Gold" "html"
#baixa_arquivo "http://www.lbma.org.uk/pages/printerFriendly.cfm?thisURL=index.cfm&show=${ano}&title=silver_fixings&page_id=54&type=daily" "LBMA_Silver" "html"
#baixa_arquivo "http://www.lbma.org.uk/pages/printerFriendly.cfm?thisURL=index.cfm&page_id=55&title=gold_forwards&show=${ano}" "LBMA_Gold_Forward" "html"
baixa_arquivo "http://lbma.oblive.co.uk/table?metal=gold&year=${ano}&type=daily" "LBMA_Gold" "html"
baixa_arquivo "http://lbma.oblive.co.uk/table?metal=silver&year=${ano}&type=daily" "LBMA_Silver" "html"
baixa_arquivo "http://lbma.oblive.co.uk/table?metal=platinum&year=${ano}&type=daily" "LBMA_Platinum" "html"
baixa_arquivo "http://lbma.oblive.co.uk/table?metal=palladium&year=${ano}&type=daily" "LBMA_Palladium" "html"


