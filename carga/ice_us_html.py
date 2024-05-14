#!/usr/bin/python -u
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, string, commands
import db, conv, admin

moedas = {}

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


#n = db.carrega_simbolos_moedas(debug, moedas)
#if n<2:
#	print "PROBLEMAS: foram carregadas menos de 2 moedas:", n
#	sys.exit(1)
#print "Há",n,"moedas cadastradas"

print "Tratando arquivo",nome_arq
try: 
	arq = open(nome_arq)
except IOError, e:
	print "Não foi possível abrir arquivo",nome_arq,"(",e,")"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")

# Ler arquivo todo
try: 
	linha = arq.read()
except IOError, e:
	print "Problemas o ler arquivo",nome_arq,"(",e,")"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Problemas o ler arquivo"+nome_arq+"("+e+")")
arq.close()

# remover quebras de linha
linha =  re.sub(r'\n', "", linha)
# remover excesso de whitespace
linha = re.sub(r'\s\s+', "", linha)
# remover alguns styles
linha = re.sub(r' style="padding:0;"', "", linha)
linha = re.sub(r' style="color:[^;]*;"', "", linha)
linha = re.sub(r' nowrap=true', "", linha)
linha = re.sub(r' class="even"', "", linha)
linha = re.sub(r' class="odd"', "", linha)
linha = re.sub(r' class="center"', "", linha)
linha = re.sub(r' class="number"', "", linha)
linha = re.sub(r'\s*</td>', "</td>", linha)
linha = re.sub(r'<td>\s*', "<td>", linha)
i = 0
fim = len(linha)

if debug>1:	print "Dados tem",fim,"caracteres"


# Verificar Título
i = string.find(linha, "<head><title>ICE Futures U.S. - Futures Daily Market Report</title>")
if i == -1:
	print "PROBLEMAS: título esperado (ICE Futures U.S. - Futures Daily Market Report) não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: título esperado (ICE Futures U.S. - Futures Daily Market Report) não encontrado")
if debug>1: print "Título encontrado em",i

# Verificar sub-título
i = string.find(linha, "<div class=\"mainTitle\">Futures Daily Market Report for ALL COMMODITIES</div><div class=\"subTitle\">")
if i == -1:
	print "PROBLEMAS: Sub-título (Futures Daily Market Report for ALL COMMODITIES) não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Sub-título (Futures Daily Market Report for ALL COMMODITIES) não encontrado")


# obter Data
i = i + len("<div class=\"mainTitle\">Futures Daily Market Report for ALL COMMODITIES</div><div class=\"subTitle\">")
f = string.find(linha, "</div>", i)
if f == -1:
	print "PROBLEMAS: terminador (</div>) da data de pregão não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: terminador (</div>) da data de pregão não encontrado")
if debug>2: print "...Data: início em",i,"fim em",f
if debug>1: print "..Data encontrada em",i,":", linha[i:f]
data = commands.getoutput("date -d "+linha[i:f]+" +%F")
print "Carregando dados de",data

# procurar tabela
tf = f
ti = string.find(linha, "<table class=\"default\">", tf)
if debug>2: 
	print "Tabela em", ti
while ti != -1:
	# achar fim da tabela
	tf = string.find(linha, "</table>", ti)
	if tf == -1:
		print "PROBLEMAS: final de tabela começando em",ti,"não encontrado"
		print linha[ti:fim]
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: final de tabela começando em",ti,"não encontrado")

	tf = tf + len("</table>")

	# Verificar cabeçalho
        i = string.find(linha, "<tr><th rowspan=\"2\" class=\"multiRow\">Commodity Name</th><th rowspan=\"2\" class=\"multiRow\">Contract Month</th><th colspan=\"4\">Electronic Daily <br> Price Range</th><th colspan=\"2\">Settle</th><th colspan=\"8\">Current Volume Report Totals</th><th colspan=\"2\">Contract</th></tr><tr><th>Open#</th><th>High</th><th>Low</th><th>Close#</th><th>Price</th><th>Change</th><th>Total<br>Volume@</th><th>OI</th><th>Change</th><th>ADJ**</th><th>EFP</th><th>EFS</th><th>Block Trades</th><th>Spread<br>Volume</th><th>High</th><th>Low</th></tr>", ti, tf)
	if i == -1:
		print "PROBLEMAS: Cabeçalho padrão não encontrado"
		print linha[ti:tf]
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Cabeçalho padrão não encontrado")

	i = i + len("<tr><th rowspan=\"2\" class=\"multiRow\">Commodity Name</th><th rowspan=\"2\" class=\"multiRow\">Contract Month</th><th colspan=\"4\">Electronic Daily <br> Price Range</th><th colspan=\"2\">Settle</th><th colspan=\"8\">Current Volume Report Totals</th><th colspan=\"2\">Contract</th></tr><tr><th>Open#</th><th>High</th><th>Low</th><th>Close#</th><th>Price</th><th>Change</th><th>Total<br>Volume@</th><th>OI</th><th>Change</th><th>ADJ**</th><th>EFP</th><th>EFS</th><th>Block Trades</th><th>Spread<br>Volume</th><th>High</th><th>Low</th></tr>")
	
	i = string.find(linha, "<tr class=\"subHeaderRow\"><td colspan=\"18\" style=\"text-align:left;\">", ti, tf)
	
	# Obter símbolo da mercadoria
	if i == -1:
		print "PROBLEMAS: linha de subHeader (define a mercadoria!) não encontrada"
		print linha[ti:tf]
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de subHeader (define a mercadoria!) não encontrada")

	i = i + len("<tr class=\"subHeaderRow\"><td colspan=\"18\" style=\"text-align:left;\">")
	f = string.find(linha, "</td></tr>", i, tf)
	if f == -1:
		print "PROBLEMAS: final de linha de código de mercadoria não encontrado"
		print linha[i:tf]
	if debug>1: print "...mercadoria:", linha[i:f]
	tsimb = re.match(r'[^\(]*\(([^\)]+)\)', linha[i:f])
	if not tsimb:
		print "AVISO: símbolo não encontrado na linha de código de mercadoria:", string.strip(linha[i:f])
		####admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: símbolo não encontrado na linha de código de mercadoria")
	else:
		simbolo = tsimb.group(1)
		print "\nSímbolo", simbolo

		# procurar família do símbolo
		familia = db.obtem_familia_programa(debug, programa_id, simbolo)
		if not familia:
			print "...Mercadoria", simbolo, "não encontrada em FamiliaContratos, ignorando!"
		else:
			print "...Mercadoria", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
			
			i = f + len("</td></tr>")
			i = string.find(linha, "<tr><td>"+simbolo+"</td>", i, tf)
			while i != -1:	# loop de vencimentos
				f = string.find(linha, "</tr>", i, tf)
				if f == -1: 
					print "PROBLEMAS: final de linha de vencimento não encontrado"
					print linha[i:tf]
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: final de linha de vencimento não encontrado")

				f = f + len("</tr>")
				if debug >2: print "linha:...",i,f,f-i,linha[i:f],"\n\n"
#                                                  CC              Dec-13                       2839           2840            2832            2832            2821                     30                    29              N/A                       N/A                   N/A             0                 0              0              29               0              0   
###				tline = re.match(r'<tr><td>([^<]*)</td><td>([^<&]*)(?:&nbsp;)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>([^<]*)</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td><span ?>([^<]*)</span></td><td>([^<]*)</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td>', linha[i:f])
				tline = re.match(r'<tr><td>([^<]*)</td><td>([^<&]*)(?:&nbsp;)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>\*?(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td><td>(?:<span ?>)?([^<]*)(?:</span>)?</td>', linha[i:f])
				if tline:
					# linha de vencimento
					if debug>1: print "......",tline.groups()
					venc = "20"+conv.my_str(tline.group(2))[4:6]+"-"+mes_venc[conv.my_str(string.upper(tline.group(2)))[0:3]]
					if re.match(r'N/A', tline.group(3)):
						abertura = None
					else:
						abertura = conv.my_float(re.sub(r',', "", tline.group(3)))
					if re.match(r'N/A', tline.group(4)):
						high = None
					else:
						high = conv.my_float(re.sub(r',', "", tline.group(4)))
					if re.match(r'N/A', tline.group(5)):
						low = None
					else:
						low = conv.my_float(re.sub(r',', "", tline.group(5)))
					if re.match(r'N/A', tline.group(6)):
						last = None
					else:
						last = conv.my_float(re.sub(r',', "", tline.group(6)))
					settle = conv.my_float(re.sub(r',', "", tline.group(7)))
					if re.match(r'N/A', tline.group(9)):
						vol_contratos = 0
					else:
						vol_contratos = conv.my_float(re.sub(r',', "", tline.group(9)))
					if re.match(r'N/A', tline.group(10)):
						open_int = 0
					else:
						open_int = conv.my_float(re.sub(r',', "", tline.group(10)))
				
					vwap = negocios = vol_financeiro = None

					if debug: print "...Vencimento", venc

					if debug>1:
						print "\tdata:", data
						print "\tsímbolo:", simbolo
						print "\tvencimento:", venc
						print "\tcontratos em aberto:", open_int
						print "\tvolume de contratos:", vol_contratos
						print "\tvolume financeiro:", vol_financeiro
						print "\tnegocios:", negocios
						print "\tabertura:", abertura
						print "\tmínimo:", low
						print "\tmáximo:", high
						print "\tvwap:", vwap
						print "\túltimo:", last
						print "\tajuste (settle):", settle
					# procurar ativo
					ativo = db.obtem_ativo(debug, familia, venc)
					if not ativo:
						# ainda não há ativo como vencimento, criar!
						print "....Vencimento",venc,"não encontrado, inserir Ativo"
						ativo = db.inserir_ativo(debug, familia, venc, None)
						if not ativo: print "!!!!! PROBLEMAS ao criar ativo para vencimento", venc
					if ativo:
						print "....Vencimento",venc,"Ativo",ativo.id
						# verificar se há cotação do ativo para a data
						cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
						if not cotacao:
							# inserir cotação
							cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
							if cotacao: print "......cotação inserida"
							count_i += 1
						else:	# já há cotação nesse dia
							# verificar se mudou...
							if (abertura>0 and cotacao.abertura != abertura) or (last>0 and cotacao.ultimo != last) or (settle>0 and cotacao.fechamento != settle) or (cotacao.vwap != None) or (high>0 and cotacao.maximo != high) or (low>0 and cotacao.minimo != low) or (cotacao.negocios != None) or (vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (cotacao.volume_financeiro != None) or (open_int>0 and cotacao.contratos_aberto != open_int):
								if abertura>0 and cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
                                	                        if last>0 and cotacao.ultimo != last: print ".......mudou ultimo",(cotacao.ultimo,last)
                                        	                if settle>0 and cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
                                                	        if cotacao.vwap != None: print ".......mudou vwap",(cotacao.vwap,vwap)
                                                        	if high>0 and cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
	                                                        if low>0 and cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
        	                                                if cotacao.negocios != None: print ".......mudou negocios",(cotacao.negocios,negocios)
                	                                        if vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos)
                        	                                if cotacao.volume_financeiro != None: print ".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro)
                                	                        if open_int>0 and cotacao.contratos_aberto != open_int: print ".......mudou contratos_aberto",(cotacao.contratos_aberto,open_int)
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
								if cotacao_nova: print "......cotação atualizada"
								count_u += 1
							else: 
								print "......cotação idêntica já existe na base, ignorando"
								count_p += 1
				i = f
				i = string.find(linha, "<tr><td>"+simbolo+"</td>", i, tf)

	ti = string.find(linha, "<table class=\"default\">", tf)
	if debug>2: 
		print "Tabela em", ti

print "FIM"
admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)

