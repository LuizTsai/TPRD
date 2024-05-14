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
lin = 0

ignorar = []
novos = []

programa = commands.getoutput("basename "+sys.argv[0]+" | sed \"s/\.py//\"")

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


arquivo_log = admin.init(programa)
programa_id = db.obtem_id_programa(debug, programa)
if not programa_id:
        print "PROBLEMAS!!: programa",programa,"não encontrado na base de dados!"
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa "+programa+" não encontrado na base de dados!");


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


# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line: # loop de símbolos/vencimentos
	tline = re.match(r'([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]*),,,([^,]*),([^,]*),([^,]+),[^,]*,[^,]*,,,,', line)
#([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]+),([^,]*),([^\r,]*)\r*',line)
	if not tline:
		print "PROBLEMAS: linha de dados inválida (não tem 12 campos encapsulados em aspas duplas seguidos de vírgula):"
		print line
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de dados inválida (não tem 12 campos encapsulados em aspas duplas seguidos de vírgula)")
	else:

		# verificar se é Futuro ou Opção
		print "Tratando", tline.groups()
		if string.strip(tline.group(4)) == "C" or string.strip(tline.group(4)) == "P":
			print "...Opção, pulando"
		else:
			# Futuro
			simbolo = string.strip(tline.group(2))
			# procurar família do símbolo
			familia = db.obtem_familia_programa(debug, programa_id, simbolo)	# Londres
			if not familia: familia = db.obtem_familia(debug, 12, simbolo)	# Paris

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
				# Obter vencimento
				venc = "20"+(string.upper(tline.group(3)))[3:5]+"-"+mes_venc[(string.upper(tline.group(3)))[0:3]]
				if debug: print "...Vencimento", venc
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
# 1=Trading date, 2=commodity (TRS contract code), 3=expiry, 4=contract type, 5=exercise price, 6=volume, 7=previous day's volume, 8=previous day's open interest, 9=opening transaction, 10=daily high, 11=daily low, 12=settlement price
					data = commands.getoutput("date -d "+tline.group(1)+" +%F")
					abertura = conv.my_float(tline.group(9))
					high = conv.my_float(tline.group(10))
					low = conv.my_float(tline.group(11))
					settle = conv.my_float(tline.group(12))
					vol_contratos = conv.my_long(tline.group(6))
					prev_open_int = conv.my_long(tline.group(8))
					if prev_open_int==0: prev_open_int = None
					
					vwap = last = vol_financeiro = negocios = open_int = None

					prev_vol = conv.my_long(tline.group(7))
					if prev_vol==0: prev_vol = None

					if debug>1:
		                                print "\tdata:", data
                		                print "\tsímbolo:", simbolo
                                		print "\tvencimento:", venc
                		                print "\tvolume de contratos:", vol_contratos
                		                print "\tvolume financeiro:", vol_financeiro
		                                print "\tnegocios:", negocios
		                                print "\tabertura:", abertura
                		                print "\tmínimo:", low
		                                print "\tmáximo:", high
                		                print "\tvwap:", vwap
                		                print "\túltimo:", last
		                                print "\tajuste (settle):", settle
                		                print "\tprev_vol:", prev_vol
                		                print "\tprev contratos em aberto:", prev_open_int

					# verificar se há cotação do ativo para a data 
					cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
					if not cotacao:
						# inserir cotação
						cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
						if cotacao: print "......cotação inserida"
						count_i += 1
					else: 	# já há cotação nesse dia
						# verificar se mudou...
						if (abertura>0 and cotacao.abertura != abertura) or (cotacao.ultimo != None) or (settle>0 and cotacao.fechamento != settle) or (cotacao.vwap != None) or (high>0 and cotacao.maximo != high) or (low>0 and cotacao.minimo != low) or (cotacao.negocios != None) or (vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (cotacao.volume_financeiro != None):
							if abertura>0 and cotacao.abertura != abertura: print ".......mudou abertura",(cotacao.abertura,abertura)
							if cotacao.ultimo != None: print ".......mudou ultimo",(cotacao.ultimo,last)
							if settle>0 and cotacao.fechamento != settle: print ".......mudou fechamento",(cotacao.fechamento,settle)
							if cotacao.vwap != None: print ".......mudou vwap",(cotacao.vwap,vwap)
							if high>0 and cotacao.maximo != high: print ".......mudou maximo",(cotacao.maximo,high)
							if low>0 and cotacao.minimo != low: print ".......mudou minimo",(cotacao.minimo,low)
							if cotacao.negocios != None: print ".......mudou negocios",(cotacao.negocios,negocios)
							if vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print ".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos)
							if cotacao.volume_financeiro != None: print ".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro)
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
                                        	# verificar volume e open interest
	                                        if cotacao_vespera.volume_contratos != prev_vol or cotacao_vespera.contratos_aberto != open_int:
        	                                        if prev_vol>0 and cotacao_vespera.volume_contratos != prev_vol: print ".......mudou volume da véspera",(cotacao_vespera.volume_contratos,prev_vol)
                	                                if open_int>0 and cotacao_vespera.contratos_aberto != open_int: print ".......mudou contratos em aberto da véspera",(cotacao_vespera.contratos_aberto,open_int)
                        	                        cotacao_vespera.volume_contratos = prev_vol
                                	                cotacao_vespera.contratos_aberto = open_int
                                        	        cotacao_vespera_atualizada = db.update_cotacao_ativo(debug, ativo, cotacao_vespera)
                                                	if cotacao_vespera_atualizada: print "......cotação da véspera atualizada"
	                                else: print ".....Cotação não encontrada para a véspera"

	line = le_linha(f)

print "FIM"

if len(novos)>0:
        print "Símbolos novos detectados:", novos
admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
