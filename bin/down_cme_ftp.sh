#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy

data_dir="$HOME/data/cme/ftp"

cd $data_dir

echo "`date`: Início"
delay

wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/cbt.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/cme.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/comex.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/dme.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/kcb.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/md.commodity.fut.[0-9]*.xml.zip
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/nymex.settle.[0-9]*.[se].txt
wget -c --proxy-user=${proxy_user} --proxy-password=${proxy_passwd} --tries=5 --progress=dot:mega --waitretry=5 --random-wait --retry-connrefused -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" ftp://ftp.cmegroup.com/pub/settle/st[0-9]*.zip

echo "`date`: Fim"
