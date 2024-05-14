#!/usr/bin/python -u
# coding=UTF8
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
ignorar = [ "CPPL" ]
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


arquivo_log = admin.init("afet")
programa_id = db.obtem_id_programa(debug, "afet")
if not programa_id:
        print "PROBLEMAS!!: programa afet não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa afet não encontrado na base de dados!");


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


def pular_simbolo(debug):
	global line
	line = le_linha(f)
	tline = re.match(r'"([^"]+)",,,,,,,,,', line)
	while not tline and line:
		line = le_linha(f)
		tline = re.match(r'"([^"]+)",,,,,,,,,', line)





# verificar linha de título 
line = le_linha(f)
if "Market Prices (" in line:
	if debug: print "Arquivo OK"
	# obter data de referencia
	tdata = re.search(r'"Market Prices +\(([^\)]+)\)"', line)
	if tdata:
		str_data = tdata.group(1)
		if debug>1: print "String de data:", str_data
		data = commands.getoutput("date -d \""+str_data+"\" +%F")
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
	print "PROBLEMAS: Arquivo inválido: título \"Commodities Market Statistics for\" não encontrado!"
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: título \"Commodities Market Statistics for\" não encontrado!")

## Verificar linha de cabeçalho 
#line = le_linha(f)	# pular "Interest on Initial Margin"
#line = le_linha(f)	# pular "Total Margin on Deposit"
#
## Inicializar estrutura de moedas
#ret = db.carrega_moedas(debug)
#if ret <= 2:
#        print "PROBLEMAS na carga de moedas, carregou", ret,"moedas!"
#	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de moedas, carregou "+str(ret)+" moedas!")
#
## Inicializar estrutura de unidades
#ret = db.carrega_unidades(debug)
#if ret <= 2:
#        print "PROBLEMAS na carga de unidades, carregou", ret,"unidades!"
#	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS na carga de unidades, carregou "+str(ret)+" unidades!")


# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line: # loop de símbolos/vencimentos
	tline = re.match(r'"([^"]+)",,,,,,,,,', line)
	if not tline:
		if debug: print "Símbolo esperado não encontrado, final do arquivo?"
		line = le_linha(f)
	else:
		simbolo = tline.group(1)
		if debug>1: print "Tupla da linha:", tline.groups()
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
			pular_simbolo(debug)
		else:
			print "...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8')
			db.inserir_programa_familia(debug, programa_id, familia)
			line = le_linha(f)	# agora deve ser o cabeçalho
			if "\"Contract\",\"Previous Settlement Prc\",\"Open Price\",\"High Price\",\"Low Price\",\"Close Price\",\"Change On Day\",\"Settlement Price\",\"Traded Vol\",\"Open Interest\"" not in line:
				print "PROBLEMAS: Arquivo inválido: linha de cabeçalho não encontrada!", "("+str(lin)+")", line
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Arquivo inválido: linha de cabeçalho não encontrada! (linha="+str(lin)+")")
			line = le_linha(f)
			tline = re.match(r'([^,]+),([^,]+),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]+),([^,]+),([^,]+)',line)
			while tline:
				if not tline:
					print "PROBLEMAS: Linha de dados não tem 10 campos:", "(linha="+str(lin)+")", line
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: Linha de dados não tem 10 campos (linha="+str(lin)+")")
				if debug>1: print "Tupla:", tline.groups()
				tsimb = re.match(r'^(\S+)\s+([A-z]+)\s(\d+)' , re.sub(r'\"', "", tline.group(1)))
				if debug>1: print "Mercadoria/Vencimento:", tsimb.groups()
				mercadoria = tsimb.group(1)
				# Obter vencimento
				mes = mes_venc[string.upper(tsimb.group(2))]
				ano = "20"+tsimb.group(3)
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
					#Parsear o resto dos campos
					# 2=Previous Settle, 3=Open, 4=High, 5=Low, 6=Close, 7=Change, 8=Settle, 9=Vol, 10=Open Interest
					settle = conv.my_float(re.sub(r'\"', "", tline.group(8)))
					abertura = conv.my_float(re.sub(r'\"', "", tline.group(3)))
					last = conv.my_float(re.sub(r'\"', "", tline.group(6)))
					high = conv.my_float(re.sub(r'\"', "", tline.group(4)))
					low = conv.my_float(re.sub(r'\"', "", tline.group(5)))
					vol_contratos = conv.my_long(re.sub(r'\"', "", tline.group(9)))
					open_int = conv.my_long(re.sub(r'\"', "", tline.group(10)))
					vwap = negocios = vol_financeiro = None
					if debug>1:
	                                	print "\tdata:", data
	               		                print "\tsímbolo:", simbolo
        	                       		print "\tvencimento:", venc
               			                print "\tcontratos em aberto:", open_int
               			                print "\tvolume de contratos:", vol_contratos
	                        	        print "\tabertura:", abertura
               		                	print "\tmínimo:", low
		                                print "\tmáximo:", high
        	       		                print "\túltimo:", last
               			                print "\tvwap:", vwap
	                	                print "\tajuste (settle):", settle
	
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
						if (abertura>0 and cotacao.abertura != abertura) or (last>0 and cotacao.ultimo != last) or (settle>0 and cotacao.fechamento != settle) or (high>0 and cotacao.maximo != high) or (low>0 and cotacao.minimo != low) or (vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (open_int>0 and cotacao.contratos_aberto != open_int):
							if abertura>0 and cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
							if last>0 and cotacao.ultimo != last: print ".......mudou ultimo",(cotacao.ultimo,last)
							if settle>0 and cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
							if high>0 and cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
							if low>0 and cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
							if vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos)
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
				tline = re.match(r'([^,]+),([^,]+),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]+),([^,]+),([^,]+)',line)

print "FIM"

if len(novos)>0:
        print "Símbolos novos detectados:", novos

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
