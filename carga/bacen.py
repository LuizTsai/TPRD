#!/usr/bin/python -u
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, string
import db, conv, admin

moedas = {}

debug=0
count_i=count_u=count_p=0
data = None
lin=0

if len(sys.argv) < 2:
	print "Uso:", sys.argv[0],"[-v] <arquivo a carregar>"
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


arquivo_log = admin.init("bacen")
programa_id = db.obtem_id_programa(debug, "bacen")
if not programa_id:
        print "PROBLEMAS!!: programa bacen não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa bacen_agro não encontrado na base de dados!");


n = db.carrega_simbolos_moedas(debug, moedas)
if n<2:
	print "PROBLEMAS: foram carregadas menos de 2 moedas:", n

        admin.sair(debug, programa_id, nome_arq, arquivo_log, Data, count_i, count_u, count_p, "PROBLEMAS: foram carregadas menos de 2 moedas:"+str(n))

print "Há",n,"moedas cadastradas"

print "Tratando arquivo",nome_arq
try: 
	f = open(nome_arq)
except IOError, e:
	print "Não foi possível abrir arquivo",nome_arq,"(",e,")"
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")


def le_linha(arq):
	global lin
	lin = lin + 1
	linha = re.sub(r'\n$', "", arq.readline())
	if debug: print "("+str(lin)+"):", linha
	return linha


line = le_linha(f)

tline = re.match(r'(\d{2})/?(\d{2})/?(\d{4});', line)
if not tline:
	print "PROBLEMAS: não foi possível obter a data na primeira linha do arquivo:"
	print line
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: não foi possível obter a data na primeira linha do arquivo")

if debug>1: print "Match da data:", tline.groups()
data = tline.group(3)+"-"+tline.group(2)+"-"+tline.group(1)
print "Carregando cotações de moedas de", data

while line:	# loop de cotações
	tline = re.match(r'([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)', line)
	if not tline:
		print "PROBLEMAS: linha de dados inválida (não tem 8 campos separados  por ponto-e-vírgula):"
		print line
	else: 
		simbolo = conv.my_str(string.strip(tline.group(4)))
		if not moedas.has_key(simbolo):
			print "Símbolo", simbolo, "não está entre as moedas cadastradas, ignorando!"
		else:
			print "Símbolo", simbolo, "é da moeda", moedas[simbolo]	
			tipo = conv.my_str(string.strip(tline.group(3)))
			compra = conv.my_float(re.sub(r',', ".", string.strip(tline.group(5))))
			venda = conv.my_float(re.sub(r',', ".", string.strip(tline.group(6))))
			par_compra_o = conv.my_float(re.sub(r',', ".", string.strip(tline.group(7))))
			par_venda_o = conv.my_float(re.sub(r',', ".", string.strip(tline.group(8))))
	
			if tipo=="B":
				par_compra = par_compra_o
				par_venda = par_venda_o
			else:	# o valor no arquivo para moedas tipo A deve dividir o valor na moeda para obter a paridade em dolar... nós pretendemos sempre multiplicar!
				par_compra = conv.my_float(str(1 / par_compra_o)[0:12])
				par_venda = conv.my_float(str(1 / par_venda_o)[0:12])

			if debug>1:
				print "\tTipo", tipo
				print "\tCompra", compra
				print "\tVenda", venda
				print "\tParidade Compra (original/corrigida)", par_compra_o, par_compra
				print "\tParidade Venda (original/corrigida)", par_venda_o, par_venda
	
			# verificar se já há cotação da moeda na data na base
			cotacao = db.obtem_cotacao_moeda( debug, moedas[simbolo], data)
			if not cotacao:
				# inserir cotacao
				cotacao = db.inserir_cotacao_moeda( debug, moedas[simbolo], data, compra, venda, par_compra, par_venda)
				if cotacao: print "...cotação inserida"
				count_i+=1
			else:
				# já há cotação nesse dia
				# verificar se mudou
				if cotacao.compra != compra or cotacao.venda != venda or cotacao.par_compra != par_compra or cotacao.par_venda != par_venda:
					if cotacao.compra != compra: print ".....mudou compra", cotacao.compra, compra
					if cotacao.venda != venda: print ".....mudou venda", cotacao.venda, venda
					if cotacao.par_compra != par_compra: print ".....mudou par_compra", cotacao.par_compra, par_compra
					if cotacao.par_venda != par_venda: print ".....mudou par_venda", cotacao.par_venda, par_venda
					cotacao.compra = compra
					cotacao.venda = venda
					cotacao.par_compra = par_compra
					cotacao.par_venda = par_venda
	
					cotacao_nova = db.update_cotacao_moeda( debug, cotacao)
					if cotacao_nova: print "...cotação atualizzada"
					count_u+=1
				else: 
					print "...cotação idêntica já existe na base, ignorando"
					count_p+=1
	line = le_linha(f)
	while line and re.match(r'^\s*$', line) : line = le_linha(f)

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
