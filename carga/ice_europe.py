#!/usr/bin/python -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, string, datetime
import db, conv, admin


debug=0
count_i=count_u=count_p=0
data = None
lin = 0

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

ignorar = [ ] 

novos = []
linha_mercadoria= ""
line = ""

secao = ""

def datahora():
	return datetime.datetime.utcnow().isoformat()	
	
def verificar_linhas_cabecalho(arq, linha):
	global versao
	line = linha
	while line and (re.match(r'\s*$', line) or re.match(r'^\s+DAILY PRICE RANGE\s+SETTLE\s+', line) or re.match(r'^\s+COMMODITY\s+CONTRACT', line) or re.match(r'^\s+NAME\s+MONTH', line) or re.match(r'^\s+TOTAL\s+BLOCK', line) or re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+(ADJ\*\*)*\s+EFP\s+EFS', line) or re.match(r'^\s+VOLUME\s+VOLUME', line)) or re.sub(r'\s*$', "", line) == re.sub(r'\s*$', "", linha_mercadoria):	
		if re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+ADJ\*\*\s+EFP\s+EFS', line): versao=1
		if re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+EFP\s+EFS', line): versao=2

		line = le_arq(arq)	# pular linhas em branco ou repetições das linhas de cabeçalho
	return(line)


def le_arq(arq):
	global lin, debug
	linha = arq.readline()
	lin = lin + 1
	if linha: linha = re.sub(r'\n$', " ", linha)
	if debug>2: print "'"+linha+"'"
	return linha


def le_linha(arq, pular_cab):
	global debug, secao
	linha = le_arq(arq)
	if pular_cab:
		acabou = False
		while not acabou and linha:
			linha = verificar_linhas_cabecalho(arq, linha)
			if "Futures Daily Market Report for" in linha:
				while "Futures Daily Market Report for" in linha:
					secao = linha
					linha = le_arq(arq)	
				# pular linha de data que vem em seguida
				while linha and re.match(r'^\d{2}-[A-Z]{3}-\d{4}',linha): linha = le_arq(arq)
			else:
				acabou = True	
	if debug: print "("+str(lin)+")",linha
	return linha



def tratar_vencimento(familia, tline):
	global count_i, count_u, count_p, lin
	# só tratar se tivermos encontrado família para o símbolo, senão ignorar
	if familia: # tratar vencimento
		if debug>1: print "--Tratando vencimento", datahora()
		# Simb, Venc, Open, High, Low, Close, Settle, Change, Vol, OI, Change, EFP, EFS, BLOCK_VOL, SPREAD_VOL
		v = re.sub(r'-+', "", tline.group(2))
		venc = "20"+conv.my_str(v[3:5])+"-"+mes_venc[conv.my_str(v[0:3])]
		if len(tline.group(7))>0 and ((len(tline.group(3))>0 and len(tline.group(4))>0 and len(tline.group(5))>0 and len(tline.group(6))>0) or (len(tline.group(3))==0 and len(tline.group(4))==0 and len(tline.group(5))==0 and len(tline.group(6))==0)) and (len(tline.group(12))>0 and len(tline.group(13))>0 and len(tline.group(14))>0 and len(tline.group(15))>0):
                        abertura = conv.my_float(string.strip(re.sub(r',',"",tline.group(3))))
                        high = conv.my_float(string.strip(re.sub(r',',"",tline.group(4))))
                        low = conv.my_float(string.strip(re.sub(r',',"",tline.group(5))))
                        last = conv.my_float(string.strip(re.sub(r',',"",tline.group(6))))
                        settle = conv.my_float(string.strip(re.sub(r',',"",tline.group(7))))
                        vol = conv.my_long(string.strip(re.sub(r',',"",tline.group(9))))
                        open_int = conv.my_long(string.strip(re.sub(r',',"",tline.group(10))))
                else:
                        n = 0
                        for i in tline.groups():
                                if len(i)>0:
                                        n=n+1
                        if n==11:
                                tl = string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')
                                abertura = None
                                high = None
                                low = None
                                last = None
                                settle = conv.my_float(string.strip(re.sub(r',',"",tl[2])))
                                vol = conv.my_long(string.strip(re.sub(r',',"",tl[4])))
                                open_int = conv.my_long(string.strip(re.sub(r',',"",tl[5])))
                        elif n==9:
                                tl = string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')
                                abertura = None
                                high = None
                                low = None
                                last = None
                                settle = conv.my_float(string.strip(re.sub(r',',"",tl[2])))
                                vol = None
                                open_int = None
                        elif n==10:
                                tl = string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')
                                abertura = None
                                high = None
                                low = None
                                last = None
                                settle = conv.my_float(string.strip(re.sub(r',',"",tl[2])))
                                vol = conv.my_long(string.strip(re.sub(r',',"",tl[4])))
                                open_int = None
                        else:
                                if debug: print "PROBLEMAS: tupla da linha", lin,"não tem todas as colunas e os \"buracos\" não estão nos lugares normais"
                                admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: tupla da linha "+str(lin)+" não tem todas as colunas e os \"buracos\" não estão nos lugares normais")

		vwap = negocios = vol_financeiro = None

		if debug>1:
			print "\tdata:", data
			print "\tsímbolo:", simbolo
			print "\tvencimento:", venc
			print "\tvolume financeiro:", vol_financeiro
			print "\tcontratos em aberto:", open_int
			print "\tnegócios:", negocios
			print "\tvolume de contratos:", vol
			print "\tabertura:", abertura
			print "\tmínimo:", low
			print "\tmáximo:", high
			print "\tvwap:", vwap
			print "\túltimo:", last
			print "\tajuste (settle):", settle
		elif debug: print "venc:",venc,"settle:",settle,"volume:",vol,"open_interest:",open_int

		if not settle:
			print "!!!!AVISO: fechamento sem valor! (linha="+str(lin)+")",simbolo,venc
		else:
			# procurar Ativo com o vencimento
			ativo = db.obtem_ativo(debug, familia, venc)
			if not ativo:
				# ainda não há Ativo com o vencimento, criar!
				print "...Vencimento", venc, "não encontrado, inserir Ativo"
				ativo = db.inserir_ativo(debug, familia, venc, None)
				if not ativo:
					print "!!!!!!PROBLEMAS ao criar ativo para vencimento",venc,"linha=",lin,"simbolo=",simbolo
			if ativo: 
				print datahora(), "...Vencimento",venc,"Ativo", ativo.id
				# verificar se já há cotação do ativo para a data na base
				cotacao = db.obtem_cotacao_ativo( debug, ativo, data)
				if not cotacao:
					# inserir cotação
					cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol, vol_financeiro, open_int)
					if cotacao: print "......Cotação inserida"
					count_i += 1
				else:	# já há cotação nesse dia
					# verificar se mudou...
					if cotacao.abertura != abertura or cotacao.ultimo != last or cotacao.fechamento != settle or cotacao.vwap != None or cotacao.maximo != high or cotacao.minimo != low or cotacao.negocios != None or cotacao.volume_contratos != vol or cotacao.volume_financeiro != None or cotacao.contratos_aberto != open_int:
						if cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
						if cotacao.ultimo != last: print ".......mudou ultimo",(cotacao.ultimo,last)
						if cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
						if cotacao.vwap != None: print ".......mudou vwap",(cotacao.vwap,vwap)
						if cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
						if cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
						if cotacao.negocios != None: print ".......mudou negocios",(cotacao.negocios,negocios)
						if cotacao.volume_contratos != vol: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol)
						if cotacao.volume_financeiro != None: print ".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro)
						if cotacao.contratos_aberto != open_int: print ".......mudou contratos_aberto",(cotacao.contratos_aberto,open_int)
						# mudou, atualizar
						cotacao.abertura = abertura
						cotacao.ultimo = last
						cotacao.fechamento = settle
						cotacao.vwap = vwap
						cotacao.maximo = high
						cotacao.minimo = low
						cotacao.negocios = negocios
						cotacao.volume_contratos = vol
						cotacao.volume_financeiro = vol_financeiro
						cotacao.contratos_aberto = open_int
						cotacao_nova = db.update_cotacao_ativo(debug, ativo, cotacao)
						if cotacao_nova: print "......Cotação atualizada"
						count_u += 1
					else: 
						print "......Cotação idêntica já existe na base, ignorando"
						count_p += 1


#===========================================================

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

arquivo_log = admin.init("ice_europe")
programa_id = db.obtem_id_programa(debug, "ice_europe")
if not programa_id:
        print "PROBLEMAS!!: programa ice_europe não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa ice_europe não encontrado na base de dados!");


print datahora(), "Tratando arquivo",nome_arq
try: 
	f = open(nome_arq)
except IOError, e:
	print "Não foi possível abrir arquivo",nome_arq,"(",e,")"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")


# verificar linha de título 
line = le_linha(f, 0)
if "Futures Daily Market Report for" in line:
	if debug: print "Arquivo OK"
	# obter data de referencia
	line = le_linha(f, 0)
	tdata = re.search(r'^(\d+)-([A-Z]+)-(\d+)', line)
	if tdata:
		dia = tdata.group(1)
		mes = mes_venc[tdata.group(2)]
		ano = tdata.group(3)
		data = ano+"-"+mes+"-"+dia
		print "Arquivo contém dados de "+dia+"/"+mes+"/"+ano
	else:
		print "PROBLEMAS: Arquivo inválido: data de referência não encontrada após linha de título!"
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Arquivo inválido: data de referência não encontrada após linha de título")
else:
	print "PROBLEMAS: Arquivo inválido: título \"Futures Daily Market Report for\" não encontrado!"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Arquivo inválido: título \"Futures Daily Market Report for\" não encontrado")


# Tratar blocos de símbolos (famílias)
line = le_linha(f, 1)
while line and not re.match(r'NOTE: The information contained in this report is compiled for the convenience of subscribers', line): # loop de blocos
	print  "----Loop Principal", datahora(), secao	####
	# linha de mercadoria não tem o símbolo
	linha_mercadoria = string.strip(line)
	line = le_linha(f,1 )
	tsimb=re.match(r'^\s*(\S{1,3})\s', line)
	if not tsimb:
		print "PROBLEMAS: símbolo não encontrado na linha de mercadoria:", line
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Símbolo não encontrado na linha de mercadoria")
	simbolo = tsimb.group(1)
	# procurar familia do simbolo
	print "Seção:", secao
	familia = None
	if re.match(r'Futures Daily Market Report for Commodities', secao):
		familia = db.obtem_familia(debug, 11, simbolo)	# ICE-EUR London
		if not familia:
			familia = db.obtem_familia(debug, 6, simbolo)	# ICE-EUR 

	if not familia:
		try:
			i = ignorar.index(simbolo)
			print "...Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar"
		except ValueError, e:
			try:
				i = novos.index(simbolo)
			except ValueError, e:
				novos.append(simbolo)
				#print "AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", linha_mercadoria
				print "...Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", linha_mercadoria
	else:
		print "...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
		db.inserir_programa_familia(debug, programa_id, familia) 
		
	if not familia:
		# pular linhas até a próxima linha de mercadoria
		#while line and not re.match(r'^\S{3}-', line):
		while line and not re.match(r'^Totals for '+simbolo+'\:', line):
			line = le_linha(f, 1)
		if line: line = le_linha(f, 1)
	else:

#	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco
#
	# loop de linhas de dados (vencimentos)
#		if versao==1:
#			tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+N/A', line)
#		else:
#	 		tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
 		tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
		while tline:
#		print datahora(), "====Loop de vencimentos", datahora() ####
			if debug>1: print "Tupla da linha:", tline.groups()
			n = 0
			for i in tline.groups():
				if len(i)>0:
					n=n+1
			if n != len(string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')):
				print "PROBLEMAS: Linha", lin, "tem", len(string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')), "dados, mas match retornou apenas", n
                	        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Linha "+str(lin)+" tem "+str(len(string.split(re.sub(r'\s*$', '', re.sub(r'^\s*', '', re.sub(r'\s+', ' ', line))), ' ')))+" dados, mas match retornou apenas "+str(n))

			if simbolo != string.strip(tline.group(1)):
				print "PROBLEMAS: linha tem símbolo diferente da mercadoria ("+simbolo+"):", string.strip(tline.group(1))
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Linha tem símbolo diferente da mercadoria ("+simbolo+"): "+string.strip(tline.group(1)))
#			simbolo = string.strip(tline.group(1))
#			# procurar familia do simbolo
#			familia = db.obtem_familia_programa(debug, programa_id, simbolo)
#			if not familia: 
#				try:
#					i = ignorar.index(simbolo)
#					print "...Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar"
#				except ValueError, e:
#					try:
#						i = novos.index(simbolo)
#					except ValueError, e:
#						novos.append(simbolo)
#						#print "AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", linha_mercadoria
#						print "Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", linha_mercadoria
#			else:
#				print "...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
			if familia:
				tratar_vencimento(familia, tline)
			line = le_linha(f, 1)
#		while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco
			if re.match(r'\s*Totals for \S*:\s+\S+\s+\S+\s+\S*\s+\S*\s+\S+\s+\S+\s*', line):
				tline = None
#			elif versao==1:
#				tlins = re.match(r'^\s*('+simbolo+r')\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+N/A', line)
			else:
 				tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)

			if debug>1:
				if not tline: print "Saiu do loop de vencimentos"
#	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco

		print "--------------------------------------" ####
		# verificar linha de totais
		if re.match(r'\s*Totals for '+simbolo+':', line):
			if debug>1: print "Achou linha de Totais"
			line = le_linha(f, 1)
#	else:	
#		print "PROBLEMAS: linha de totais não encontrada no final do bloco"
#               admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "linha de totais não encontrada no final do bloco")		
#	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco


print datahora(), "FIM"

#if len(novos)>0:
#        print "Símbolos novos detectados:", novos
admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)

