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

ignorar = [ "AA", "AM", "KK", "KW", "KB", "KS", "KC", "KM", "AP", "AR", "VI", "AF", "ATR", "IB", "IR", "OI", "YT", "YS", "XT", "XS", "BN", "BQ", "BS", "BV", "PN", "PQ", "PS", "PV", "GK", "GJ", "GN", "GQ", "GS", "GV", "GX", "GY", "EO", "EN", "EQ", "ES", "EV", "VS", "XX" ]
novos = []

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


arquivo_log = admin.init("asx")
programa_id = db.obtem_id_programa(debug, "asx")
if not programa_id:
        print "PROBLEMAS!!: programa asx não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa asx não encontrado na base de dados!");



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
linha =  re.sub(r'\r', "", linha)
# remover excesso de whitespace
linha = re.sub(r'\s\s+', "", linha)
# remover alguns styles
linha = re.sub(r'<br>*', "", linha)
linha = re.sub(r' align="left"', "", linha)
linha = re.sub(r' align="right"', "", linha)
linha = re.sub(r' valign="[^"]*"', "", linha)
linha = re.sub(r' width="[^"]*"', "", linha)
linha = re.sub(r' colspan="\d*"', "", linha)
linha = re.sub(r' class="Highlight"', "", linha)
linha = re.sub(r' class="noHighlight"', "", linha)
linha = re.sub(r'<TD><BR></TD>', "", linha)
linha = re.sub(r'<TR></TR>', "", linha)
linha = re.sub(r'&amp;', "&", linha)
linha = re.sub(r'\s*</td>', "</td>", linha)
linha = re.sub(r'<td>\s*', "<td>", linha)
linha = re.sub(r'<TR><TD><IMG src=[^>]*></TD></TR>', "", linha)
i = 0
fim = len(linha)

if debug>1:	print "Dados tem",fim,"caracteres"

# Verificar Título
i = string.find(linha, "<head><title>SFE End of Day Data - Futures Total Traded at close of trade date ")
if i == -1:
	print "PROBLEMAS: título esperado (SFE End of Day Data - Futures Total Traded at close of trade date) não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: título esperado (SFE End of Day Data - Futures Total Traded at close of trade date) não encontrado")
if debug>1: print "Título encontrado em",i


# obter Data
i = i + len("<head><title>SFE End of Day Data - Futures Total Traded at close of trade date ")
f = string.find(linha, "</title>", i)
if f == -1:
	print "PROBLEMAS: terminador (</title>) da data de pregão não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: terminador (</title>) da data de pregão não encontrado")
if debug>2: print "...Data: início em",i,"fim em",f
if debug>1: print "..Data encontrada em",i,":", linha[i:f]
#data = commands.getoutput("date -d "+linha[i:f]+" +%F")
data = "20"+linha[i+6:i+8]+"-"+linha[i+3:i+5]+"-"+linha[i:i+2]
print "Carregando dados de",data


# procurar linha de descrição de mercadoria
i = string.find(linha, "<TR class=\"Headbold\">", f)
while i > -1:
	# achar fim da mercadoria
	f = string.find(linha, "Click here to view settlement price and volume graph", i)
	if f == -1:
		print "PROBLEMAS: linha final da mercadoria (\"Click here to view settlement price and volume graph\") não encotrada"
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha final da mercadoria (\"Click here to view settlement price and volume graph\") não encotrada")

	# Obter símbolo da mercadoria
	i = i + len("<TR class=\"Headbold\"><TD>")
	tf = string.find(linha, "</TD>", i)
	if tf == -1:
		print "PROBLEMAS: final da linha de mercadoria (\"</TD>\") não encotrado"
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: final da linha de mercadoria (\"</TD>\") não encotrado")
	mercadoria = linha[i:tf]
	if debug: print "---------------"
	if debug > 1: print "Mercadoria:", mercadoria
	tsimb = re.match(r'([^ -]*) - ', linha[i:tf])
	if not tsimb:
		print "AVISO: símbolo não encontrado na linha de código de mercadoria:", string.strip(linha[i:f])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: símbolo não encontrado na linha de código de mercadoria")
	else:
		simbolo = tsimb.group(1)
		print "Símbolo", simbolo
		# procurar família do símbolo
		familia = db.obtem_familia_programa(debug, programa_id, simbolo)
		if not familia:
			try:
				x = ignorar.index(simbolo)
				print "Símbolo", simbolo, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar"
			except ValueError, e:
				try:
					x = novos.index(simbolo)
				except ValueError, e:
					novos.append(simbolo)
					print "AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", mercadoria
		else:
			print "Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
			db.inserir_programa_familia(debug, programa_id, familia)

		if familia:
			# verificar linha de cabeçalho
		        i = string.find(linha, "<TR><TD>Expiry</TD><TD>Open</TD><TD>High</TD><TD>Low</TD><TD>Last</TD><TD>Sett</TD><TD>Sett Chg</TD><TD>Op Int</TD><TD>Op Int Chg</TD><TD>Volume</TD></TR>", tf, f)
			if i == -1:
				print "PROBLEMAS: Cabeçalho padrão não encontrado"
				print linha[tf:f]
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Cabeçalho padrão não encontrado")
			tf = i + len("<TR><TD>Expiry</TD><TD>Open</TD><TD>High</TD><TD>Low</TD><TD>Last</TD><TD>Sett</TD><TD>Sett Chg</TD><TD>Op Int</TD><TD>Op Int Chg</TD><TD>Volume</TD></TR>")
			i =  string.find(linha, "<TR><TD>", tf, f)
			while i > -1:
				if debug: print ""
				tf = string.find(linha, "</TR>", i, f)
				if tf == -1: 
					print "PROBLEMAS: final de linha de vencimento não encontrado"
					print linha[i:f]
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: final de linha de vencimento não encontrado")
				if debug >2: print "linha:...",i,tf,tf-i,linha[i:tf]
#				Vencimento, Open, High, Low, Last, Settle, Change, Open Interest, Change, Volume			
				tline = re.match(r'<TR><TD>([^<]*)</TD><TD>([^<]*)</TD><TD>([^<]*)</TD><TD>([^<]*)</TD><TD>([^<]*)</TD><TD>([^<]*)</TD><TD>[^<]*</TD><TD>([^<]*)</TD><TD>[^<]*</TD><TD>([^<]*)</TD>', linha[i:tf])			
				if tline:
					# linha de vencimento
					if debug>1: print "......",tline.groups()
					vencimento = string.split(tline.group(1), " ")
					if debug>1: print "...... Vencimento:", vencimento
					venc = conv.my_str(vencimento[1])+"-"+mes_venc[conv.my_str(string.upper(vencimento[0]))]
					if re.match(r'-', tline.group(2)):
						abertura = None
					else:
						abertura = conv.my_float(re.sub(r',', "", tline.group(2)))
					if re.match(r'-', tline.group(3)):
						high = None
					else:
						high = conv.my_float(re.sub(r',', "", tline.group(3)))
					if re.match(r'-', tline.group(4)):
						low = None
					else:
						low = conv.my_float(re.sub(r',', "", tline.group(4)))
					if re.match(r'-', tline.group(5)):
						last = None
					else:
						last = conv.my_float(re.sub(r',', "", tline.group(5)))
					settle = conv.my_float(re.sub(r',', "", tline.group(6)))
					if re.match(r'-', tline.group(7)):
						open_int = 0
					else:
						open_int = conv.my_float(re.sub(r',', "", tline.group(7)))
					if re.match(r'-', tline.group(8)):
						vol_contratos = 0
					else:
						vol_contratos = conv.my_float(re.sub(r',', "", tline.group(8)))
			
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
				else:
					print "PROBLEMAS: linha de dados não reconhecida", mercadoria, linha[i:tf]
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de dados não reconhecida")
				i =  string.find(linha, "<TR><TD>", tf, f)

	i = string.find(linha, "<TR class=\"Headbold\">", f)


if len(novos)>0:
        print "Símbolos novos detectados:", novos

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
#
