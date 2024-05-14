#!/usr/bin/python -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

import sys, re, subprocess, math
import db, conv, admin

mes_venc = {
		"JAN": "01",
		"FEB": "02",
		"MAR": "03",
		"APR": "04",
		"MAY": "05",
		"JUN": "06",
		"JUL": "07",
		"JLY": "07",
		"AUG": "08",
		"SEP": "09",
		"OCT": "10",
		"NOV": "11",
		"DEC": "12"
	}

debug=0
count_i=count_u=count_p=0
data = None
lin = 0 

ignorar = [ "RDCC", "QBRN", "QCFF", "QCOC", "QCOP", "QCRN", "QCTN", "QGAS", "QGLC", "QGLD", "QHEA", "QNAT", "QPLD", "QPLT", "QSIL", "QSUG", "WMNC", "XWHT", "XPLD", "XQCN", "XQSB", "XQSM", "XWMS", "YMNC" ]
novos = []

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


arquivo_log = admin.init("safex")
programa_id = db.obtem_id_programa(debug, "safex")
if not programa_id:
	print("PROBLEMAS!!: programa safex não encontrado na base de dados!")
	# enviar email
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa safex não encontrado na base de dados!");


print("Tratando arquivo",nome_arq)
try: 
	f = open(nome_arq)
except IOError as e:
	print("Não foi possível abrir arquivo",nome_arq,"(",e,")")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")	


def le_linha(arq):
	global lin
	lin = lin + 1
	linha = re.sub(r'\n$', "", arq.readline())
	if debug: print("("+str(lin)+"):", linha)
	return linha


# verificar linha de título 
line = le_linha(f)
if "Commodities Market Statistics for" in line:
	if debug: print("Arquivo OK")
	# obter data de referencia
	tdata = re.search(r'"Commodities Market Statistics for +([^"]+)"', line)
	if tdata:
		str_data = tdata.group(1)
		if debug>1: print("String de data:", str_data)
		data = subprocess.check_output(["date", "-d "+str_data," +%F"]).decode("utf-8")
		tdata = re.match(r'\d{4}-\d{2}-\d{2}', data)
		if tdata: print("Arquivo contém dados de", data)
		else:
			print("PROBLEMAS ao converter data \"",tdata,"\", saida do date:", data)
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS ao converter data \""+tdata+"\", saida do date: "+data)
	else:
		print("PROBLEMAS: Arquivo inválido: data de referência não encontrada na linha de título!")
		print(line)
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: data de referência não encontrada na linha de título!")
else:
	print("PROBLEMAS: Arquivo inválido: título \"Commodities Market Statistics for\" não encontrado!")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: título \"Commodities Market Statistics for\" não encontrado!")

# Verificar linha de cabeçalho 
line = le_linha(f)	# pular "Interest on Initial Margin"
line = le_linha(f)	# pular "Total Margin on Deposit"
line = le_linha(f)	# agora deve ser o cabeçalho
if "\"Contract Type\",\"Spot/Volatility \",\"Bid\",\"Offer\",\"M-t-M\",\"First\",\"Last\",\"High\",\"Low\",\"Deals\",\"Conts\",\"Value\",\"Open Interest \"" not in line:
	print("PROBLEMAS: Arquivo inválido: linha de cabeçalho não encontrada!")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: linha de cabeçalho não encontrada!")

# Inicializar estrutura de moedas
ret = db.carrega_moedas(debug)
if ret <= 2:
	print("PROBLEMAS na carga de moedas, carregou", ret,"moedas!")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de moedas, carregou "+str(ret)+" moedas!")

# Inicializar estrutura de unidades
ret = db.carrega_unidades(debug)
if ret <= 2:
	print("PROBLEMAS na carga de unidades, carregou", ret,"unidades!")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de unidades, carregou "+str(ret)+" unidades!")


# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line: # loop de símbolos/vencimentos
	tline = re.match(r'"([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)"',line)
	if not tline:
		# verificar se chegou nas linhas de totalização
		if (len(line)>3 and not re.search(r'Total|Market|Month|Rand', line)) and not re.match(r'^,*$', line):
			print("PROBLEMAS: linha de dados inválida (não tem 13 campos encapsulados em aspas duplas seguidos de vírgula):")
			print(line)
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de dados inválida (não tem 13 campos encapsulados em aspas duplas seguidos de vírgula)")
	else:
		if debug>1: print("Tupla da linha:", tline.groups())

		# verificar se é Futuro ou Opção
		print("Tratando", tline.group(1))
		tsimb = re.match(r'\d*\s*([A-Za-z]{3}) (\d{2}) (\w+)', tline.group(1))
		if not tsimb: print("...Opção, pulando")
		else:
			# Futuro
			if debug>1: print("Tupla (Venc,Simbolo):", tsimb.groups())
			simbolo = tsimb.group(3).strip()
			# procurar família do símbolo
			familia = db.obtem_familia_programa(debug, programa_id, simbolo)
			if not familia:
				try: 
					i = ignorar.index(simbolo)
					print("...Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar")
				except ValueError as e:
					try:
						i = novos.index(simbolo)
	       				except ValueError as e:
						novos.append(simbolo)
						print("AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", line)
			else:
				print("...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8'))
				db.inserir_programa_familia(debug, programa_id, familia)
				# Obter vencimento
				mes = mes_venc[tsimb.group(1).upper()]
				ano = "20"+tsimb.group(2)
				venc = ano+"-"+mes
				# procurar Ativo
				ativo = db.obtem_ativo(debug, familia, venc)
				if not ativo: 
					# ainda não há ativo com o vencimento, criar!
					print("...Vencimento", venc, "não encontrado, inserir Ativo")
					ativo = db.inserir_ativo(debug, familia, venc, None)
					if not ativo: print("!!!!! PROBLEMAS ao criar ativo, para vencimento", venc)
				if ativo: 
					print("...Vencimento", venc, "Ativo", ativo.id)
					#Parsear o resto dos campos
#1="Contract Type",2="Spot/Volatility ",3="Bid",4="Offer",5="M-t-M",6="First",7="Last",8="High",9="Low",10="Deals",11="Conts",12="Value",13="Open Interest "
					settle = conv.my_float(tline.group(5))
					abertura = conv.my_float(tline.group(6))
					last = conv.my_float(tline.group(7))
					high = conv.my_float(tline.group(8))
					low = conv.my_float(tline.group(9))
					negocios = conv.my_int(tline.group(10))
					vol_contratos = conv.my_long(tline.group(11))
					vol_financeiro= conv.my_float(tline.group(12))
					open_int = conv.my_long(tline.group(13))

					casas = conv.obtem_casas_decimais(debug, ativo.tick_size)
					if debug>1: print("Tick size:", ativo.tick_size, "Casas decimais:", casas)

					if vol_contratos and vol_financeiro:
						fator_conv_unidade = conv.fator_conversao_unidade(debug, ativo.unidade_contrato_principal, ativo.unidade_cotacao)
						if fator_conv_unidade:
							fator_conv_moeda = conv.fator_conversao_moeda(debug, ativo.moeda_cotacao, ativo.moeda_cotacao)
							if fator_conv_moeda:
								vwap = ( vol_financeiro / vol_contratos / ativo.qtdade_contrato_principal / fator_conv_unidade * fator_conv_moeda )
								if debug > 1: print(".... (vol_finan, vol_contr, qty_contrato_prin, fator_conv_unid, fator_conv_moeda) =", vol_financeiro, vol_contratos, ativo.qtdade_contrato_principal, fator_conv_unidade, fator_conv_moeda)
								vwap = conv.arredonda_casas(debug, vwap, casas)
							else:
								print("!!!!!! Problemas ao obter fator de conversão de moedas ( 7", ativo.moeda_cotacao, ")")
								vwap = None
						else:
							print("!!!!!! Problemas ao obter fator de conversão de unidades (", ativo.unidade_contrato_principal, ativo.unidade_cotacao, ")")
							vwap = None
					else: vwap = None


					if debug>1:
						print("\tdata:", data)
						print("\tsímbolo:", simbolo)
						print("\tvencimento:", venc)
						print("\tvolume financeiro:", vol_financeiro)
						print("\tcontratos em aberto:", open_int)
						print("\tnegócios:", negocios)
						print("\tvolume de contratos:", vol_contratos)
						print("\tabertura:", abertura)
						print("\tmínimo:", low)
						print("\tmáximo:", high)
						print("\tvwap:", vwap)
						print("\túltimo:", last)
						print("\tajuste (settle):", settle)

					# verificar se há cotação do ativo para a data 
					cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
					if not cotacao:
						# inserir cotação
						cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
						if cotacao: print("......cotação inserida"
						count_i += 1
					else: 	# já há cotação nesse dia
						# verificar se mudou...
						if (abertura and abertura>0 and cotacao.abertura != abertura) or (last and last>0 and cotacao.ultimo != last) or (settle and settle>0 and cotacao.fechamento != settle) or (vwap and vwap>0 and cotacao.vwap != vwap) or (high and high>0 and cotacao.maximo != high) or (low and low>0 and cotacao.minimo != low) or (negocios and negocios>0 and cotacao.negocios != negocios) or (vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (vol_financeiro and vol_financeiro>0 and abs(cotacao.volume_financeiro - vol_financeiro)>ativo.tick_size) or (open_int and open_int>0 and cotacao.contratos_aberto != open_int):
							if abertura and abertura>0 and cotacao.abertura != abertura: print(".......mudou abertura",(cotacao.abertura,abertura))
							if last and last>0 and cotacao.ultimo != last: print(".......mudou ultimo",(cotacao.ultimo,last))
							if settle and settle>0 and cotacao.fechamento != settle: print(".......mudou fechamento",(cotacao.fechamento,settle))
							if vwap and vwap>0 and cotacao.vwap != vwap: print(".......mudou vwap",(cotacao.vwap,vwap))
							if high and high>0 and cotacao.maximo != high: print(".......mudou maximo",(cotacao.maximo,high))
							if low and low>0 and cotacao.minimo != low: print(".......mudou minimo",(cotacao.minimo,low))
							if negocios and negocios>0 and cotacao.negocios != negocios: print(".......mudou negocios",(cotacao.negocios,negocios))
							if vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print(".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos))
							if vol_financeiro and vol_financeiro>0 and abs(cotacao.volume_financeiro - vol_financeiro)>ativo.tick_size: print(".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro))
							if open_int and open_int>0 and cotacao.contratos_aberto != open_int: print(".......mudou contratos_aberto",(cotacao.contratos_aberto,open_int))
							# mudou, atualizar cotação
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
							if cotacao_nova: print("......cotação atualizada")
							count_u += 1
						else: 
							print("......cotação idêntica já existe na base, ignorando")
							count_p += 1
	line = le_linha(f)

print("FIM")

if len(novos)>0:
	print("Símbolos novos detectados:", novos)

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
