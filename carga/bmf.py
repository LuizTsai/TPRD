#!/usr/bin/python -u
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, string
import db, conv, admin
import subprocess

debug=0
count_i=count_u=count_p=0
data = None
lin=0

mes_venc = {
                "F": "01",
                "G": "02",
                "H": "03",
                "J": "04",
                "K": "05",
                "M": "06",
                "N": "07",
                "Q": "08",
                "U": "09",
                "V": "10",
                "X": "11",
                "Z": "12"
        }

ignorar = [ "AUD", "BRI", "BSE", "CAD", "CHF", "CLP", "CNY", "CR1", "DAP", "DCO", "DDI", "DDM", "DI1", "DOL", "DR1", "EUR", "FRC", "FRO", "FRP", "GBP", "HSI", "IAP", "IGM", "IND", "IR1", "ISP", "JPY", "JSE", "KR1", "MIX", "MXN", "NZD", "OC1", "RSP", "TRY", "T10", "WDO", "WEU", "WIN", "ZAR" ]
novos = []


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


def file_len(fname):
	p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
	result, err = p.communicate()
	if p.returncode != 0:
		raise IOError(err)
	return int(result.strip().split()[0])

qtd_linhas = file_len(nome_arq)

arquivo_log = admin.init("bmf")
programa_id = db.obtem_id_programa(debug, "bmf")
if not programa_id:
        print("PROBLEMAS!!: programa bmf não encontrado na base de dados!")
        # enviar email
        admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: programa bmf não encontrado na base de dados!");



print("Tratando arquivo",nome_arq)
try: 
	f = open(nome_arq)
except e:
	print("Não foi possível abrir arquivo",nome_arq,"(",e,")")
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "Não foi possível abrir arquivo"+nome_arq+"("+e+")")


def le_linha(arq):
	global lin
	lin = lin + 1
	linha = re.sub(r'\n$', "", arq.readline())
	if debug: print("("+str(lin)+"):", linha)
	return linha

'''
https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/commodities/

BGI: Boi Gordo (Contrato = 330 Arrobas; Cotação = R$/Arroba)
Mercado Futuro
              Contratos     Negócios          Contratos                       Preço de      Preço      Preço       Preço      Último        Variação em            Última Oferta       Última Oferta
Vencimento                                                    Volume                                                                 Ajuste
             em Aberto     Realizados        Negociados                       Abertura     Mínimo     Máximo       Médio       Preço             Pontos               de Compra            de Venda
F24                  41             8                18      1.306.800          220,00      220,00      220,00     220,00     220,00    233,10           0,00            220,00               223,85
J24                    -                -                -              -              -          -           -          -          - 245,00            -8,40↓                 -             245,00
K24                    1                1                1      77.534          234,95      234,95      234,95     234,95      234,95 239,80             0,00            230,00              234,95
Q23                2.581           152              499      35.771.274          217,95     216,00      218,45      217,23     216,35   216,45          -0,30↓            216,05              216,50
U23                1.797          200               499 34.693.032               210,50    208,00       212,90     210,68     208,90 208,65             -2,55↓            208,25             209,25
V23               15.533         2.208             6.291 441.132.549            214,00      209,60      216,00     212,48      211,00 210,60            -3,50↓            210,70              210,95
X23               1.994            139              349      25.253.019          219,20     216,00      222,30      219,26     216,00   216,55          -2,60↓            216,00              216,95
Z23                1.317           121              357 26.262.836               222,75     218,85      224,50     222,92      219,35   220,15          -3,05↓            219,25             220,40

OZ1: Ouro (Contrato = 250g; Cotação = R$/g)
Mercado Disponível
                  Negócios           Contratos                    Preço de       Preço           Preço           Preço             Último          Variação em          Oferta de        Última Oferta de
Código                                         Volume
                 Realizados         Negociados                    Abertura      Mínimo          Máximo           Médio              Preço               Pontos           Compra                   Venda
OZ1                       8                     9 676.428             301,00      300,01            301,30       300,94             301,10                0,87↑            301,09                  301,99

OZ1: Ouro (Contrato = 250g; Cotação = R$/g)
Mercado Futuro
               Contratos em        Negócios       Contratos                 Preço de      Preço       Preço       Preço           Último        Variação em             Última Oferta      Última Oferta
Vencimento                                                  Volume                                                                       Ajuste
                     Aberto       Realizados     Negociados                 Abertura     Mínimo      Máximo       Médio            Preço             Pontos                de Compra           de Venda
OZ1U23                        -            -                 -         -           -            -            -            -            - 302,88                1,96↑                 -                  -
OZ1V23                        -            -                 -         -           -            -            -            -            - 305,82                1,97↑                 -                  -


'''

while 1:
	line = le_linha(f)

	if lin == qtd_linhas:
		break

	tsymb = re.match(r'([A-Za-z0-9]{3}): ([A-Z].*)', line)
	if not tsymb:
		continue
	else:
		simbolo = tsymb.group(1)
		desc = tsymb.group(2)

	mercado = le_linha(f)
	if mercado != "Mercado Futuro" and mercado != "Mercado Disponível":
		mercado = le_linha(f)
		if mercado != "Mercado Futuro" and mercado != "Mercado Disponível":
			if debug: 
				print("Mercado não é Disponível ou Futuro, ignorando")
			continue

	# descartando cabecalhos
	cab = le_linha(f)
	cab = le_linha(f)
	cab = le_linha(f)

	while 1:
		# agora temos a lista dos contratos (ativos) da família, cada um com um vencimento
		line = le_linha(f)
		tline = re.match(r'([A-Z]{1}\d{2})\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)

		if not tline:
			tline = re.match(r'([A-Z0-9]{4}\d{2})\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
			if not tline:
				break

			venc = conv.my_str("20" + tline.group(1)[4:6]+"-"+ mes_venc[tline.group(1)[3:4]]+"-01")
		else:
			venc = conv.my_str("20" + tline.group(1)[1:3]+"-"+ mes_venc[tline.group(1)[0:1]]+"-01")

		print(line)

		# ler próximo vencimento


		# BDI_00_20230815
		data = conv.my_str(nome_arq[-12:-8]+"-"+nome_arq[-8:-6]+"-"+nome_arq[-6:-4]) 
		cod_merc = conv.my_str(tsymb.group(1).strip()) 

		#venc = conv.my_str("20" + tline.group(1)[1:3]+"-"+ mes_venc[tline.group(1)[0:1]]+"-01") 

		vol_real = conv.my_float(tline.group(5).strip().replace('.','')) 
		vol_dol = conv.my_float(tline.group(5).strip().replace('.',''))
		open_int = conv.my_long(tline.group(2).strip().replace('.','')) 
		negocios = conv.my_int(tline.group(3).strip().replace('.','')) 
		vol_contratos = conv.my_long(tline.group(4).strip().replace('.',''))
		abertura = conv.my_float(tline.group(6).strip().replace(',','.')) 
		low = conv.my_float(tline.group(7).strip().replace(',','.')) 
		high = conv.my_float(tline.group(8).strip().replace(',','.')) 
		vwap = conv.my_float(tline.group(9).strip().replace(',','.')) 
		last = conv.my_float(tline.group(10).strip().replace(',','.'))
		fechamento = conv.my_float(tline.group(11).strip().replace(',','.'))
		settle = conv.my_float(tline.group(12).strip().replace(',','.').replace('↓','').replace('↑','')) 
		casas_dec = 2 
		casas_dec_set = 2

		# corrigir valores pelo número de casas decimais
		#abertura = abertura / (10 ** casas_dec)
		#low = low / (10 ** casas_dec)
		#high = high / (10 ** casas_dec)
		#vwap = vwap / (10 ** casas_dec)
		#last = last / (10 ** casas_dec)
		#fechamento = fechamento / (10 ** casas_dec)
		#settle = settle / (10 ** casas_dec_set)
		
		if True:
			print("\tdata:", data)
			print("\tcódigo mercadoria:", cod_merc)
			print("\tvencimento:", venc)
			print("\tvolume em reais:", vol_real)
			print("\tvolume em dolars:", vol_dol)
			print("\tcontratos em aberto:", open_int)
			print("\tnegócios:", negocios)
			print("\tvolume de contratos:", vol_contratos)
			print("\tabertura:", abertura)
			print("\tmínimo:", low)
			print("\tmáximo:", high)
			print("\tvwap", vwap)
			print("\túltimo:", last)
			print("\tfechamento(?):", fechamento)
			print("\tajuste (settle):", settle)

		if venc[0]=="0":
			print("AVISO: vencimento zerado! - código mercadoria:",cod_merc)
			print(line)
			print("\tdata:", data)
			print("\tcódigo mercadoria:", cod_merc)
			print("\tvencimento:", venc)
			print("\tvolume em reais:", vol_real)
			print("\tvolume em dolars:", vol_dol)
			print("\tcontratos em aberto:", open_int)
			print("\tnegócios:", negocios)
			print("\tvolume de contratos:", vol_contratos)
			print("\tabertura:", abertura)
			print("\tmínimo:", low)
			print("\tmáximo:", high)
			print("\tvwap", vwap)
			print("\túltimo:", last)
			print("\tfechamento(?):", fechamento)
			print("\tajuste (settle):", settle)
		else:
			print("Código Mercadoria:",cod_merc,"Vencimento:", venc,"Settle:", settle,"Volume:", vol_contratos)
			# procurar família do símbolo
			familia = db.obtem_familia_programa(debug, programa_id, cod_merc)
			if familia:
				print(familia.densidade)
				print(familia.unidade_contrato_secundaria)
			if not familia:
				try:
					i = ignorar.index(cod_merc)
					print("...Símbolo", cod_merc, "não encontrado em FamiliaContratos, mas está na lista de símbolos a ignorar")
				except ValueError as e:
					try:
						i = novos.index(cod_merc)
					except ValueError as e:
						novos.append(cod_merc)
						print("AVISO: Símbolo", cod_merc, "não encontrado em FamiliaContratos, nem na lista de símbolos a ignorar")
			else: 
				print("...Mercadoria", cod_merc, "pertence à família", familia.id, familia.nome.encode('utf-8'))
				db.inserir_programa_familia(debug, programa_id, familia)
				# procurar Ativo com o vencimento
				ativo = db.obtem_ativo(debug, familia, venc[0:7])
				if not ativo:
					# ainda não há Ativo com o vencimento, criar!
					print("...Vencimento", venc, "não encontrado, inserir Ativo")
					data_vencimento = venc
					#ativo = db.inserir_ativo(debug, familia, venc[0:7], data_vencimento)
					ativo = db.inserir_ativo(debug, familia, venc[0:7], None)
					ativo.imprime()
					if not ativo:
						print("!!!!!!PROBLEMAS ao criar ativo para vencimento",venc)
				if ativo: 
					print("...Vencimento",venc,"Ativo", ativo.id)
					if ativo.moeda_cotacao == 1:
						vol_financeiro = vol_real
					else: vol_financeiro = vol_dol
					# verificar se já há cotação do ativo para a data na base
					cotacao = db.obtem_cotacao_ativo( debug, ativo, data)
					if not cotacao:
						# inserir cotação
						cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int)
						if cotacao: print("......cotação inserida")
						count_i += 1
					else:	# já há cotação nesse dia
						# verificar se mudou...
						if (abertura and abertura>0 and cotacao.abertura != abertura) or (last and last>0 and cotacao.ultimo != last) or (settle and settle>0 and cotacao.fechamento != settle) or (vwap and vwap>0 and cotacao.vwap != vwap) or (high and high>0 and cotacao.maximo != high) or (low and low>0 and cotacao.minimo != low) or (negocios and negocios>0 and cotacao.negocios != negocios) or (vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos) or (vol_financeiro and vol_financeiro>0 and cotacao.volume_financeiro != vol_financeiro) or (open_int and open_int>0 and cotacao.contratos_aberto != open_int):
							if abertura and abertura>0 and cotacao.abertura != abertura: print(".......mudou abertura",(cotacao.abertura,abertura))
							if last and last>0 and cotacao.ultimo != last: print(".......mudou ultimo",(cotacao.ultimo,last))
							if settle and settle>0 and cotacao.fechamento != settle: print(".......mudou fechamento",(cotacao.fechamento,settle))
							if vwap and vwap>0 and cotacao.vwap != vwap: print(".......mudou vwap",(cotacao.vwap,vwap))
							if high and high>0 and cotacao.maximo != high: print(".......mudou maximo",(cotacao.maximo,high))
							if low and low>0 and cotacao.minimo != low: print(".......mudou minimo",(cotacao.minimo,low))
							if negocios and negocios>0 and cotacao.negocios != negocios: print(".......mudou negocios",(cotacao.negocios,negocios))
							if vol_contratos and vol_contratos>0 and cotacao.volume_contratos != vol_contratos: print(".......mudou volume_contratos",(cotacao.volume_contratos,vol_contratos))
							if vol_financeiro and vol_financeiro>0 and cotacao.volume_financeiro != vol_financeiro: print(".......mudou volume_financeiro",(cotacao.volume_financeiro,vol_financeiro))
							if open_int and open_int>0 and cotacao.contratos_aberto != open_int: print(".......mudou contratos_aberto",(cotacao.contratos_aberto,open_int))
							# mudou, atualizar
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

print("FIM")

if len(novos)>0:
        print("Símbolos novos detectados:", novos)

#db.close()

admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
db.close()
