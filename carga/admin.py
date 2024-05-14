#!/usr/bin/python
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, os, time
import db

f = sys.stdout

def init(prog):
	data = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
	home = os.environ["HOME"]
	if (os.path.exists(home+"/log/carga")):
		diretorio = home+"/log/carga"
	else:	diretorio = "/tmp"
	print(diretorio+"/"+prog+"_"+data+".log")
	sys.stdout=open(diretorio+"/"+prog+"_"+data+".log","a")	
	print("Redirecionando stdout para "+diretorio+"/"+prog+"_"+data+".log")
	return diretorio+"/"+prog+"_"+data+".log"



def fim(arq):
	sys.stdout.flush()
	sys.stdout.close()
	sys.stdout = f


def sair(debug, prog, nome_arq, arquivo_log, data, inseridas, alteradas, iguais, erro):
	if erro: print(erro)
	else:
		print("\n\nFIM")
		print("\n\nCotações inseridas:", inseridas)
		print("Cotações atualizadas:", alteradas)
		print("Cotações iguais na base:", iguais)

	if data and prog:
		db.inserir_execucao(debug, prog, nome_arq, data, arquivo_log, inseridas, alteradas, iguais, erro)
	db.close()
	fim(arquivo_log)
#	fl = open(arquivo_log)
#	sys.stdout.writelines(fl.readlines())
#	fl.close()
	if erro is None:
		sys.exit(0)
	else:	sys.exit(1)
