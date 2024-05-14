#!/usr/bin/python -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, string, os.path
import db, conv, admin

debug=0
count_i=count_u=count_p=0
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

ignorar = [ "AIR", "AJC", "AMM", "AW", "BCX", "BRS", "BST", "C3S", "CAW", "CCS", "CKS", "CKW", "CPC", "CSI", "DDG", "DFL", "DFT", "DGS", "DRS", "FCP", "FGE", "FGL", "FPO", "FTE", "FZE", "HB0", "HR0", "IBF", "IHF", "IOI", "IPF", "ISF", "IWF", "K6S", "KAW", "KB3", "KC7", "KLI", "KLS", "KNS", "KWS", "KZS", "MCX",  "MG3", "MG5", "NM", "NX", "OPS", "PKO", "Q02", "Q04", "Q06", "QC2", "QC3", "QC4", "QC6", "QC7", "QC8", "QCC", "QCW", "QM2", "QM3", "QM4", "QM5", "QM6", "QO2", "QO3", "QO4", "QO5", "QO6", "QS0", "QS1", "QS2", "QS3", "QS5", "QS8", "QS9", "QW2", "QW3", "QW6", "QX5", "RHB", "RRE", "S7C", "SE2", "SE3", "SES", "SNS", "SQ2", "SQ5", "UFG", "UFN", "UFU", "UFZ", "UPO", "WCS", "WMK", "WQ6", "Y01", "Y02", "Y03", "Y04", "Y05", "Z3W", "ZWC", "ZX", "AA", "KB", "RB", "***" ]
novos = []



def desfraciona(s):
	# Alguns ativos da CME tem valores na forma n'm, onde n é inteiro m é [01234567] (número de 1/8s)
	c = re.match(r'\s*(\d+)\'(\d+)', s)
	if not c:
		return s
	else:
		a = c.group(1)
		b = c.group(2)
		n = int(a) + int(b) * 0.125 
		return str(n)



#https://www.cmegroup.com/content/dam/cmegroup/notices/clearing/2023/02/Chadv23-037.pdf
#https://www.cmegroup.com/market-data/files/settlement-file-layout.pdf

#Column 1 (10 char width)  MTH/STRIKE  The Month column designates the month and year of the contract.
#Column 2 (13 char width)  Open Represents the first price at which the contract traded after opening, on either Globex or Open Outcry..
#Column 3 (13 char width)  High   Displays the highest price at which the contract traded during the trading day, during either Globex or the Open Outcry session. If the price is followed by a B, this indicates a bid price that was higher than the highest traded price.
#Column 4 (13 char width)  Low Displays the lowest price at which the contract traded during the trading day, during either Globex or the Open Outcry session. If the price is followed by an A, this indicates an ask price that was lower than the lowest traded price
#Column 5 (13 char width)  Last  Displays the last price traded. If the last price is followed by a B or an A, this indicates that the last price was a bid or ask.
#Column 6 (12 char width)  Sett Displays the settlement price calculated at the end of the trading day for the contract.
#Column 7 (12 char width)  CHGE Displays the change in price between the trade date settlement price and the previous days settlement price. If the current days settlement price is the same as the previous days price, or if the previous trading day was the first day the product was settled, 0 (zero) is displayed.
#Column 8 (9 char width)  EST. VOL  Displays the total number of contracts traded during the trading day, during both Globex and the Open Outcry session. A blank in this column indicates that the contract did not trade on the trade date.
#Column 9 (12 char width)  SETT Prior Day Settlement displays the final settlement price calculated at the end of the previous trading day.
#Column 10 (9 char width)  VOL  Prior Day Volume displays the total number of contracts traded during the prior day trading. Both outright and spread volume is included. A blank in this column indicates that the contract did not trade on the trade date.
#Column 11 (9 char width) INT   The Open Interest column displays the total number of contracts long or short in the respective month, during both Globex and the Open Outcry session. Each open transaction has both a buyer and seller, but only one side of the transaction is counted when calculating open interest. A blank in this column indicates that there is no Open Interest.

#1. Report columns are wider, making the whole report line wider (from 110 chars to 138 chars) 

#MTH/                       -------  DAILY  ------                                  PT                         -------  PRIOR  DAY  -------
#STRIKE            OPEN         HIGH          LOW         LAST         SETT         CHGE  ACTUAL VOL           SETT         VOL         INT
#06 Soybean Meal Futures
#JUL23            406.4        410.6        400.7        402.2        402.2         -4.2       57163          406.4       65237      175267
#         1         2         3         4         5         6         7         8         9         0         1         2         3         4
#12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#         |            |            |            |            |           |            |           |              |           |

def tratar_vencimento(familia, line):
	global nome_arq, programa_id, arquivo_log, data, count_i, count_u, count_p
	# só tratar se tivermos encontrado família para o símbolo, senão ignorar
	if familia: # tratar vencimento
		prev_settle = None
		prev_vol = None
		venc = conv.my_str(line[0:10].strip())
		abertura = conv.my_float((desfraciona(re.sub(r'[AB-]+',"",line[10:23]))).strip())
		high = conv.my_float((desfraciona(re.sub(r'[AB-]+',"",line[23:36]))).strip())
		low = conv.my_float((desfraciona(re.sub(r'[AB-]+',"",line[36:49]))).strip())
		last = conv.my_float((desfraciona(re.sub(r'[AB-]+',"",line[49:62]))).strip())
		settle = conv.my_float((desfraciona(line[62:74])).strip())
		vol = conv.my_long((re.sub(r'[AB-]+',"",line[87:99])).strip())
		open_int = conv.my_long(line[126:138].strip())
		vencimento = "20" + venc[3:5] + "-" + mes_venc[venc[0:3]]

		vwap = negocios = vol_financeiro = None

		try:
			prev_settle = conv.my_float((desfraciona(line[100:112])).strip())
		except ValueError as e:
			prev_setlle = None
		try:
			prev_vol = conv.my_long((re.sub(r'[AB-]+',"",line[114:126])).strip())
		except ValueError as e:
			prev_vol = None

		if debug>1:
			print("\tdata:", data)
			print( "\tsímbolo:", simbolo)
			print( "\tvencimento:", venc)
			print( "\tvolume financeiro:", vol_financeiro)
			print( "\tcontratos em aberto:", open_int)
			print( "\tnegócios:", negocios)
			print( "\tvolume de contratos:", vol)
			print("\tabertura:", abertura)
			print("\tmínimo:", low)
			print("\tmáximo:", high)
			print("\tvwap:", vwap)
			print("\túltimo:", last)
			print("\tajuste (settle):", settle)
			print("\tprev_settle:", prev_settle)
			print("\tprev_vol:", prev_vol)
		elif debug: print("venc:"+vencimento+"("+venc+") settle:",settle,"volume:",vol,"open_interest:",open_int)

		# procurar Ativo com o vencimento
		ativo = db.obtem_ativo(debug, familia, vencimento)
		if not ativo:
			# ainda não há Ativo com o vencimento, criar!
			print("...Vencimento", venc, "não encontrado, inserir Ativo")
			ativo = db.inserir_ativo(debug, familia, vencimento, None)
			if not ativo:
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "!!!!!!PROBLEMAS ao criar ativo da familia "+familia.id+"("+familia.nome_res.encode('utf-8')+") para vencimento "+venc)
		if ativo: 
			print("...Vencimento",vencimento,"Ativo", ativo.id)
			# verificar se já há cotação do ativo para a data na base
			cotacao = db.obtem_cotacao_ativo( debug, ativo, data)
			if not cotacao:
				# inserir cotação
				cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol, vol_financeiro, open_int)
				if cotacao: print("......cotação inserida")
				count_i += 1
			else:	# já há cotação nesse dia
				# verificar se mudou...
				if cotacao.abertura != abertura or cotacao.ultimo != last or cotacao.fechamento != settle or cotacao.vwap != None or cotacao.maximo != high or cotacao.minimo != low or cotacao.negocios != None or cotacao.volume_contratos != vol or cotacao.volume_financeiro != None:
					if cotacao.abertura != abertura: print(".......mudou abertura",(cotacao.abertura,abertura))
					if cotacao.ultimo != last: print(".......mudou ultimo",(cotacao.ultimo,last))
					if cotacao.fechamento != settle: print(".......mudou fechamento",(cotacao.fechamento,settle))
					if cotacao.vwap != None: print(".......mudou vwap",(cotacao.vwap,vwap))
					if cotacao.maximo != high: print(".......mudou maximo",(cotacao.maximo,high))
					if cotacao.minimo != low: print(".......mudou minimo",(cotacao.minimo,low))
					if cotacao.negocios != None: print(".......mudou negocios",(cotacao.negocios,negocios))
					if cotacao.volume_contratos != vol: print(".......mudou volume_contratos",(cotacao.volume_contratos,vol))
					if cotacao.volume_financeiro != None: print(".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro))
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
					cotacao_nova = db.update_cotacao_ativo(debug, ativo, cotacao)
					if cotacao_nova: print("......cotação atualizada")
					count_u += 1
				else: 
					print("......cotação idêntica já existe na base, ignorando")
					count_p += 1
			# verificar cotação da véspera
			i = -1
			cotacao_vespera = None
			while not cotacao_vespera and i >= -3: # voltar até 3 dias de semana
				data_vespera = conv.shift_data_dias_uteis(debug, data, i)
				cotacao_vespera = db.obtem_cotacao_ativo(debug, ativo, data_vespera)
				i = i - 1
			if cotacao_vespera:
				# verificar fechamento, volume e open interest
				if cotacao_vespera.fechamento != prev_settle or cotacao_vespera.volume_contratos != prev_vol or cotacao_vespera.contratos_aberto != open_int:
					if prev_settle and prev_settle>0 and cotacao_vespera.fechamento != prev_settle: print(".......mudou fechamento da véspera",(cotacao_vespera.fechamento,prev_settle))
					if prev_vol and prev_vol>0 and cotacao_vespera.volume_contratos != prev_vol: print(".......mudou volume da véspera",(cotacao_vespera.volume_contratos,prev_vol))
					if open_int and open_int>0 and cotacao_vespera.contratos_aberto != open_int: print(".......mudou contratos em aberto da véspera",(cotacao_vespera.contratos_aberto,open_int))
					cotacao_vespera.fechamento = prev_settle
					cotacao_vespera.volume_contratos = prev_vol
					cotacao_vespera.contratos_aberto = open_int
					cotacao_vespera_atualizada = db.update_cotacao_ativo(debug, ativo, cotacao_vespera)
					if cotacao_vespera_atualizada: print("......cotação da véspera atualizada")
			else: print(".....Cotação não encontrada para a véspera")


#===========================================================

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

programa = (os.path.basename(sys.argv[0])).replace(".py", "")

arquivo_log = admin.init(programa)
programa_id = db.obtem_id_programa(debug, programa)

if not programa_id:
	print("PROBLEMAS!!: programa cme_agro não encontrado na base de dados!")
	# enviar email
	admin.sair(debug, programa_id, nome_arq, arquivo_log, None, count_i, count_u, count_p, "PROBLEMAS!!: programa cme_agro não encontrado na base de dados!"); 

print("Tratando arquivo",nome_arq)
try: 
	f = open(nome_arq)
except IOError as e:
	print("Não foi possível abrir arquivo",nome_arq,"(",e,")")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, None, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")


def le_linha(arq):
	global lin
	lin = lin + 1
	linha = re.sub(r'\n$', "", arq.readline())
	if debug: print("("+str(lin)+"):", linha)
	return linha



# verificar linha de título 
line = le_linha(f)
if "FINAL POST-CLEARING PRICES AS OF " in line:
	if debug: print("Arquivo OK")
	# obter data de referencia
	tdata = re.search(r'FINAL POST-CLEARING PRICES AS OF (\d+)/(\d+)/(\d+) ', line)
	if tdata:
		dia = tdata.group(2)
		mes = tdata.group(1)
		ano = tdata.group(3)
		data = ano+"-"+mes+"-"+dia
		print("Arquivo contém dados de "+dia+"/"+mes+"/"+ano)
	else:
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: data de referência não encontrada na linha de título!")
else:
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: título \"FINAL PRE-CLEARING PRICES AS OF\" não encontrado!")

# Verificar linhas de cabeçalho 
line = le_linha(f)

print(line)

#print("MTH/                 ---- DAILY ---                        PT                     -------  PRIOR  DAY  -------")

if "MTH/                       -------  DAILY  ------                                  PT                         -------  PRIOR  DAY  -------" not in line:
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: primeira linha de cabeçalho não encontrada!")

line = le_linha(f)

#print(line)
#print("STRIKE     OPEN      HIGH      LOW       LAST      SETT    CHGE     EST.VOL       SETT         VOL         INT")

if "STRIKE            OPEN         HIGH          LOW         LAST         SETT         CHGE  ACTUAL VOL           SETT         VOL         INT" not in line:
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: segunda linha de cabeçalho não encontrada!")


# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line:	# loop de simbolos
	# devemos ter uma linha definindo um símbolo (família de contratos)
	tsymb = re.match(r'(\S*) (.*)', line)
	if not tsymb:
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de símbolo esperada (e não encontrada)")
	simbolo = tsymb.group(1)
	desc = tsymb.group(2)
	# verificar se símbolo é de uma família de Opções
	tdesc = re.match(r'[A-Z]{3}\d{2}\s+.* (?=CALL|PUT)', desc, re.I)
	if tdesc: # Opções.... não tratamos!
		print("Opções (ignorando!):"+line)
		line = le_linha(f)
		tline = re.match(r'^-?\d+\s', line)
		while tline:	#loop de strike price
			# ignorar linhas para cada strike price
			line = le_linha(f)
			tline = re.match(r'^-?\d+\s', line, re.I)
	else:   # símbolo de família de Futuros
		print("Símbolo "+simbolo+": "+desc)
		# procurar família do símbolo
		familia = db.obtem_familia_programa(debug, programa_id, simbolo)
		if familia:
			db.inserir_programa_familia(debug, programa_id, familia)
			print("...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8'))
		else:
			try:
				i = ignorar.index(simbolo)
				print("...Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar")
			except ValueError as e:
				novos.append(simbolo)
				print("AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", line)

		# agora temos a lista dos contratos (ativos) da família, cada um com um vencimento
		line = le_linha(f)	
		tline = re.match(r'[A-Z]{3}\d{2}\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+', line)
		while tline:	# loop de contratos (vencimentos) de um simbolo
			tratar_vencimento(familia, line)
			# ler próximo vencimento
			line = le_linha(f)
			tline = re.match(r'[A-Z]{3}\d{2}\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+', line)
	# Tratar linh(s) de Total (ignorá-las)
	tline = re.match(r'TOTAL\s*', line)
	while tline: 	# loop de totals
		# ignorar linhas de TOTAL
		line = le_linha(f)
		tline = re.match(r'TOTAL\s*', line)
	# agora devemos ter outro símbolo, voltar pro início do loop

if len(novos)>0:
	print("Símbolos novos detectados:", novos)

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
db.close()
