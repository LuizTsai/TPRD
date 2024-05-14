#!/usr/bin/python
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import MySQLdb
import sys, datetime, re, commands

debug = 0

if len(sys.argv) < 2:
        print "Uso:", sys.argv[0], "<programa de carga> [<data_inicial>] [ <data final>]"
        print "\tVerifica se há buracos na carga do programa no período indicado"
	print "\tUm buraco é um dia de semana que não tenha sido carregado"
        print "\t<programa de carga>: nome do programa (contido na tabela carga.Programa)"
        print "\t<data inicial>: início do período no formato AAAA-MM-DD"
        print "\t<data final>: fim do período no formato AAAA-MM-DD"
        sys.exit(1)


programa = sys.argv[1]
if len(sys.argv) > 2:
	data_i = sys.argv[2]
	if len(sys.argv) == 4:
		data_f = sys.argv[3]
	else:	data_f = datetime.date.today().isoformat()
else:	
	data_i = "1970-01-01"
	data_f = datetime.date.today().isoformat()

if not re.match(r'\d{4}-\d{2}-\d{2}', data_i):
	print "Erro: data inicial ("+data_i+") não está no formato AAAA-MM-DD"
	sys.exit(2)

if not re.match(r'\d{4}-\d{2}-\d{2}', data_f):
	print "Erro: data final ("+data_f+") não está no formato AAAA-MM-DD"
	sys.exit(3)

if data_i >= data_f:
	print "Erro: data inicial ("+data_i+") maior que data final ("+data_f+")"
	sys.exit(4)

conn = MySQLdb.connect(user='carga',passwd='p0k@', db='carga',charset='utf8');
cur = conn.cursor()

n = cur.execute("select idPrograma, nome from carga.Programa where nome=%s", (programa,))
if n<1:
	print "Erro: programa", programa, "não encontrado na base de dados"
	sys.exit(5)
row = cur.fetchone()
programa_id = int(row[0])

print "Verificando a existência de buracos na carga do programa", programa, "("+str(programa_id)+") no período", data_i, "a", data_f

dias = 0
acabou = False
while not acabou:
	data = commands.getoutput("date -d \""+data_i+" + "+str(dias)+"days\" +%F")
	if data>data_f:
		acabou = True
	else:
		dw = commands.getoutput("date -d \""+data+"\" +%u")
		dwt = commands.getoutput("date -d \""+data+"\" +%a")
		if dw=='6':
			# sábado
			dias = dias + 2
			ds = "sábado"
		elif dw=='7':
			# domingo
			dias = dias + 1
			ds = "domingo"
		else:
			ds = "dia de semana"
			dias = dias + 1
			# verificar carga nesse dia
			n = cur.execute("select data, cot_inseridas, cot_alteradas, cot_iguais, erro from carga.Execucao where programa_id=%s and data_carregada=%s and cot_inseridas+cot_alteradas+cot_iguais>0 order by data desc", (programa_id, data))
			if n<1:
				print data, dwt, "... sem carga de", programa
			else:
				row = cur.fetchone()
				if row[4]==1:
					print data, dwt, "... sem carga de", programa, "(última carga deu erro!)"
#		print ".........",data, dw, ds

