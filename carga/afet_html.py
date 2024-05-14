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
ignorar = [ "CPPL" ]
novos = []
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


arquivo_log = admin.init("afet")
programa_id = db.obtem_id_programa(debug, "afet")
if not programa_id:
        print "PROBLEMAS!!: programa afet não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa afet não encontrado na base de dados!");


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
linha = re.sub(r'\n', "", linha)
# remover excesso de whitespace
linha = re.sub(r'\s\s+', "", linha)
# remover tranqueira 
linha = re.sub(r'^.*<html>', "<html>", linha)
linha = re.sub(r'<head>.*</head>', "", linha)
linha = re.sub(r'<td>\&nbsp;</td>', "", linha)
linha = re.sub(r'<tr></tr>', "", linha)
linha = re.sub(r'<font[^>]*>', "", linha)
linha = re.sub(r'</font>', "", linha)
linha = re.sub(r' align="[^"]+"', "", linha)
linha = re.sub(r'<td >', "<td>", linha)
linha = re.sub(r'<b>', "", linha)
linha = re.sub(r'</b>', "", linha)
linha = re.sub(r' class="[^"]+"', "", linha)
linha = re.sub(r'\&nbsp;', "", linha)
linha = re.sub(r' >', ">", linha)
linha = re.sub(r'> ', ">", linha)
linha = re.sub(r'\r', "", linha)

i = 0
fim = len(linha)

if debug>1:	print "Dados tem",fim,"caracteres"


# obter Data
i = string.find(linha, "<td>Market Prices (")
if i == -1:
	print "PROBLEMAS: Campo com data do pregão (\"Market Prices\") não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Campo com data do pregão (\"Market Prices\") não encontrado")

if debug>1: print "Campo com data encontrado em",i

i = i + len("<td>Market Prices (")
f = string.find(linha, ")</td>", i)
if f == -1:
	print "PROBLEMAS: terminador (\")</td>\") da data de pregão não encontrado"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: terminador (\")</td>\") da data de pregão não encontrado")

if debug>2: print "...Data: início em",i,"fim em",f
if debug>1: print "..Data encontrada em",i,":", linha[i:f]
data = commands.getoutput("date -d "+linha[i:f]+" +%F")
print "Carregando dados de", data

# loop de  bloco de símbolos
f = f + len(")</td>")
i = string.find(linha, "<td colspan=\"10\">", f)
while i != -1:
	i = i + len("<td colspan=\"10\">")
	f = string.find(linha, "</td>", i)
	simbolo = linha[i:f]
	print "====Encontrado símbolo", simbolo
	
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
				print "AVISO: Símbolo", simbolo, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar:", line
		i = string.find(linha, "<td colspan=\"10\">", f)
	else:
		print "Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
		db.inserir_programa_familia(debug, programa_id, familia)

		f = string.find(linha, "</tr>", i)
		i = f + len("</tr>")

		# verifica linha de cabeçalho
		f = string.find(linha, "</tr>", i)
		x = string.find(linha, "<tr><td>Contract</td><td>Previous Settlement Prc</td><td>Open Price</td><td>High Price</td><td>Low Price</td><td>Close Price</td><td>Change On Day</td><td>Settlement Price</td><td>Traded Vol</td><td>Open Interest</td></tr>", i)
		if x == -1 or x > f:
			print "i=", i, "f=", f, "x=", x
			print "PROBLEMAS: linha de cabeçalho não encontrada ("+linha[i:f]+")"
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de cabeçalho não encontrada")
		i = f + len("</tr>")
	
		# loop de vencimentos do símbolo
		f = string.find(linha, "</tr>", i)
		while f>-1 and re.match(r'<tr><td>'+simbolo+" ", linha[i:f]):
			# obter vencimento
			ti = i + len("<tr><td>"+simbolo+" ")
			tf = string.find(linha, "</td>", ti)
			if debug>1: print "...achou vencimento", linha[ti:tf]
			vencimento = string.split(linha[ti:tf], " ")
			mes = mes_venc[vencimento[0]]
			ano = "20" +  vencimento[1]
			venc = ano + "-" + mes
			print ".Vencimento", vencimento
			ti = tf + len("</td>")
			tline = re.match(r'<td>[\d\.]*</td><td>([\d\.]*)</td><td>([\d\.]*)</td><td>([\d\.]*)</td><td>([\d\.]*)</td><td>[-\d\.]*</td><td>([\d\.]*)</td><td>([\d\.]*)</td><td>([\d\.]*)</td>', linha[ti:f])
			if not tline:
				print "PROBLEMAS: campos do vencimento",vencimento,"do símbolo",simbolo,":", linha[ti:tf]
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: campos do vencimento "+str(vencimento)+" do símbolo "+simbolo)
			if debug>1: print tline.groups()
			abertura = conv.my_float(tline.group(1))
			high = conv.my_float(tline.group(2))
			low = conv.my_float(tline.group(3))
			last = conv.my_float(tline.group(4))
			settle = conv.my_float(tline.group(5))
			vol_contratos = conv.my_long(tline.group(6))
			open_int = conv.my_long(tline.group(7))
			vwap = negocios = vol_financeiro = None

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
				else:
					# já há cotação nesse dia
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
			i = f + len("</tr>")
			f = string.find(linha, "</tr>", i)
		
		i = string.find(linha, "<td colspan=\"10\">", i)

print "FIM"

if len(novos)>0:
        print "Símbolos novos detectados:", novos
admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)

