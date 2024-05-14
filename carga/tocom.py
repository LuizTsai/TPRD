#!/usr/bin/python3 -u
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re
import db, conv, admin

debug=0
count_i=count_u=count_p=0
data = None
lin = 0 

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


arquivo_log = admin.init("tocom")
programa_id = db.obtem_id_programa(debug, "tocom")
if not programa_id:
	print("PROBLEMAS!!: programa tocom não encontrado na base de dados!")
	# enviar email
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa tocom não encontrado na base de dados!");


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


# Tratar blocos de símbolos (famílias)
line = le_linha(f)
while line: # loop de símbolos/vencimentos
	tline = re.match(r'([^,]+),([^,]+),([^,]+),([^,]+),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]+),([^,]*),([^\r,]*)\r*',line)
	if not tline:
		print("AVISO: linha de dados",lin,"inválida (não tem 12 campos encapsulados em aspas duplas seguidos de vírgula):")
		print(line)
		line = le_linha(f)
		#admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: linha de dados inválida (não tem 12 campos encapsulados em aspas duplas seguidos de vírgula)")
	else:

		# verificar se é Futuro ou Opção
		print("Tratando", tline.groups())
		if tline.group(2).strip() == "21" or tline.group(2).strip() == "22":
			print("...Opção, pulando")
		else:
			# Futuro
			simbolo = tline.group(3).strip()
			# procurar família do símbolo
			familia = db.obtem_familia_programa(debug, programa_id, simbolo)
			if not familia: print("...Símbolo", simbolo, "não encontrado em FamiliaContratos, ignorando!")
			else:
				print("...Símbolo", simbolo, "pertence à família", familia.id, familia.nome.encode('utf-8'))
				db.inserir_programa_familia(debug, programa_id, familia)
				# Obter vencimento
				venc = (tline.group(4).upper())[0:4]+"-"+(tline.group(4).upper())[4:6]
				if debug: print("...Vencimento", venc)
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
					data = (tline.group(1))[0:4]+"-"+(tline.group(1))[4:6]+"-"+(tline.group(1))[6:8]
					abertura = conv.my_float(tline.group(6))
					high = conv.my_float(tline.group(7))
					low = conv.my_float(tline.group(8))
					last = conv.my_float(tline.group(9))
					settle = conv.my_float(tline.group(10))
					vol_contratos = conv.my_long(tline.group(11))
					open_int = conv.my_long(tline.group(12))

					vwap = negocios = vol_financeiro = None

					if debug>1:
						print("\tdata:", data)
						print("\tsímbolo:", simbolo)
						print("\tvencimento:", venc)
						print("\tcontratos em aberto:", open_int)
						print("\tvolume de contratos:", vol_contratos)
						print("\tvolume financeiro:", vol_financeiro)
						print("\tnegocios:", negocios)
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
						if cotacao: print("......cotação inserida")
						count_i += 1
					else: 	# já há cotação nesse dia
						# verificar se mudou...
						if (abertura and abertura>0 and cotacao.abertura != abertura) or (last and last>0 and cotacao.ultimo != last) or (settle and settle>0 and cotacao.fechamento != settle) or (cotacao.vwap != None) or (high and high>0 and cotacao.maximo != high) or (low and low>0 and cotacao.minimo != low) or (cotacao.negocios != None) or (vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (cotacao.volume_financeiro != None) or (open_int and open_int>0 and cotacao.contratos_aberto != open_int):
							if abertura and abertura>0 and cotacao.abertura != abertura: print(".......mudou abertura",(cotacao.abertura,abertura))
							if last and last>0 and cotacao.ultimo != last: print(".......mudou ultimo",(cotacao.ultimo,last))
							if settle and settle>0 and cotacao.fechamento != settle: print(".......mudou fechamento",(cotacao.fechamento,settle))
							if cotacao.vwap != None: print(".......mudou vwap",(cotacao.vwap,vwap))
							if high and high>0 and cotacao.maximo != high: print(".......mudou maximo",(cotacao.maximo,high))
							if low and low>0 and cotacao.minimo != low: print(".......mudou minimo",(cotacao.minimo,low))
							if cotacao.negocios != None: print(".......mudou negocios",(cotacao.negocios,negocios))
							if vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print(".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos))
							if cotacao.volume_financeiro != None: print(".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro))
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

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
