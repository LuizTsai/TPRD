#!/usr/bin/python3 -u
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, os.path 
import db, conv, admin
import lme_v1, lme_v2

debug=0
count_i=count_u=count_p=0
data = None

programa = (os.path.basename(sys.argv[0])).replace(".py", "")

if len(sys.argv) < 2:
	print("Uso:", sys.argv[0],"[-v] <arquivo a carregar>")
	sys.exit()
if sys.argv[1] == "-v":
	debug = 1
	nome_arq = sys.argv[2]
elif sys.argv[1] == "-vv":
	debug = 2
	nome_arq = sys.argv[2]
elif sys.argv[1] == "-vvv":
	debug = 3
	nome_arq = sys.argv[2]
else: nome_arq = sys.argv[1]


arquivo_log = admin.init(programa)

programa_id = db.obtem_id_programa(debug, programa)

if not programa_id:
	print("PROBLEMAS!!: programa", programa, "não encontrado na base de dados!")
	# enviar email
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa "+programa+" não encontrado na base de dados!");


print("Tratando arquivo",nome_arq)
try: 
	arq = open(nome_arq)
except IOError as e:
	print("Não foi possível abrir arquivo",nome_arq,"(",e,")")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")

# Ler arquivo todo
try: 
	linha = arq.read()
except IOError as e:
	print("Problemas o ler arquivo",nome_arq,"(",e,")")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Problemas o ler arquivo"+nome_arq+"("+e+")")
arq.close()

	
if linha.find("<h2 class=\"stocks-heading\">") >=0:
	print("Arquivo",nome_arq,"está no formato da versão 1")
	lme_v1.trata_arquivo(debug, arquivo_log, nome_arq, programa_id, linha)
elif linha.find("<div class=\"delayed-date left \">") >= 0:
	print("Arquivo",nome_arq,"está no formato da versão 2")
	lme_v2.trata_arquivo(debug, arquivo_log, nome_arq, programa_id, linha)
else:
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "ERRO: Arquivo "+nome_arq+" está num formato desconhecido")

