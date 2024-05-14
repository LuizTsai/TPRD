#!/usr/bin/python
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import pymysql as MySQLdb
import modelo
import conv
import datetime

conn = MySQLdb.connect(user='root',passwd='', db='dados',charset='utf8');

cur = conn.cursor()

def close():
	cur.close()
	conn.commit()


def familias_subbolsa(debug, subbolsa_id):
	if debug>1: print("\tFamílias de subbolsa", subbolsa_id)
	n = cur.execute("select idFamiliaContratos, subbolsa_id, tipo_id, nome, nome_res, cod_arq, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL, fisico, tipo_vencimento from FamiliaContratos where subbolsa_id=%s",(subbolsa_id,))
	if n<=0:
		if debug: print("!!! PROBLEMAS: nenhuma família encontrada para a subbolsa", subbolsa_id)
		return None
	i = 0
	familias = {}
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print(i, row)
		familia = modelo.FamiliaContratos(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15], row[16], row[17], row[18], row[19])
		familias[familia.cod_arq] = familia
		if debug: print("---", familia.id, familia.nome, "fisico:", familia.fisico, "tipo_vencimento:", familia.tipo_vencimento)
		row = cur.fetchone()
	return familias



def carrega_moedas(debug):
	if debug>1: print("\tCarga de Moedas")
	n = cur.execute("select idMoeda, simbolo, mnemonico, nome, derivada, Moeda_pai, qtdade_um_pai from Moeda")
	if n<=0: 
		print("!!!! PROBLEMAS: nenhuma moeda encontrada! (cursor retornou",n,")")
		return -1
	i = 0
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print(i, row)
		conv.moedas[row[0]] = modelo.Moeda(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
		if debug>1: conv.moedas[row[0]].imprime()
		row = cur.fetchone()
	return i

	

def carrega_unidades(debug):
	if debug>1: print("\tCarga de Unidades")
	n = cur.execute("select unidade_id, tipo from UnidadePadrao")
	if n<=0: 
		print("!!!! PROBLEMAS: nenhuma unidade padrão encontrada! (cursor retornou",n,")")
		return -1
	i = 0
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print(i, row)
		conv.unidade_padrao[row[1]] = int(row[0])
		row = cur.fetchone()
	if debug>1: print("Unidades Padrão:", conv.unidade_padrao)

	n = cur.execute("select idUnidade, tipo, simbolo, nome from Unidade")
	if n<=0: 
		print("!!!! PROBLEMAS: nenhuma unidade encontrada! (cursor retornou",n,")")
		return -1
	i = 0
	cur2 = conn.cursor()
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print(i, row)
		if int(row[0]) == conv.unidade_padrao[row[1]]:
			fator = 1
		else:
			n = cur2.execute("select fator_multi from ConversaoUnidade where origem=%s and destino=%s", (row[0],conv.unidade_padrao[row[1]]))
			if n < 1: 
				print("!!!!!PROBLEMAS: fator de conversão da unidade", row[0], "para a unidade", conv.unidade_padrao[row[1]], "não encontrado")
				fator = None
			else:
				row2 = cur2.fetchone()
				fator = row2[0]
		conv.unidades[row[0]] = modelo.Unidade(row[0],row[1],row[2],row[3],conv.unidade_padrao[row[1]], fator)
		row = cur.fetchone()
	if debug>1: print("Unidades:", conv.unidades)
	return i



def obtem_familia(debug, subbolsa, codigo):
	if debug: print("......procurando família, subbolsa", subbolsa, "código (", codigo,")")
	n = cur.execute("select idFamiliaContratos, subbolsa_id, tipo_id, nome, nome_res, cod_arq, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL, fisico, tipo_vencimento from FamiliaContratos where subbolsa_id=%s and cod_arq=%s",(subbolsa, codigo))
	if n<1: 
		if debug: print("......família não encontrada, subbolsa", subbolsa, "código (", codigo,")")
		return None
	row = cur.fetchone()
	familia = modelo.FamiliaContratos(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15], row[16], row[17], row[18], row[19])
	if debug>1: familia.imprime()
	return familia



def obtem_familia_id(debug, familia_id):
	if debug: print("......procurando família, id", familia_id)
	n = cur.execute("select idFamiliaContratos, subbolsa_id, tipo_id, nome, nome_res, cod_arq, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL, fisico, tipo_vencimento from FamiliaContratos where idFamiliaContratos=%s",(familia_id,))
	if n<1: 
		if debug: print("......família não encontrada, id", familia_id)
		return None
	row = cur.fetchone()
	familia = modelo.FamiliaContratos(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15], row[16], row[17], row[18], row[19])
	if debug>1: familia.imprime()
	return familia



def obtem_familia_programa(debug, programa, codigo):
	n = cur.execute("select subbolsa_id from carga.ProgramaSubBolsa where programa_id=%s", (programa,))
	if n==0:
		print("PROBLEMA!!: obtem_familia_programa: não foram encontradas famílias associadas ao programa", programa)
		# enviar email
		return None
	else:
		rows = cur.fetchall()
		for r in rows:
			if debug>1: print("\tSubbolsa", r[0], "associada ao programa",programa)
			familia = obtem_familia(debug, r[0], codigo)
			if familia: return familia
		if debug>1: print("\tSímbolo", codigo, "não é de famílias de nenhuma SubBolsa associada ao programa", programa)
		return None



def obtem_ativo(debug, familia, vencimento, tipo_vencimento=None):
	# vencimento tem a forma AAAA-MM
	if debug: print("......procurando ativo da família", familia.id,"com vencimento", vencimento)


	if familia.tipo_vencimento == "V" or (familia.tipo_vencimento == "A" and tipo_vencimento == "V"):
		n = cur.execute("select idAtivo, subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento, delta_vencimento from Ativo where familia_contratos_id =%s and vencimento=%s", (familia.id, vencimento))
	else:
		n = cur.execute("select idAtivo, subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento, delta_vencimento from Ativo where familia_contratos_id =%s and tipo_vencimento=%s and delta_vencimento=%s", (familia.id, familia.tipo_vencimento, vencimento))

	if n<1: 
		if debug: print("......ativo não encontrado, família", familia.id, "vencimento", vencimento)
		return None
	row = cur.fetchone()
	ativo = modelo.Ativo(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16])
	if debug>1: ativo.imprime()
	return ativo




def inserir_ativo(debug, familia, mes_vencimento, data_vencimento, delta_vencimento=None, tipo_vencimento=None):
	print("......inserindo ativo",familia.cod_arq,"familia", familia.id," vencimento", mes_vencimento, " data de vencimento",data_vencimento, " delta de vencimento", delta_vencimento)
	if familia.tipo_vencimento == "V" and data_vencimento == None:
		# calcular data de vencimento
		data_vencimento = conv.calc_data_venc(debug, mes_vencimento, familia.delta_venc_m, familia.delta_venc_d, familia.tipo_delta, familia.ajuste_fds)
		print("......data de vencimento calculada em", data_vencimento )
	t_v = familia.tipo_vencimento
	if t_v == "A":	# família tem contratos com data de vencimento e contratos com delta de vencimento (metais da LME)
		t_v = tipo_vencimento # chamador controla o tipo de contrato, se é com data ou delta de vencimento

	# inserir o Ativo
	if t_v == "V":
		if familia.unidade_contrato_secundaria:
			n = cur.execute("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, mes_vencimento, data_vencimento, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal, familia.unidade_contrato_secundaria, familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v))
			print("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, mes_vencimento, data_vencimento, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal, familia.unidade_contrato_secundaria, familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v))
		else:
                        n = cur.execute("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, mes_vencimento, data_vencimento, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal,  familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v))
                        print("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento) values (%s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, mes_vencimento, data_vencimento, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal, familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v))

	else:
		n = cur.execute("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento, delta_vencimento) values (%s, %s, %s, NULL, NULL, NULL, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal, familia.unidade_contrato_secundaria, familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v, str(delta_vencimento)))
		print("insert into Ativo (subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento, delta_vencimento) values (%s, %s, %s, NULL, NULL, NULL, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (familia.subbolsa_id, familia.id, familia.tipo_id, familia.unidade_cotacao, familia.moeda_cotacao, familia.unidade_contrato_principal, familia.unidade_contrato_secundaria, familia.qtdade_contrato_principal, familia.densidade, familia.tick_size, t_v, str(delta_vencimento)))
	if debug>1: print("............insert retornou n=",n)
	if n==1:
		n = cur.execute("SELECT LAST_INSERT_ID()")
		if debug>1: print("............last_insert_id retornou n=",n)
		if n==1:
			ativo_id = cur.fetchone()
			print("........inseriu ativo com id", ativo_id[0])
			# instanciar e popular objeto como o Ativo inserido para retorno
			if t_v == "V":
				ativo = obtem_ativo(debug, familia, mes_vencimento, t_v)
			else:
				ativo = obtem_ativo(debug, familia, delta_vencimento, t_v)

			conn.commit()
			return ativo
		else:
			print("......PROBLEMAS ao recuperar ID do Ativo inserido, familia",familia.id,"vencimento",mes_vencimento)
			return None
	else:
		print("......PROBLEMAS ao inserir Ativo, familia",familia.id,"vencimento",mes_vencimento)
		return None



def update_ativo(debug, ativo):
	if debug: 
		print("......atualizando Ativo", ativo.id)
	# atualizar a cotação
	if ativo.tipo_vencimento == "V":
		n = cur.execute("update Ativo set familia_contratos_id=%s, tipo_id=%s, vencimento=%s, data_vencimento=%s, pri_neg=%s, ult_neg=%s, unidade_cotacao=%s, moeda_cotacao=%s, unidade_contrato_principal=%s, unidade_contrato_secundaria=%s, qtdade_contrato_principal=%s, densidade=%s, tick_size=%s, tipo_vencimento=%s, delta_vencimento=%s where idAtivo=%s", (ativo.familia_contratos_id, ativo.tipo_id, ativo.vencimento, ativo.data_vencimento, ativo.pri_neg, ativo.ult_neg, ativo.unidade_cotacao, ativo.moeda_cotacao, ativo.unidade_contrato_principal, ativo.unidade_contrato_secundaria, ativo.qtdade_contrato_principal, ativo.densidade, ativo.tick_size, ativo.tipo_vencimento, ativo.delta_vencimento, ativo.id))
	else:
		n = cur.execute("update Ativo set familia_contratos_id=%s, tipo_id=%s, vencimento=%s, data_vencimento=NULL, pri_neg=%s, ult_neg=%s, unidade_cotacao=%s, moeda_cotacao=%s, unidade_contrato_principal=%s, unidade_contrato_secundaria=%s, qtdade_contrato_principal=%s, densidade=%s, tick_size=%s, tipo_vencimento=%s, delta_vencimento=%s where idAtivo=%s", (ativo.familia_contratos_id, ativo.tipo_id, ativo.vencimento, ativo.pri_neg, ativo.ult_neg, ativo.unidade_cotacao, ativo.moeda_cotacao, ativo.unidade_contrato_principal, ativo.unidade_contrato_secundaria, ativo.qtdade_contrato_principal, ativo.densidade, ativo.tick_size, ativo.tipo_vencimento, ativo.delta_vencimento, ativo.id))
	if debug>1: print("............update retornou n=",n)
	if n==1:
		# instanciar e popular objeto como o Ativo inserido para retorno
		familia = obtem_familia_id(debug, ativo.familia_contratos_id) 
		if ativo.tipo_vencimento == "V":
			ativo_novo = obtem_ativo(debug, familia, ativo.vencimento, ativo.tipo_vencimento)
		else:
			ativo_novo = obtem_ativo(debug, familia, ativo.delta_vencimento, ativo.tipo_vencimento)
		return ativo_novo
	else:
		print("......PROBLEMAS ao atualiza Ativo",ativo.id)
		return None








def obtem_cotacao_ativo(debug, ativo, data):
	if debug: print("......procurando cotação do ativo", ativo.id,"para a data", data)
	n = cur.execute("select ativo_id, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto, compra, venda from CotacaoAtivo where ativo_id =%s and data=%s", (ativo.id, data))
	if n<1: 
		if debug: print("......cotação não encontrada, ativo", ativo.id, "data", data)
		return None
	row = cur.fetchone()
	if row[9] and ativo.qtdade_contrato_principal: 
		volume_merc_principal = ativo.qtdade_contrato_principal*int(row[9])
	else:	volume_merc_principal = None
	cotacao = modelo.CotacaoAtivo(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11], volume_merc_principal, row[12],row[13])
	if debug>1: cotacao.imprime()
	return cotacao




def inserir_cotacao_ativo(debug, ativo, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto, compra=None, venda=None):
	if debug: print("......inserindo cotação do ativo",ativo.id,"na data", data,"com abertura", abertura,"maximo",maximo,"minimo",minimo,"ultimo",ultimo,"fechamento",fechamento,"vwap",vwap,"negocios",negocios,"volume_contratos",volume_contratos,"volume_financeiro",volume_financeiro,"contratos_aberto",contratos_aberto, "compra", compra, "venda", venda)
	# inserir a cotação
	n = cur.execute("insert into CotacaoAtivo (ativo_id, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto, compra, venda) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ativo.id, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto, compra, venda))
	if debug>1: print("............insert retornou n=",n)
	if n==1:
		# instanciar e popular objeto como o Ativo inserido para retorno
		cotacao = obtem_cotacao_ativo(debug, ativo, data)
		if ativo.ult_neg == None or data > ativo.ult_neg:
			# atualizar data do último negócio
			print("......Cotação posterior ao último negócio (",ativo.ult_neg,"), atualizando Ativo")
			ativo.ult_neg = data
			ativo = update_ativo(debug, ativo)
		if ativo.pri_neg == None or data < ativo.pri_neg:
			# atualizar data do primeiro negócio
			print("......Cotação anterior ao primeiro negócio (",ativo.pri_neg,"), atualizando Ativo")
			ativo.pri_neg = data
			ativo = update_ativo(debug, ativo)
		return cotacao
	else:
		print("......PROBLEMAS ao inserir cotação do ativo",ativo.id,"na data", data,"com fechamento",fechamento)
		return None




def update_cotacao_ativo(debug, ativo, cotacao):
	if debug: 
		print("......atualizando cotação do ativo")
		print((cotacao.abertura, cotacao.ultimo, cotacao.fechamento, cotacao.vwap, cotacao.maximo, cotacao.minimo, cotacao.negocios, cotacao.volume_contratos, cotacao.volume_financeiro, cotacao.contratos_aberto, cotacao.ativo_id, cotacao.data, cotacao.compra, cotacao.venda))
	# atualizar a cotação
	n = cur.execute("update CotacaoAtivo set abertura=%s, ultimo=%s, fechamento=%s, vwap=%s, maximo=%s, minimo=%s, negocios=%s, volume_contratos=%s, volume_financeiro=%s, contratos_aberto=%s, compra=%s, venda=%s where ativo_id=%s and data=%s", (cotacao.abertura, cotacao.ultimo, cotacao.fechamento, cotacao.vwap, cotacao.maximo, cotacao.minimo, cotacao.negocios, cotacao.volume_contratos, cotacao.volume_financeiro, cotacao.contratos_aberto, cotacao.compra, cotacao.venda, cotacao.ativo_id, cotacao.data))
	if debug>1: print("............update retornou n=",n)
	if n==1 or n==0:
		# instanciar e popular objeto como o Ativo inserido para retorno
		cotacao_nova = obtem_cotacao_ativo(debug, ativo, cotacao.data)
		return cotacao_nova
	else:
		print("......PROBLEMAS ao atualiza cotação do ativo",cotacao.ativo_id,"na data", cotacao.data,"com fechamento",cotacao.fechamento)
		return None




def carrega_simbolos_moedas(debug, moedas):
	n = cur.execute("select idMoeda, simbolo from Moeda")
	if debug: print("Há",n,"moedas")
	i=0
	while i<n:
		row = cur.fetchone()
		if debug>1: print(i,row)
		moedas[row[1]] = row[0]
		i = i + 1
	return i



def obtem_cotacao_moeda(debug, moeda_id, data):
	n = cur.execute("select moeda_id, data, compra, venda, par_compra, par_venda from CotacaoMoeda where moeda_id=%s and data=%s",(moeda_id, data))
	if n<1: 
		if debug: print("......cotação não encontrada, moeda", moeda_id, "data", data)
		return None
	row = cur.fetchone()
	cotacao = modelo.CotacaoMoeda(row[0],row[1],row[2],row[3],row[4],row[5])
	if debug>1: cotacao.imprime()
	return cotacao



def inserir_cotacao_moeda(debug, moeda_id, data, compra, venda, par_compra, par_venda):
	if debug: print("......inserindo cotação da moeda",moeda_id,"na data", data,"com compra", compra,"venda",venda,"par_compra",par_compra,"par_venda",par_venda)
	# inserir a cotação
	n = cur.execute("insert into CotacaoMoeda (moeda_id, data, compra, venda, par_compra, par_venda) values (%s, %s, %s, %s, %s, %s)", (moeda_id, data, compra, venda, par_compra, par_venda))
	if debug>1: print("............insert retornou n=",n)
	if n==1:
		# instanciar e popular objeto como o Ativo inserido para retorno
		cotacao = obtem_cotacao_moeda(debug, moeda_id, data)
		return cotacao
	else:
		print("......PROBLEMAS ao inserir cotação da moeda",moeda_id,"na data", data,"com venda",venda)
		return None




def update_cotacao_moeda(debug, cotacao):
	if debug: 
		print("......atualizando cotação da moeda", cotacao.moeda_id, "na data", cotacao.data)
		print((cotacao.compra, cotacao.venda, cotacao.par_compra, cotacao.par_venda))
	# atualizar a cotação
	n = cur.execute("update CotacaoMoeda set compra=%s, venda=%s, par_compra=%s, par_venda=%s where moeda_id=%s and data=%s", (cotacao.compra, cotacao.venda, cotacao.par_compra, cotacao.par_venda, cotacao.moeda_id, cotacao.data))
	if debug>1: print("............update retornou n=",n)
	if n==1:
		# instanciar e popular objeto como o Ativo inserido para retorno
		cotacao_nova = obtem_cotacao_moeda(debug, cotacao.moeda_id, cotacao.data)
		return cotacao_nova
	else:
		print("......PROBLEMAS ao atualiza cotação da moeda",cotacao.moeda_id,"na data", cotacao.data,"com venda",cotacao.venda)
		return None


def obtem_id_programa(debug, prog):
	if debug>2: print("\tObtendo id do programa", prog)
	# obter id do programa
	n = cur.execute("select idPrograma from carga.Programa where nome=%s", (prog,))
	if n==1:
		row = cur.fetchone()
		if debug>2: print("\t\tPrograma tem id", row[0])
		return row[0]
	else:
		print("PROBLEMAS: inserir_execucao: programa",prog,"não encontrado")
		# enviar email
		return None


#
# "Anota" que o programa 'prog' carrega dados da família
#
def inserir_programa_familia(debug, prog, familia):
	if debug>2: print("\tAnotando que a família",familia.id, familia.nome_res.encode('utf-8'),"é carregada pelo programa",prog)
	n = cur.execute("select * from carga.ProgramaFamiliaContratos where programa_id=%s and familiacontratos_id=%s", (prog, familia.id))
	if n==0:
		# não há ligação do programa com a família na base, anotar!
		n = cur.execute("insert into carga.ProgramaFamiliaContratos (programa_id, familiacontratos_id) values (%s, %s)", (prog, familia.id))
		if n==1:
			if debug: print("\tCriada ligação entre o programa", prog,"e a família", familia.id, familia.nome_res.encode('utf-8'))
			return 0
		else:
			print("PROBLEMAS: inserir_programa_familia: não cosneguiu inserir a ligação do programa", prog,"com a família", familia.id, familia.nome_res.encode('utf-8'))
			return 2
	else:	return 0



def inserir_execucao(debug, programa, arq_carregado, data, arq_log, inseridas, alteradas, iguais, erro):
	if debug>2: print("\n\nInserindo execução de",programa,"pro arquivo", arq_carregado, "de", data,"com log em", arq_log,"inseridas",inseridas,"alteradas",alteradas,"iguais", iguais,"erro",erro)

	if erro:	
		b_erro = 1
	else:	b_erro = 0
	n = cur.execute("insert into carga.Execucao (data, programa_id, arq_carregado, data_carregada, arq_log, cot_inseridas, cot_alteradas, cot_iguais, erro, msg_erro) values (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)", (datetime.datetime.today(), programa, arq_carregado, data, arq_log, inseridas, alteradas, iguais, b_erro, erro))
	if n==1: return 0
	else:
		print("PROBLEMAS: inserir_execucao: não cosneguiu inserir a execução na base")
		return 2
