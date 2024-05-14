#!/usr/bin/python -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



###### -*- coding: utf8 -*-

import sys, re, string, math
import db, conv, admin

debug=0
count_i=count_u=count_p=0
data = None
lin = 0 

ignorar = [ "DHAANYA" ]
novos = []

moeda_arq = { "rs":7, "rs.":7 }
unidade_arq = { "lot":None, "quintal":19, "barrel":14, "barrels":14, "kg":1, "kgs":1, "10kgs":20, "gms":2, "10gms":24, "40kgs":27, "20kgs":26, "mt":5, "100gms":28, "bale":22, "bales":22 } 

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


arquivo_log = admin.init("ncdex")
programa_id = db.obtem_id_programa(debug, "ncdex")
if not programa_id:
        print "PROBLEMAS!!: programa ncdex não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa ncdex não encontrado na base de dados!");


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


def trata_data(s):
	ts = re.match(r'(\d+)/(\d+)/(\d+)', string.strip(s))
	if ts:
		ano = string.zfill(ts.group(3), 4)
		mes = string.zfill(ts.group(1), 2)
		dia = string.zfill(ts.group(2), 2)
		return ano+"-"+mes+"-"+dia
	else:
		print "PROBLEMAS: data inválida:",s
		return None


# verificar linha de cabeçalho
line = le_linha(f)
if not re.match(r'"Symbol *","Expiry *Date *","Commodity *","Ex-[Bb]asis *[Dd]elivery *[Cc]entre *","Price *[Uu]nit *","Previous *[Cc]losing *[Pp]rice *","Opening *[Pp]rice *","High *[Pp]rice *","Low *[Pp]rice *","Closing *[Pp]rice *","Quantity *[Tt]raded *[Tt]oday *","Measure *","No *[Oo]f *[Tt]rades *","Traded* *[Vv]alue *[Ii]n *[Ll]acs *","Open *[Ii]nterest *([Ii]n *[Qq]uantity *){0,1}","Last *[Tt]raded* *[Dd]ate *",', line):
	print "PROBLEMAS: Arquivo inválido, linha de cabeçalho não encontrada"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido, linha de cabeçalho não encontrada")


line = le_linha(f)
# obter data do pregão
tline = re.match(r'"DHAANYA\s*","([^"]+)",', line)
if tline:
	data = trata_data(tline.group(1))
	if not data:
		print "PROBLEMAS: data do pregão inválida:", tline.group(1)
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: data do pregão inválida:"+ tline.group(1))
	print "Pregão de",data
else:
	print "PROBLEMAS ao obter data do pregão da primeira linha de dados (deveria se o índice DHAANYA):"
	print line
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS ao obter data do pregão da primeira linha de dados (deveria se o índice DHAANYA)")

# Inicializar estrutura de moedas
ret = db.carrega_moedas(debug) 
if ret <= 2:
	print "PROBLEMAS na carga de moedas, carregou", ret,"moedas!"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de moedas, carregou "+str(ret)+" moedas!")

# Inicializar estrutura de unidades
ret = db.carrega_unidades(debug) 
if ret <= 2:
	print "PROBLEMAS na carga de unidades, carregou", ret,"unidades!"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de unidades, carregou "+str(ret)+" unidades")

while line:	# loop de simbolos
	tline = re.match(r'"([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)",',line)
	if not tline:
		if (len(line)>3 and not re.search(r'TRADE', line)) and not (re.match(r'^,*$',string.strip(re.sub(r'\"\s*\"',"", line)))):
			print "PROBLEMAS: linha de dados inválida (não tem 16 campos encapsulados em aspas duplas seguidos de vírgula):"
			print line
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de dados inválida (não tem 16 campos encapsulados em aspas duplas seguidos de vírgula)")
	else:
		if debug>1:
			print tline.groups()
		simbolo = string.strip(tline.group(1))
		
		# procurar família do símbolo
		familia = db.obtem_familia_programa(debug, programa_id, simbolo)
		if not familia:
                	try:
                        	i = ignorar.index(simbolo)
	                        print "...Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar"
        	        except ValueError, e:
                	        try:
                        	        i = novos.index(simbolo)
	                        except ValueError, e:
        	                        novos.append(simbolo)
                	                print "AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", line
		else: 
			print "...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
			db.inserir_programa_familia(debug, programa_id, familia)
			# procurar Ativo com o vencimento
			venc = trata_data(tline.group(2))
			if not venc:
				print "PROBLEMAS: Data de Vencimento inválida:", string.strip(tline.group(2))
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Data de Vencimento inválida: "+string.strip(tline.group(2)))
			ativo = db.obtem_ativo(debug, familia, venc[0:7])
			if not ativo:
				# ainda não há Ativo com o vencimento, criar!
				print "...Vencimento", venc, "não encontrado, inserir Ativo"
				data_vencimento = venc
				ativo = db.inserir_ativo(debug, familia, venc[0:7], data_vencimento)
				if not ativo:
					print "!!!!!!PROBLEMAS ao criar ativo para vencimento",venc
			if ativo: 
				print "...Vencimento",venc,"Ativo", ativo.id
				# Parsear o resto dos campos
#1="Symbol",2="Expiry Date ",3="Commodity",4="Ex-basis delivery centre",5="Price unit",6="Previous Closing Price ",7="Opening Price ",8="High Price ",9="Low Price ",10="Closing Price ",11="Quantity Traded Today",12="Measure",13="No of Trades",14="Traded Value in lacs",15="Open Interest In Quantity",16="LastTradeDate",
				price_unit = string.split(conv.my_str(string.strip(tline.group(5))), "/")		
				abertura = conv.my_float(string.strip(tline.group(7)))		
				high = conv.my_float(string.strip(tline.group(8)))		
				low = conv.my_float(string.strip(tline.group(9)))		
				last = conv.my_float(string.strip(tline.group(10)))		
				settle = conv.my_float(string.strip(tline.group(10)))		
				qtty = conv.my_long(string.strip(tline.group(11)))
				unidade_vol = conv.my_str(string.strip(tline.group(12)))
				negocios = conv.my_int(string.strip(tline.group(13)))		
				vol_financeiro = conv.my_float(string.strip(tline.group(14)))		
				open_int = conv.my_long(string.strip(tline.group(15)))

				# verificar unidades
				if debug>1: print "Unidade do preço:", price_unit
				try:
					moeda_preco = moeda_arq[string.lower(price_unit[0])]
				except KeyError:
					print "PROBLEMAS: moeda em price unit("+price_unit[0]+") desconhecida, linha", lin
				try: 
					unidade_preco = unidade_arq[string.lower(price_unit[1])]	
				except KeyError:
					print "PROBLEMAS: unidade em price unit("+price_unit[1]+") desconhecida, linha", lin

				if moeda_preco != ativo.moeda_cotacao:
					print "PROBLEMAS: moeda em price_unit ("+price_unit[0], moeda_preco,"diferente da moeda de cotação do ativo ("+ativo.moeda_cotacao+"), linha", lin
				if unidade_preco != ativo.unidade_cotacao:
					print "PROBLEMAS: unidade em price_unit ("+price_unit[1], unidade_preco,"diferente da unidade de cotação do ativo ("+ativo.unidade_cotacao+"), linha", lin
				if debug>1: print "Unidade da Quantidade Negociada:", unidade_vol
				try:
					unidade_qtty = unidade_arq[string.lower(unidade_vol)]
				except KeyError:
					print "PROBLEMAS: unidade da quantidade("+unidade_vol+") desconhecida"

				if unidade_qtty and unidade_qtty != ativo.unidade_contrato_principal:
					print "PROBLEMAS: unidade da quantidade ("+unidade_vol, unidade_qtty,"diferente da unidade principal do contrato ("+ativo.unidade_contrato_principal+"), linha", lin

				# corrigir valores
				if qtty:
					if re.match(r'[Ll][Oo][Tt]', unidade_vol):
						# quantidade em contratos
						vol_contratos = qtty 	
					else:
						# quantidade na unidade do contrato
						vol_contratos = long(qtty / ativo.qtdade_contrato_principal)	
				else: vol_contratos = None
				if open_int: 
					if re.match(r'[Ll][Oo][Tt]', unidade_vol):
						# quantidade em contratos
						open_int = open_int
					else:
						open_int = open_int / ativo.qtdade_contrato_principal	# open_interest vem em quantidade

				casas = conv.obtem_casas_decimais(debug, ativo.tick_size)
				if debug>1: print "Tick size:", ativo.tick_size, "Casas decimais:", casas

				if vol_financeiro: 
					vol_financeiro = vol_financeiro * 100000 # volume vem em lakhs... 1 lakh = 100.000
					vol_financeiro = conv.arredonda_casas(debug, vol_financeiro, casas)
				if vol_contratos and vol_financeiro:
					fator_conv_unidade = conv.fator_conversao_unidade(debug, ativo.unidade_contrato_principal, ativo.unidade_cotacao)
					if fator_conv_unidade:
						fator_conv_moeda = conv.fator_conversao_moeda(debug, 7, ativo.moeda_cotacao)
						if fator_conv_moeda:
							vwap = ( vol_financeiro / vol_contratos / ativo.qtdade_contrato_principal / fator_conv_unidade * fator_conv_moeda ) 
							if debug > 1: print ".... (vol_finan, vol_contr, qty_contrato_prin, fator_conv_unid, fator_conv_moeda) =", vol_financeiro, vol_contratos, ativo.qtdade_contrato_principal, fator_conv_unidade, fator_conv_moeda
							vwap = conv.arredonda_casas(debug, vwap, casas)
						else:
							print "!!!!!! Problemas ao obter fator de conversão de moedas ( 7", ativo.moeda_cotacao, ")"
							vwap = None
					else:
						print "!!!!!! Problemas ao obter fator de conversão de unidades (", ativo.unidade_contrato_principal, ativo.unidade_cotacao, ")"
						vwap = None
				else: vwap = None
	# Verificar se unidades batem com as cadastradas no ativo
	# Later...

				print "...Settle:", settle,"Volume:", vol_contratos
				if debug > 1:
					print "\tdata:", data
					print "\tsímbolo:", simbolo 
					print "\tvencimento:", venc
					print "\tvolume financeiro:", vol_financeiro
					print "\tcontratos em aberto:", open_int
					print "\tnegócios:", negocios
					print "\tvolume de contratos:", vol_contratos
					print "\tabertura:", abertura
					print "\tmínimo:", low
					print "\tmáximo:", high
					print "\tvwap:", vwap
					print "\túltimo:", last
					print "\tajuste (settle):", settle
	
				# verificar se já há cotação do ativo para a data na base
				cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
				if not cotacao:
					# inserir cotação
					cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
					if cotacao: print "......cotação inserida"
					count_i += 1
				else:	# já há cotação nesse dia
					# verificar se mudou...
					if (abertura>0 and cotacao.abertura != abertura) or (last>0 and cotacao.ultimo != last) or (settle>0 and cotacao.fechamento != settle) or (vwap>0 and cotacao.vwap != vwap) or (high>0 and cotacao.maximo != high) or (low>0 and cotacao.minimo != low) or (negocios>0 and cotacao.negocios != negocios) or (vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (vol_financeiro>0 and abs(cotacao.volume_financeiro - vol_financeiro)>ativo.tick_size) or (open_int>0 and cotacao.contratos_aberto != open_int):
						if abertura>0 and cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
						if last>0 and cotacao.ultimo != last: print ".......mudou ultimo",(cotacao.ultimo,last)
						if settle>0 and cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
						if vwap>0 and cotacao.vwap != vwap: print ".......mudou vwap",(cotacao.vwap,vwap)
						if high>0 and cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
						if low>0 and cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
						if negocios>0 and cotacao.negocios != negocios: print ".......mudou negocios",(cotacao.negocios,negocios)
						if vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos)
						if vol_financeiro>0 and abs(cotacao.volume_financeiro - vol_financeiro)>ativo.tick_size: print ".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro)
						if open_int>0 and cotacao.contratos_aberto != open_int: print ".......mudou contratos_aberto",(cotacao.contratos_aberto,open_int)
						# mudou, atualizar
						cotacao.abertura = abertura
						cotacao.ultimo = last
						cotacao.fechamento = settle
						cotacao.vwap = vwap
						cotacao.maximo = high
						cotacao.minimo = low
						cotacao.negocios = negocios
						cotacao.volume_contratos = vol_contratos
						cotacao.volume_financeiro = vol_financeiro
						cotacao.contratos_aberto = open_int
						cotacao_nova = db.update_cotacao_ativo(debug, ativo, cotacao)
						if cotacao_nova: print "......cotação atualizada"
						count_u += 1
					else: 
						print "......cotação idêntica já existe na base, ignorando"
						count_p += 1
	line = le_linha(f)

print "FIM"

if len(novos)>0:
        print "Símbolos novos detectados:", novos


admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
