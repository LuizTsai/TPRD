#!/bin/sh

if [ $# -eq 0 ]; then
	echo "Uso: teste_proxy <IP>:<porta>"
	exit
fi

export http_proxy="$1"
wget -O /tmp/testa_proxy.html -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0" "http://www.stilllistener.addr.com/checkpoint1/test2/"
lynx /tmp/testa_proxy.html
