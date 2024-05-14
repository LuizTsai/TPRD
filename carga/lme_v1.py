#!/usr/bin/python3 -u
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys, re, subprocess 
import db, conv, admin

moedas = {}

debug=0
count_i=count_u=count_p=0
data = None
ignorar = []
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



def trata_contrato(debug, familia, contrato, data):
	global count_i,count_u,count_p
	if debug: print("\n..Tratando contrato", contrato, "na família", familia.nome, "para data", data)
	if contrato[1] is None:
		print("...contrato", contrato[0], "sem valores, ignorando")
		return
	if re.match(r'Dec \d+', contrato[0]):
		print("....contrato com data de vencimento, ignorando")

	else:
		if not re.match(r'^\d+-months$', contrato[0]):
			if re.match(r'^Cash$', contrato[0]):
				delta = 0
			else:
				print("PROBLEMAS: contrato", contrato[0], "não obedece à máscara \"<n>-months\"")
				return
		else:	delta = conv.my_int(re.match(r'^(\d+)-months$', contrato[0]).group(1))
		if debug: print("...contrato com delta de vencimento", delta)
		ativo = db.obtem_ativo(debug, familia, delta, "D")
		if not ativo:
			print("....inserindo contrato com delta", delta)
			familia.imprime()
			ativo = db.inserir_ativo(debug, familia, None, None, delta, "D")
			if not ativo: print("PROBLEMAS ao criar ativo com delta", delta)
		if ativo:
			abertura = vwap = last = high = low = negocios = vol_contratos = vol_financeiro = open_int = None
			compra = contrato[1]
			venda = contrato[2]
			settle = venda
			if debug>1:
				print("\tdata:", data)
				print("\tsímbolo", familia.cod_arq)
				print("\tdelta de vencimento:", ativo.delta_vencimento)
				print("\tcontratos em aberto:", open_int)
				print("\tvolume de contratos:", vol_contratos)
				print("\tabertura:", abertura)
				print("\tmínimo:", low)
				print("\tmáximo:", high)
				print("\túltimo:", last)
				print("\tvwap:", vwap)
				print("\tajuste (settle):", settle)
				print("\tcompra:", compra)
				print("\tvenda:", venda)
			 # verificar se há cotação do ativo para a data
			cotacao = db.obtem_cotacao_ativo(debug, ativo, data)
			if not cotacao:
				# inserir cotação
				cotacao = db.inserir_cotacao_ativo(debug, ativo, data, abertura, last, settle, vwap, high, low, negocios, vol_contratos, vol_financeiro, open_int, compra, venda)
				if cotacao:
					print("......cotação inserida")
					count_i += 1
			else:   # já há cotação nesse dia
				# verificar se mudou...
				if (compra and compra>0 and cotacao.compra != compra) or (venda and venda>0 and cotacao.venda != venda) or (settle and settle>0 and cotacao.fechamento != settle):
					if compra and compra>0 and cotacao.compra != compra: print(".......mudou compra",(cotacao.compra,compra))
					if venda and venda>0 and cotacao.venda != venda: print(".......mudou venda",(cotacao.venda,venda))
					if settle and settle>0 and cotacao.fechamento != settle: print(".......mudou fechamento",(cotacao.fechamento,settle))
					# mudou, atualizar cotação
					cotacao.compra = compra
					cotacao.venda = venda
					cotacao.fechamento = settle
					cotacao_nova = db.update_cotacao_ativo(debug, ativo, cotacao)
					if cotacao_nova:
						print("......cotação atualizada")
						count_u += 1
				else:
					print("......cotação idêntica já existe na base, ignorando")
					count_p += 1

def trata_arquivo(debug, arquivo_log, nome_arq, programa_id, linha):

	# Obter famílias da LME
	familias = db.familias_subbolsa(debug, 13)
	if not familias:
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS!!: não foram encontradas famílias para a subbolsa LME (18) na base de dados!");
	if debug>2: print(familias.keys())


	# remover quebras de linha
	linha = re.sub(r'\n', "", linha)
	# remover excesso de whitespace
	linha = re.sub(r'\s\s+', "", linha)
	# remover tranqueira 
	linha = re.sub(r'^.*<html>', "<html>", linha)
	linha = re.sub(r'<td>\&nbsp;</td>', "", linha)
	linha = re.sub(r'<tr></tr>', "", linha)
	linha = re.sub(r'<font[^>]*>', "", linha)
	linha = re.sub(r'</font>', "", linha)
	linha = re.sub(r' align="[^"]+"', "", linha)
	linha = re.sub(r'<b>', "", linha)
	linha = re.sub(r'</b>', "", linha)
	linha = re.sub(r' class="stocks-heading"', "stocks-heading", linha)
	linha = re.sub(r' class="[^"]+"', "", linha)
	linha = re.sub(r'\&nbsp;', "", linha)
	linha = re.sub(r' >', ">", linha)
	linha = re.sub(r'> ', ">", linha)
	linha = re.sub(r'\r', "", linha)
	linha = re.sub(r' scope="col"', "", linha)
	linha = re.sub(r'<span id[^>]*>', "", linha)
	linha = re.sub(r'</span>', "", linha)
	linha = re.sub(r'Stocks and prices for *', "", linha)
	linha = re.sub(r'Daily prices for *', "", linha)
	linha = re.sub(r'<h2>Free trading reports</h2>', "", linha)
	linha = re.sub(r'<h2>LME Education</h2>', "", linha)
	linha = re.sub(r'<h2>LME[^\d]+</h2>', "", linha)
	linha = re.sub(r'<h2>The official LME Guide</h2>', "", linha)
	
	i = 0
	fim = len(linha)
	
	if debug>2:	print("Dados tem",fim,"caracteres")
	
	
	# obter Metal
	i = linha.find("<title>London Metal Exchange: ")
	if i == -1:
		print("PROBLEMAS: <title> esperado não encontrado")
		print(linha)
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: <title> esperado não encontrado")
	if debug>2: print("Título encontrado em",i)
	i = i + len("<title>London Metal Exchange: ")
	f = linha.find("</title>", i)
	if f == -1:
		print("PROBLEMAS: terminador (\"</title>\") do título não encontrado")
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: terminador (\"</title>\") do título não encontrado")
	metal = linha[i:f].upper()
	if debug: print("Metal encontrado no título:", metal)
	if metal in familias.keys():
		print("Arquivo de um único metal:", metal)
		unico = familias[metal]
		if debug: unico.imprime()
	else:
		print(metal, "não é uma família da LME, arquivo contém vários metais")
		unico = None
	
	# obter Data
	f = f + len("</title>")
	i = linha.find("<h2stocks-heading>", f)
	if i == -1:
		print("PROBLEMAS: <h2> não encontrado")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: \"<h2>\"  não encontrado")
	i = i + len("<h2stocks-heading>")
	f = linha.find("</h2>", i)
	if f == -1:
		print("PROBLEMAS: terminador (\"</h2>\") da Data não encontrado")
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: terminador (\"</h2>\") da Data não encontrado")
	str_data = linha[i:f]
	if not re.match(r'^[0-9]+ [a-zA-Z]+ [0-9]+$', str_data):
		print("PROBLEMAS: data não obedece ao padrão <dd> <mês> <aaaa>", str_data)
		print(linha[i:f+50])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: data não obedece ao padrão <dd> <mês> <aaaa>:'"+str_data+"'")
	
	if debug>2: print("Data encontrada:", str_data)
	data = subprocess.check_output(["date", "-d "+str_data," +%F"]).decode("utf-8")
	print("Arquivo contém dados de", data)
	
	
	### Obter dados
	
	f = f + len("</h2>")
	i = linha.find("<div id=\"ctl01_maincontent_0_ctl00_pnlPrices\"", f)
	if i == -1:
		print("PROBLEMAS: div com dados (id=\"ctl01_maincontent_0_ctl00_pnlPrices\") não encontrado")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: div com dados (id=\"ctl01_maincontent_0_ctl00_pnlPrices\") não encontrado")
	f = f + len("<div id=\"ctl01_maincontent_0_ctl00_pnlPrices\"")
	i = linha.find("<thead>", f)
	if i == -1:
		print("PROBLEMAS: <thead> não encontrado")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: <thead> não encontrado")
	f = i + len("<thead>")
	fim_header = linha.find("</thead>", f)
	
	# obter colunas da tabela
	colunas = []
	i = linha.find("<th>Contract</th>", f)
	if i == -1:
		print("PROBLEMAS: coluna \"Contract\" (deveria ser a primeira coluna) não encontrada")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: coluna \"Contract\" (deveria ser a primeira coluna) não encontrada")
	f = i + len("<th>Contract</th>")
	if unico:
		colunas.append([metal])
		# próxima coluna deve ser "Price"
		i = linha.find("<th>Price</th>", f)
		if i == -1:
			print("PROBLEMAS: coluna \"Price\" (deveria ser a segunda coluna) não encontrada")
			print(linha[f:fim])
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: coluna \"Price\" (deveria ser a segunda coluna) não encontrada")
		f = i + len("<th>Price</th>")
	else:
		# colunas contém metais
		if debug: print("\nProcurando metais nas colunas da tabela...")
		n_metais = 0
		colunas = []
		if fim_header == -1:
			print("PROBLEMAS: fim de header de tabela (</thead>) não encontrado")
			print(linha[f:fim])
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de header de tabela (</thead>) não encontrado")
		while f < fim_header:
			i = linha.find("<th>", f)
			if i == -1 or i > fim_header:
				if n_metais == 0:
					print("PROBLEMAS: não foram encontrados metais no header da tabela")
					print(linha[f:fim_header])
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: não foram encontrados metais no header da tabela")
				# acabaram as colunas no header
				f = fim_header
			else:
				f = i + len("<th>")
				i = linha.find("</th>", f)
				if i == -1:
					print("PROBLEMAS: final de header de coluna (</th>) não encontrado")
					print(linha[f,fim_header])
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: final de header de coluna (</th>) não encontrado")
				colunas.append([linha[f:i].upper()])
				print("..Achou metal ("+str(n_metais)+")", colunas[n_metais][0])
				try:
					print("....familia", familias[colunas[n_metais][0]].id, familias[colunas[n_metais][0]].nome)
				except KeyError as e:
					print("...\nAVISO: Metal", colunas[n_metais][0], "não está nas famílias da LME")
				n_metais = n_metais + 1
				f = i + len("</th>")	
		print("Encontrados", n_metais, "metais:", colunas)
	
	# Examinar linhas da tabela
	f = fim_header
	i = linha.find("<tbody>", f)
	if i == -1:
		print("PROBLEMAS: início do corpo da tabela (<tbody>) não encontrado")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS:  início do corpo da tabela (<tbody>) não encontrado")
	f = i + len("<tbody>")	
	fim_body = linha.find("</tbody>", f)
	if fim_body == -1:
		print("PROBLEMAS: fim da tabela (</tbody>) não encontrado")
		print(linha[f:fim])
		admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim da tabela (</tbody>) não encontrado")
	
	# Varrer contratos
	n_contratos = 0
	if debug: print("\nVarrendo linhas da tabela em busca de contratos...")
	while f < fim_body:
		# Primeira linha de contrato deve ser "Buyer"
		i = linha.find("<tr><td>", f)
		if i == -1:
			print("PROBLEMAS: início de linha da tabela (<tr><td>) não encontrado")
			print(linha[f:fim])
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: início de linha da tabela (<tr><td>) não encontrado")
		f = i + len("<tr><td>")
		i = linha.find("</td>", f)
		if i == -1:
			print("PROBLEMAS: fim de campo (</td>) não encontrado")
			print(linha[f:fim])
			admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de campo (</td>) não encontrado")
		contrato = re.match(r'^(.*) Buyer.*', linha[f:i])
		if not contrato:
			i = linha.find("</tr>", f)
			print("AVISO: Contrato de compra (Buyer) não encontrado, pulando linha",linha[f:i])
			f = i + len("</tr>")
		else:
			if debug: print("\n..Contrato ("+linha[f:i]+"):",contrato.group(1))
			f = i  + len("</td>")
			fim_linha = linha.find("</tr>", f)
			if fim_linha == -1:
				print("PROBLEMAS: fim de linha de contrato",contrato.group(1),"não encontrado")
				print(linha[f:fim])
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de linha de contrato "+contrato.group(1)+" não encontrado")
			# varrer colunas com valores
			col = 0
			while f<fim_linha:
				i = linha.find("<td>", f)
				if i > -1:
					# obter valor
					f = i + len("<td>")
					i = linha.find("</td>", f)
					if i == -1:
						print("PROBLEMAS: fim de campo (</td>) não encontrado")
						print(linha[f:fim])
						admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de campo (</td>) não encontrado")
					valor = conv.my_float(linha[f:i])	
					if debug: print("....Coluna", col, colunas[col][0], ", valor:", valor,"("+linha[f:i]+")" )
					colunas[col].append([contrato.group(1), valor])
					col = col + 1
				f = i + len("</td>")
			if debug >2: print(colunas)
			f = fim_linha + len("</tr>")
	
	
			# Segunda linha de contrato deve ser "Seller"
			i = linha.find("<tr><td>", f)
			if i == -1:
				print("PROBLEMAS: início de linha da tabela (<tr><td>) não encontrado")
				print(linha[f:fim])
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: início de linha da tabela (<tr><td>) não encontrado")
			f = i + len("<tr><td>")
			i = linha.find("</td>", f)
			if i == -1:
				print("PROBLEMAS: fim de campo (</td>) não encontrado")
				print(linha[f:fim])
				admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de campo (</td>) não encontrado")
			contrato = re.match(r'^(.*) Seller.*', linha[f:i])
			if not contrato:
				print("AVISO: Contrato de venda (Seller) não encontrado")
			else:
				if debug: print("\n..Contrato ("+linha[f:i]+"):",contrato.group(1))
				f = i  + len("</td>")
				fim_linha = linha.find("</tr>", f)
				if fim_linha == -1:
					print("PROBLEMAS: fim de linha de ocntrato",contrato.group(1),"não encontrado")
					print(linha[f:fim])
					admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de linha de contrato "+contrato.group(1)+" não encontrado")
				# varrer colunas com valores
				col = 0
				while f<fim_linha:
					i = linha.find("<td>", f)
					if i > -1:
						# obter valor
						f = i + len("<td>")
						i = linha.find("</td>", f)
						if i == -1:
							print("PROBLEMAS: fim de campo (</td>) não encontrado")
							print(linha[f:fim])
							admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, "PROBLEMAS: fim de campo (</td>) não encontrado")
						valor = conv.my_float(linha[f:i])	
						if debug: print("....Coluna", col, colunas[col][0], ", valor:", valor,"("+linha[f:i]+")" )
						colunas[col][n_contratos+1].append(valor)
						col = col + 1
					f = i + len("</td>")
				if debug >1: print(colunas)
			f = fim_linha + len("</tr>")
			n_contratos = n_contratos + 1
			
	if debug > 2:
		print("--- Tabela adquirida")
		print(colunas)
	
	
	for m in colunas:
		print("\nTratando metal", m[0])
		try:
			familia = familias[m[0]]
			if debug: print("..Família", familia.id, familia.nome)
			i = 1
			while i < len(m):
				trata_contrato(debug, familia, m[i], data)
				i = i + 1
		except KeyError as e:
			print("..metal", m[0], "não está nas famílias da LME, ignorando")
		
	
	
	print("FIM")
	
	if len(novos)>0:
		print("Símbolos novos detectados:", novos)
	admin.sair(debug, programa_id, nome_arq, arquivo_log, data, count_i, count_u, count_p, None)
	
