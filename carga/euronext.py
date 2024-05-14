#!/usr/bin/python -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

import sys, re, string, commands
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
lin=0
ignorar = []
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


arquivo_log = admin.init("euronext")
programa_id = db.obtem_id_programa(debug, "euronext")
if not programa_id:
        print "PROBLEMAS!!: programa euronext não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa euronext não encontrado na base de dados!");


print "Tratando arquivo",nome_arq
try: 
	f = open(nome_arq)
except IOError, e:
	print "Não foi possível abrir arquivo",nome_arq,"(",e,")"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo "+nome_arq+"("+str(e)+")")	


def le_linha(arq):
	global lin
	lin = lin + 1
	linha = re.sub(r'\n$', "", arq.readline())
	if debug: print "("+str(lin)+"):", linha
	return linha




# verificar linha de título 
line = le_linha(f)
if "Euronext Paris - Daily Derivatives statistics of" in line:
	if debug: print "Arquivo OK"
	# obter data de referencia
	#tdata = re.search(r'"Euronext Paris - Daily Derivatives statistics of +\([^"]+\)"', line)
	tdata = re.search(r'"Euronext Paris - Daily Derivatives statistics of ([^"]*)\"', line)
	if tdata:
		str_data = tdata.group(1).split(" ")
		if debug>1: print "String de data:", str_data
		data = commands.getoutput("date -d \""+str_data[2]+"-"+str_data[1]+"-"+str_data[0]+"\" +%F")
		tdata = re.match(r'\d{4}-\d{2}-\d{2}', data)
		if tdata: print "Arquivo contém dados de", data
		else:
			print "PROBLEMAS ao converter data \"",tdata,"\", saida do date:", data
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS ao converter data \""+tdata+"\", saida do date: "+data)
	else:
		print "PROBLEMAS: Arquivo inválido: data de referência não encontrada na linha de título!"
		print line
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: data de referência não encontrada na linha de título!")
else:
	print "PROBLEMAS: Arquivo inválido: título \"Euronext Paris - Daily Derivatives statistics of\" não encontrado!"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: título \"Euronext Paris - Daily Derivatives statistics of\" não encontrado!")

# Procurar Sheet de EOD
line = le_linha(f)
pular = 1
while pular:
	if "Euronext Paris - All Series at " in line:
		pular = 0;
	line = le_linha(f)
if debug: print "Encontrou sessão de EOD"

while re.match(r'^,,,,,,$', line): line = le_linha(f)

if not re.match(r'"Date","Product group",,"Generic contract type","Contract code","Contract name","Contract type","Expiry month","Exercise price","Lot size","Exercise type","Settlement price","First price","Highest price","Lowest price","Last price","Volume \(Total\)","Cleared volume \(Block\)","Number of trades \(Total\)","Value of volume in euro \(Total\)","Premium turnover in euro \(Total\)","Open Interest"', line):
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: cabeçalho de EOD não encontrado!")
	

# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line: # loop de símbolos/vencimentos
	tline = re.match(r'^"([0-9\/]+)","Commodity Products *","Commodity Products *","Futures ","([^"]*)","([^"]*)","[^"]*","([^"]*)","[^"]*","([^"]*)","[^"]*","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","[^"]*","([^"]*)","([^"]*)","[^"]*","([^"]*)"$', line)
	if tline:
		if debug: print "Tupla da linha:", tline.groups()
		dline = tline.group(1)
		simbolo = tline.group(2)
		
		print "Tratando símbolo", simbolo 
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
			mercadoria = tline.group(3)
			vencimento = tline.group(4)
			lote = conv.my_int(tline.group(5))
			settle = conv.my_float(tline.group(6))
			abertura = conv.my_float(tline.group(7))
			high = conv.my_float(tline.group(8))
			low = conv.my_float(tline.group(9))
			last = conv.my_float(tline.group(10))
			vol_contratos = conv.my_long(tline.group(11))
			negocios = conv.my_int(tline.group(12))
			vol_financeiro = conv.my_float(tline.group(13))
			open_int = conv.my_long(tline.group(14))


			if not settle:
				print "AVISO: linha", lin, "inválida: não há valor de fechamento"
				print line
				print tline
			else:
				# Obter vencimento
				if re.match(r'[A-Z]{3}',string.upper(vencimento[0:3])):
					mes = mes_venc[string.upper(vencimento[0:3])]
				else:	mes = vencimento[0:2]
				ano = "20"+vencimento[3:5]
				venc = ano+"-"+mes
				if debug: print "...Vencimento", venc, " da Mercadoria", mercadoria

				# procurar Ativo
				ativo = db.obtem_ativo(debug, familia, venc)
				if not ativo: 
					# ainda não há ativo com o vencimento, criar!
					print "...Vencimento", venc, "não encontrado, inserir Ativo"
					ativo = db.inserir_ativo(debug, familia, venc, None)
					if not ativo: print "!!!!! PROBLEMAS ao criar ativo, para vencimento", venc
				if ativo: 
					print "...Vencimento", venc, "Ativo", ativo.id
					if debug>1:
                        	        	print "\tdata:", data
               		        	        print "\tsímbolo:", simbolo
						print "\tmercadoria:", mercadoria
						print "\tlote:", lote
       		                       		print "\tvencimento:", venc
       				                print "\tcontratos em aberto:", open_int
       				                print "\tvolume de contratos:", vol_contratos
						print "\tvolume financeiro:", vol_financeiro
						print "\tnegócios:", negocios
		                      	        print "\tabertura:", abertura
        		                	print "\tmínimo:", low
			                        print "\tmáximo:", high
        			                print "\túltimo:", last
	                        	        print "\tajuste (settle):", settle
					if vol_contratos > 0:
						vwap = (vol_financeiro / float(vol_contratos)) / float(lote)
					else:   vwap = None
					if debug>1:
               		        	        print "\tvwap:", vwap
			
	
					# verificar se há cotação do ativo para a data 
					cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
					if not cotacao:
						# inserir cotação
						cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
						if cotacao: 
							print "......cotação inserida"
							count_i += 1
					else: 	# já há cotação nesse dia
						# verificar se mudou...
						if (abertura>0 and cotacao.abertura != abertura) or (last>0 and cotacao.ultimo != last) or (settle>0 and cotacao.fechamento != settle) or ((vwap>0 and abs(cotacao.vwap - vwap) >= ativo.tick_size) or high>0 and cotacao.maximo != high) or (low>0 and cotacao.minimo != low) or (negocios>0 and cotacao.negocios != negocios) or (vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (vol_financeiro>0 and cotacao.volume_financeiro != vol_financeiro) or (open_int>0 and cotacao.contratos_aberto != open_int):
							if abertura>0 and cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
							if last>0 and cotacao.ultimo != last: print ".......mudou ultimo",(cotacao.ultimo,last)
							if settle>0 and cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
							if vwap>0 and abs(cotacao.vwap - vwap) >= ativo.tick_size: print ".......mudou vwap",(cotacao.vwap,vwap)
							if high>0 and cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
							if low>0 and cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
							if negocios>0 and cotacao.negocios != negocios: print ".......mudou negocios",(cotacao.negocios,negocios)
							if vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos)
							if vol_financeiro>0 and cotacao.volume_financeiro != vol_financeiro: print ".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro)
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
							if cotacao_nova: 
								print "......cotação atualizada"
								count_u += 1
						else: 
							print "......cotação idêntica já existe na base, ignorando"
							count_p += 1
	line = le_linha(f)

print "FIM"

if len(novos)>0:
        print "Símbolos novos detectados:", novos

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
