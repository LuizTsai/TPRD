#!/usr/bin/python
# coding=UTF8

import db
import conv

debug = 3 
ret =  db.carrega_moedas(debug)

for i in conv.moedas.items():
	i[1].imprime()
