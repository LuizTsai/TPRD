#!/usr/bin/python -u
# coding=UTF8

import sys, re, string
import db, conv, admin


debug=0
count_i=count_u=count_p=0
data = None

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

line = ""

def verificar_linhas_cabecalho():
	global line, versao
	# o cabeçalho tem 6 linhas e pode "recomeçar" se houver uma quebra de página no PDF original no meio dele
#	if not re.match(r'^\s+DAILY PRICE RANGE\s+SETTLE\s+', line):
#		print "PROBLEMAS: Arquivo inválido, primeira linha de cabeçalho de bloco não encontrada"
#		print line
#		return(2)
#	line = le_linha(f)
#	if not re.match(r'^\s+COMMODITY\s+CONTRACT', line):
#		if verificar_linhas_cabecalho() != 0:
#			print "PROBLEMAS: Arquivo inválido, segunda linha de cabeçalho de bloco não encontrada"
#			print line
#			return(2)
#		else: return(0)
#	line = le_linha(f)
#	if not re.match(r'^\s+NAME\s+MONTH', line):
#		if verificar_linhas_cabecalho() != 0:
#			print "PROBLEMAS: Arquivo inválido, terceira linha de cabeçalho de bloco não encontrada"
#			print line
#			return(2)
#		else: return(0)
#	line = le_linha(f)
#	if not re.match(r'^\s+TOTAL\s+BLOCK', line):
#		if verificar_linhas_cabecalho() != 0:
#			print "PROBLEMAS: Arquivo inválido, quarta linha de cabeçalho de bloco não encontrada"
#			print line
#			return(2)
#		else: return(0)
#	line = le_linha(f)
#	if not re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+(ADJ\*\*)*\s+EFP\s+EFS', line):
#		if verificar_linhas_cabecalho() != 0:
#			print "PROBLEMAS: Arquivo inválido, quinta linha de cabeçalho de bloco não encontrada"
#			print line
#			return(2)
#		else: return(0)
#	line = le_linha(f)
#	if not re.match(r'^\s+VOLUME\s+VOLUME', line):
#		if verificar_linhas_cabecalho() != 0:
#			print "PROBLEMAS: Arquivo inválido, sexta linha de cabeçalho de bloco não encontrada"
#			print line
#			return(2)
#		else: return(0)
#	line = le_linha(f)
	while line and (re.match(r'\s*$', line) or re.match(r'^\s+ELECTRONIC DAILY PRICE RANGE\s+SETTLE\s+VOLUME AND OI TOTALS', line) or re.match(r'^\s+COMMODITY\s+CONTRACT', line) or re.match(r'^\s+NAME\s+MONTH', line) or re.match(r'^\s+TOTAL\s+BLOCK\s', line) or re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+(ADJ\*\*)*\s+EFP\s+EFS', line) or re.match(r'^\s+VOLUME\s+VOLUME', line) or re.match(r'^Agriculture', line)):	
		if re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+ADJ\*\*\s+EFP\s+EFS', line): versao=1
		if re.match(r'^\s+OPEN\#\s+HIGH\s+LOW\s+CLOSE\#\s+PRICE\s+CHANGE\s+OI\s+CHANGE\s+EFP\s+EFS', line): versao=2

		line = le_linha(f)	# pular linhas em branco ou repetições das linhas de cabeçalho
	
	return(0)


def tratar_vencimento(familia, tline):
	global count_i, count_u, count_p
	# só tratar se tivermos encontrado família para o símbolo, senão ignorar
	if familia: # tratar vencimento
		# Simb, Venc, Open, High, Low, Close, Settle, Change, Vol, OI, Change, EFP, EFS, BLOCK_VOL, SPREAD_VOL
		v = re.sub(r'-+', "", tline.group(2))
		venc = "20"+conv.my_str(v[3:5])+"-"+mes_venc[conv.my_str(v[0:3])]
		abertura = conv.my_float(string.strip(re.sub(r',',"",tline.group(3))))
		high = conv.my_float(string.strip(re.sub(r',',"",tline.group(4))))
		low = conv.my_float(string.strip(re.sub(r',',"",tline.group(5))))
		last = conv.my_float(string.strip(re.sub(r',',"",tline.group(6))))
		settle = conv.my_float(string.strip(re.sub(r',',"",tline.group(7))))
		vol = conv.my_long(string.strip(re.sub(r',',"",tline.group(9))))
		open_int = conv.my_long(string.strip(re.sub(r',',"",tline.group(10))))

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
			print "!!!!AVISO: fechamento sem valor!"
		else:
			# procurar Ativo com o vencimento
			ativo = db.obtem_ativo(debug, familia.id, venc)
			if not ativo:
				# ainda não há Ativo com o vencimento, criar!
				print "...Vencimento", venc, "não encontrado, inserir Ativo"
				ativo = db.inserir_ativo(debug, familia, venc, None)
				if not ativo:
					print "!!!!!!PROBLEMAS ao criar ativo para vencimento",venc
			if ativo: 
				print "...Vencimento",venc,"Ativo", ativo.id
				# verificar se já há cotação do ativo para a data na base
				cotacao = db.obtem_cotacao_ativo( debug, ativo, data)
				if not cotacao:
					# inserir cotação
					cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol, vol_financeiro, open_int)
					if cotacao: print "......cotação inserida"
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
						if cotacao_nova: print "......cotação atualizada"
						count_u += 1
					else: 
						print "......cotação idêntica já existe na base, ignorando"
						count_p += 1
				# verificar cotação da véspera
        	                i = -1
                	        cotacao_vespera = None
                        	while not cotacao_vespera and i >= -3: # voltar até 3 dias de semana
                        		data_vespera = conv.shift_data_dias_uteis(debug, data, i)
	                                cotacao_vespera = db.obtem_cotacao_ativo(debug, ativo, data_vespera)
        	                        i = i - 1
                	        if cotacao_vespera:
                        		# verificar open interest
                                	if cotacao_vespera.contratos_aberto != open_int:
                                        	if open_int>0 and cotacao_vespera.contratos_aberto != open_int: print ".......mudou contratos em aberto da véspera",(cotacao_vespera.contratos_aberto,open_int)
	                                        cotacao_vespera.contratos_aberto = open_int
        	                                cotacao_vespera_atualizada = db.update_cotacao_ativo(debug, ativo, cotacao_vespera)
                	                        if cotacao_vespera_atualizada: print "......cotação da véspera atualizada"
                        	else: print ".....Cotação não encontrada para a véspera"


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


arquivo_log = admin.init("ice_us")
programa_id = db.obtem_id_programa(debug, "ice_us")
if not programa_id:
        print "PROBLEMAS!!: programa ice_us não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa ice_us não encontrado na base de dados!");

print "Tratando arquivo",nome_arq
try: 
	f = open(nome_arq)
except IOError, e:
	print "Não foi possível abrir arquivo",nome_arq,"(",e,")"
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")


def le_linha(arq):
	linha = arq.readline()
	if linha: linha = re.sub(r'\n$', " ", linha)
	if debug: print linha
	return linha


# verificar linha de título 
line = le_linha(f)
if "Futures Daily Market Report for ALL COMMODITIES" in line:
	if debug: print "Arquivo OK"
	# obter data de referencia
	line = le_linha(f)
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
	print "PROBLEMAS: Arquivo inválido: título \"Futures Daily Market Report for Dry Freight\" não encontrado!"
       	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Arquivo inválido: título \"Futures Daily Market Report for Dry Freight\" não encontrado")



# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line and not re.match(r'NOTE: The information contained in this report is compiled for the convenience of subscribers', line): # loop de blocos
	while line and re.match(r'^\s*$', line) : line = le_linha(f)	# pular linhas em branco
	# verificar se não é um novo título...
	if re.match(r'Futures Daily Market Report for', line):
		while line and re.match(r'Futures Daily Market Report for', line): line = le_linha(f)
		# pular linha de data que vem depois
		line = le_linha(f)
		while line and re.match(r'^\d{1,2}-[A-Z]{3,3}-\d{4,4}\W*$', line) : line = le_linha(f) # pular linhas de data
		while line and re.match(r'^\s*$', line) : line = le_linha(f)	# pular linhas em branco

	# Verificar linhas de cabeçalho 
	if verificar_linhas_cabecalho() != 0:
       		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Arquivo inválido: problemas com as linhas de cabeçalho")
	
	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco

	# linha com descrição da mercadoria
	print "Mercadoria:", line
	line = le_linha(f)

	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco

	# loop de linhas de dados (vencimentos)
	simbolo = ""
	if versao==1:
		tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+N/A', line)
	else:
		# Simb, Venc, Open, High, Low, Close, Settle, Change, Vol, OI, Change, EFP, EFS, BLOCK_VOL, SPREAD_VOL
 		tline = re.match(r'^\s*(\S+)\s+(\S+)\s+(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
	while tline:
		if debug>1: print "Tupla da linha:", tline.groups()
		if simbolo != string.strip(tline.group(1)):
			simbolo = string.strip(tline.group(1))
			# procurar familia do simbolo
			familia = db.obtem_familia_programa(debug, programa_id, simbolo)
			if not familia: print "...Símbolo", simbolo, "não encontrado em FamiliaContratos, ignorando!"
			else:
				print "...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
		if familia: tratar_vencimento(familia, tline)
		line = le_linha(f)
		while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco
		if debug>1: print "pulou linhas em branco, verificando se é mais um vencimento"
		if versao==1:
			tline = re.match(r'^\s*('+simbolo+r')\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+N/A', line)
		else:
 			tline = re.match(r'^\s*('+simbolo+r')\s+(\S+)\s+(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
		if debug>1:
			if tline:  print "Parece haver mais um vencimento, Tupla da linha após verificação:", tline.groups()
			else: print "LInha não é mais um vencimento"

	if debug>1: print "Saiu do loop de vencimentos, vai pular linhsa em branco"
	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco

	if debug>1: print "Pulou linhas em branco, vai verificar Totais"
	# verificar linha de totais
	if re.match(r'\s*Totals for \S*:\s+\S+\s+\S+\s+\S*\s+\S*\s+\S+\s+\S+\s*', line):
		line = le_linha(f)
	else:
		print "AVISO: linha de totais não encontrada no final do bloco"
       		#admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "linha de totais não encontrada no final do bloco")
	while line and re.match(r'\s*$', line):	line = le_linha(f)	# pular linhas em branco

print "FIM"
admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)

