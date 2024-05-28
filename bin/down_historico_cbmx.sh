#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 

data_dir="$HOME/data/cbmx"

ano="2013"
download=` date "+%Y%m%d%H%M"`

cd $data_dir




baixa_arq () {

        wget -nv -c "$1" -O "tudo/${2}_${ano}${mes}${dia}_${download}.html"
        ret=$?
        if [ $ret -ne 0 ]; then
                echo "`date`: wget retornou problemas ($ret)"
                rm "tudo/${2}_${ano}${mes}${dia}_${download}.html"
        else
                if [ -f "${2}_${ano}${mes}${dia}.html" ]; then
                        diff "${2}_${ano}${mes}${dia}.html" "tudo/${2}_${ano}${mes}${dia}_${download}.html" >  /dev/null
                        if [ $? -ne 0 ]; then
                                echo "`date`: Arquivo $2 do dia $data diferente do baixado anteriormente, mantendo!"
                                rm "${2}_${ano}${mes}${dia}.html"
                                ln -s "tudo/${2}_${ano}${mes}${dia}_${download}.html" "${2}_${ano}${mes}${dia}.html"
                        else
                                echo "`date`: Arquivo $2 do dia $data idêntico ao baixado anteriormente, removendo..."
                                rm "tudo/${2}_${ano}${mes}${dia}_${download}.html"
                        fi
                else
                        echo "`date`: Arquivo $2 do dia $data baixado pela primeira vez, mantendo..."
                        ln -s "tudo/${2}_${ano}${mes}${dia}_${download}.html" "${2}_${ano}${mes}${dia}.html"
                fi
        fi
}


obtem_spot_link () {

	echo "Baixando página $2"

	wget -nv -c "$1/article/chinairon/$2" -O "tudo/spot.html"
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "`date`: wget retornou problemas ($ret) ao procurar link do Spot Trading Data" 1>&2
		rm "tudo/spot.html"
		echo ""
	else
		for i in `cat tudo/spot.html | grep "<a title=\"China Iron Ore Spot Trading Data([A-Za-z]* [0-9]*, ${ano})\"" | tr -d \ `; do
			echo $i
			mes_a=`echo $i | sed -n "s/[^(]*(\([A-Za-z]*\)[0-9]*.*/\1/p"`
			dia=`echo $i | sed -n "s/[^(]*([A-Za-z]*\([0-9]*\),.*/\1/p"`
			data=`date -d "$mes_a $dia, $ano" "+%Y%m%d"`
			echo $data
			mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
			l=`echo $i | sed -n "s/.*href=\"\([^\"]*\)\".*/\1/p"`

			baixa_arq "http://en.cbmx.com.cn/$l" "CBMX_Spot_Trading"
		done
	fi
}




obtem_spot_link "http://en.cbmx.com.cn" "?6"
