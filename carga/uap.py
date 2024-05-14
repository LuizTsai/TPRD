#!/usr/bin/python
# -*- coding: utf8 -*-
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import sys
import MySQLdb
import modelo
import muap
import conv
import commands
import re

conn = MySQLdb.connect(user='uap',passwd='p0k@', db='dados',charset='utf8');

cur = conn.cursor()

mes_venc = {
		"01":	"JAN",
		"02":	"FEV",
		"03":	"MAR",
		"04":	"ABR",
		"05":	"MAI",
		"06":	"JUN",
		"07":	"JUL",
		"08":	"AGO",
		"09":	"SET",
		"10":	"OUT",
		"11":	"NOV",
		"12":	"DEZ"
	}

# Classe com os dados de um contrato (uma linha da planilha) ao longo dos cálculos de normalização
# Na instanciação são conhecidos apenas os objetos originais (sub_bolsa, família, ativo e cotação)
# Os demais atributos são preenchidos pelas rotinas de cálculo envolvidas na normalização
class ContratoCalculo:
        def __init__(self, sub_bolsa, familia, ativo, cotacao):
                self.sub_bolsa = sub_bolsa
                self.familia = familia
                self.ativo = ativo
                self.cotacao = cotacao
                self.valor_original = None
                self.campo_usado = None
                self.simbolo_moeda_original = None
                self.valor_moeda_pai = None
                self.simbolo_moeda_pai = None
                self.moeda_pai = None
                self.valor_dolar_un_ori = None
                self.valor_moeda_norm_un_ori = None
                self.simbolo_moeda_norm = None
                self.moeda_norm = None
                self.simbolo_unidade_original = None
                self.valor_moeda_norm_un_contr = None
                self.unidade_contrato_usada = None
                self.simbolo_unidade_contrato = None
                self.valor_normalizado = None
                self.simbolo_unidade_norm = None
                self.unidade_norm = None
                self.volume_contratos = None
                self.volume_merc_un_pri = None
                self.simbolo_un_pri = None
                self.volume_merc_un_vol_usada = None
                self.simbolo_un_vol_usada = None
                self.unidade_vol_usada = None
                self.volume_merc_normalizado= None
                self.simbolo_un_vol_norm = None
                self.unidade_vol_norm = None
	def imprime(self, nivel):
                print "--- ContratoCalculo ---"
                if nivel>0:
                        if self.sub_bolsa: self.sub_bolsa.imprime()
                        if self.familia: self.familia.imprime()
                        if self.ativo: self.ativo.imprime()
                        if self.cotacao: self.cotacao.imprime()

                print "\tValor Original:", self.valor_original
                print "\tCampo Usado:", self.campo_usado
                print "\tMoeda Original:", self.simbolo_moeda_original
                print "\tValor Moeda Pai:", self.valor_moeda_pai
                print "\tMoeda pai:", self.moeda_pai, self.simbolo_moeda_pai
                print "\tValor USD Unidade Original:", self.valor_dolar_un_ori
                print "\tValor",self.simbolo_moeda_norm,"Unidade Original:", self.valor_moeda_norm_un_ori
                print "\tUnidade Original:", self.ativo.unidade_cotacao, self.simbolo_unidade_original
                print "\tValor",self.simbolo_moeda_norm,"Unidade Contrato:", self.valor_moeda_norm_un_contr
                print "\tUnidade Contrato Usada:", self.unidade_contrato_usada, self.simbolo_unidade_contrato
                print "\tUnidade Normalização:", self.unidade_norm, self.simbolo_unidade_norm
                print "\tValor Normalizado:", self.valor_normalizado, self.simbolo_moeda_norm,"/",self.simbolo_unidade_norm
                print "\tVolume Contratos:", self.volume_contratos
                print "\tVolume Mercadoria Unidade Principal:", self.volume_merc_un_pri, self.simbolo_un_pri
                print "\tUnidade Principal:", self.ativo.unidade_contrato_principal, self.simbolo_un_pri
                print "\tVolume Mercadoria Unidade Vol Contrato:", self.volume_merc_un_vol_usada, self.simbolo_un_vol_usada
                print "\tUnidade Vol Contrato:", self.unidade_vol_usada, self.simbolo_un_vol_usada
                print "\tVolume Mercadoria Normalizado:", self.volume_merc_normalizado, self.simbolo_un_vol_norm
                print "\tUnidade Vol Normalização:", self.unidade_vol_norm, self.simbolo_un_vol_norm
	def converte_display(self):
		return muap.ContratoCalculoDisplay(self.sub_bolsa.mnemonico, self.familia.nome_res, mes_venc[self.ativo.vencimento[5:7]]+"/"+self.ativo.vencimento[0:4], self.campo_usado, self.valor_original, self.simbolo_moeda_original+"/"+self.simbolo_unidade_original, self.valor_moeda_pai, self.simbolo_moeda_pai+"/"+self.simbolo_unidade_original, self.valor_dolar_un_ori, "USD/"+self.simbolo_unidade_original, self.valor_moeda_norm_un_ori, self.simbolo_moeda_norm+"/"+self.simbolo_unidade_original, self.valor_moeda_norm_un_contr, self.simbolo_moeda_norm+"/"+self.simbolo_unidade_contrato, self.valor_normalizado, self.simbolo_moeda_norm+"/"+self.simbolo_unidade_norm, self.ativo.qtdade_contrato_principal, self.simbolo_un_pri, self.volume_contratos, self.volume_merc_un_pri, self.simbolo_un_pri, self.volume_merc_un_vol_usada, self.simbolo_un_vol_usada, self.volume_merc_normalizado, self.simbolo_un_vol_norm)




def close():
	cur.close()
	conn.commit()

#######################################################################################
#
# Rotinas de acesso ao Banco de Dados
#

# obtem categoria
def obtem_categoria(debug, id):
	if debug: print "Obtendo categorias",id 
	n = cur.execute("select idCategoria, pai, nome, raiz, dimensoes, unidade_preco_default, unidade_volume from Categoria where idCategoria=%s", (id,))
	if debug: print "...há",n,"categorias"
	if n<1:
		return None
	else: return cur.fetchall()		


# obtem categorias filhas
def obtem_categorias_filhas(debug, raiz):
	if debug: print "Obtendo categorias filhas de",raiz 
	n = cur.execute("select idCategoria, pai, nome, raiz, dimensoes, unidade_preco_default, unidade_volume from Categoria where pai=%s", (raiz,))
	if debug: print "...há",n,"categorias"
	if n<1:
		return None
	else: return cur.fetchall()		


# Obtem os dados de uma SubBolsa dado o id da mesma
def obtem_sub_bolsa(debug, sub_bolsa_id):
	if debug: print "......procurando sub_bolsa (", sub_bolsa_id,")"
	n = cur.execute("select bolsa_id, idSubBolsa, mnemonico, nome from SubBolsa where idBolsa=%s and idSubBolsa=%s", (sub_bolsa_id,))
	if n<1: 
		if debug: print "......sub_bolsa não encontrada"
		return None
	row = cur.fetchone()
	sub_bolsa = modelo.SubBolsa(row[0],row[1],row[2],row[3])
	if debug>1: sub_bolsa.imprime()
	return sub_bolsa


# Obtem os dados de uma Família de Contratos dado o id da mesma
def obtem_familia(debug, familia_id):
	n = cur.execute("select idFamiliaContratos, subbolsa_id, tipo_id, nome, nome_res, cod_elet, cod_clearing, cod_vvoz, cod_arq, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, fator_principal_secundaria, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL from FamiliaContratos where idFamiliaContratos=%s",(familia_id,))
	if n<1: 
		if debug: print "......família não encontrada, subbolsa", subbolsa, "código", codigo
		return None
	row = cur.fetchone()
	familia = modelo.FamiliaContratos(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15], row[16], row[17], row[18], row[19], row[20])
	if debug>1: familia.imprime()
	return familia



# Devolve os dados do primeiro Ativo (contrato) de uma Família com vencimenmto não anterior ao informado 
def obtem_ativo(debug, familia_contratos_id, vencimento):
	# vencimento tem a forma AAAA-MM
	if debug: print "......procurando ativo da família", familia_contratos_id,"com vencimento igual ou posterior", vencimento
	n = cur.execute("select idAtivo, subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, fator_principal_secundaria, tick_size from Ativo where familia_contratos_id =%s and vencimento>=%s order by vencimento asc", (familia_contratos_id, vencimento))
	if n<1: 
		if debug: print "......ativo não encontrado, família", familia_contratos_id, "vencimento", vencimento
		return None
	row = cur.fetchone()
	ativo = modelo.Ativo(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14])
	if debug>1: ativo.imprime()
	return ativo



# Obtem a cotação de um Ativo numa data
def obtem_cotacao_ativo(debug, ativo, data):
	if debug: print "......procurando cotação do ativo", ativo.id,"para a data", data
	n = cur.execute("select ativo_id, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto from CotacaoAtivo where ativo_id =%s and data=%s", (ativo.id, data))
	if n<1: 
		if debug: print "......cotação não encontrada, ativo", ativo.id, "data", data
		return None
	row = cur.fetchone()
	if row[9] and ativo.qtdade_contrato_principal: 
		volume_merc_principal = ativo.qtdade_contrato_principal*int(row[9])
	else:	volume_merc_principal = None
	cotacao = modelo.CotacaoAtivo(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11], volume_merc_principal)
	if debug>1: cotacao.imprime()
	return cotacao


# Obtem a cotação de uma Moeda numa data
def obtem_cotacao_moeda(debug, moeda_id, data):
	n = cur.execute("select moeda_id, data, compra, venda, par_compra, par_venda from CotacaoMoeda where moeda_id=%s and data=%s",(moeda_id, data))
	if n<1: 
		if debug: print "......cotação não encontrada, moeda", moeda_id, "data", data
		return None
	row = cur.fetchone()
	cotacao = modelo.CotacaoMoeda(row[0],row[1],row[2],row[3],row[4],row[5])
	if debug>1: cotacao.imprime()
	return cotacao



# Obtem a cotação de uma Moeda numa data com delta de dias úteis
def obtem_cotacao_moeda_delta(debug, moeda_id, data, delta):
	if debug > 1: print "...Obtendo cotação da moeda",moeda_id,"para",data,"com delta de",delta,"dias úteis"
	new_data = conv.shift_data_dias_uteis(debug, data, delta)
	n = cur.execute("select moeda_id, data, compra, venda, par_compra, par_venda from CotacaoMoeda where moeda_id=%s and data<=%s order by data desc",(moeda_id, new_data))
	if n<1: 
		if debug: print "......cotação não encontrada, moeda", moeda_id, "data", data
		return None
	row = cur.fetchone()
	cotacao = modelo.CotacaoMoeda(row[0],row[1],row[2],row[3],row[4],row[5])
	if debug>1: cotacao.imprime()
	return cotacao



# Carrega as moedas na lista de moedas do módulo conv
def carrega_moedas(debug):
	if debug>1: print "\tCarga de Moedas"
	n = cur.execute("select idMoeda, simbolo, mnemonico, nome, derivada, Moeda_pai, qtdade_um_pai from Moeda")
	if n<=0: 
		print "!!!! PROBLEMAS: nenhuma moeda encontrada! (cursor retornou",n,")"
		return -1
	i = 0
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print i, row
		conv.moedas[row[0]] = modelo.Moeda(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
		if debug>1: conv.moedas[row[0]].imprime()
		row = cur.fetchone()
	return i


# Carrega as unidades na lista de unidades do módulo conv
def carrega_unidades(debug):
	if debug>1: print "\tCarga de Unidades"
	n = cur.execute("select unidade_id, tipo from UnidadePadrao")
	if n<=0: 
		print "!!!! PROBLEMAS: nenhuma unidade padrão encontrada! (cursor retornou",n,")"
		return -1
	i = 0
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print i, row
		conv.unidade_padrao[row[1]] = int(row[0])
		row = cur.fetchone()
	if debug>1: print "Unidades Padrão:", conv.unidade_padrao

	n = cur.execute("select idUnidade, tipo, simbolo, nome from Unidade")
	if n<=0: 
		print "!!!! PROBLEMAS: nenhuma unidade encontrada! (cursor retornou",n,")"
		return -1
	i = 0
	cur2 = conn.cursor()
	row = cur.fetchone()
	while row:
		i = i + 1
		if debug>2: print i, row
		if int(row[0]) == conv.unidade_padrao[row[1]]:
			fator = 1
		else:
			n = cur2.execute("select fator_multi from ConversaoUnidade where origem=%s and destino=%s", (row[0],conv.unidade_padrao[row[1]]))
			if n < 1: 
				print "!!!!!PROBLEMAS: fator de conversão da unidade", row[0], "para a unidade", conv.unidade_padrao[row[1]], "não encontrado"
				fator = None
			else:
				row2 = cur2.fetchone()
				fator = row2[0]
		conv.unidades[row[0]] = modelo.Unidade(row[0],row[1],row[2],row[3],conv.unidade_padrao[row[1]], fator)
		row = cur.fetchone()
	if debug>1: print "Unidades:", conv.unidades
	return i



#
# Obtem uma lista das Famílias associadas a uma Categoria
#
def obtem_familias_categoria(debug, categoria_id):
	n = cur.execute("select familia_contratos_id from CategoriasFamiliaContratos where categoria_id=%s",(categoria_id,))
	if n<1: 
		if debug: print "..Famílias não encontradas, categoria", categoria_id
		return None
	if debug>1: print "..Retornando",n,"Famílias"
	l = cur.fetchall()
	linhas = []
	# transformar de lista de tuplas prá lista de inteiros
	for i in l:
		linhas.append(int(i[0]))
	return linhas



#######################################################################################
#
# Rotinas de Cálculo de Normalização
#

#
# Inicializa os campos de câmbio para reais em parâmetros
#
def obtem_taxa_cambio_reais(debug, parametros):
	cotacao = obtem_cotacao_moeda_delta(debug, parametros.moeda_norm, parametros.data, parametros.delta_cambio_real)
	parametros.data_cambio_reais = cotacao.data
	if parametros.cotacao_real==0:
		parametros.taxa_cambio_real = cotacao.compra
	elif parametros.cotacao_real==1:
		parametros.taxa_cambio_reais = cotacao.venda
	else: parametros.taxa_cambio_reais = (cotacao.compra + cotacao.venda ) / 2
	if debug: print "---- Câmbio para Reais:   Taxa:", parametros.taxa_cambio_reais, "Data:", parametros.data_cambio_reais
	if debug>1: parametros.imprime()



# 
# seleciona_campo: seleciona o campo de valor a ser usado nos cálculos de acordo com a escolha do usuário
#
# escolha_usuario:
#		0: VWAP
#		1: Fechamento
# 		2: VWAP se houver, senão fechamento
def seleciona_campo(debug, contrato_calculo, escolha_usuario):
	if escolha_usuario==0:
		if debug: print "...Escolha de campo para", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento,": escolha_usuario=VWAP"
		contrato_calculo.campo_usado = "VWAP"
		contrato_calculo.valor_original = contrato_calculo.cotacao.vwap
	elif escolha_usuario==1:
		if debug: print "...Escolha de campo para", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento,": escolha_usuario=Fechamento"
		contrato_calculo.campo_usado = "Fech"
		contrato_calculo.valor_original = contrato_calculo.cotacao.fechamento
	elif contrato_calculo.cotacao.vwap and contrato_calculo.cotacao.vwap>0:
		if debug: print "...Escolha de campo para", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento,": escolha_usuario=(VWAP, senão Fechamento), usando VWAP"
		contrato_calculo.campo_usado = "VWAP"
		contrato_calculo.valor_original = contrato_calculo.cotacao.vwap
	else:
		if debug: print "...Escolha de campo para", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento,": escolha_usuario=(VWAP, senão Fechamento), usando Fechamento"
		contrato_calculo.campo_usado = "Fech"
		contrato_calculo.valor_original = contrato_calculo.cotacao.fechamento
	# transformar None em 0 prá facilitar rotinas de cálculos
	if not contrato_calculo.valor_original: contrato_calculo.valor_original = 0 
	contrato_calculo.simbolo_unidade_original = conv.unidades[contrato_calculo.ativo.unidade_cotacao].simbolo
		
			

#
# trata_moeda_derivada: transforma o valor escolhido da moeda derivada prá moeda pai
#
def trata_moeda_derivada(debug, contrato_calculo):
	if conv.moedas[contrato_calculo.ativo.moeda_cotacao].derivada:
		moeda_pai =  conv.moedas[contrato_calculo.ativo.moeda_cotacao].moeda_pai
		fator =  conv.moedas[contrato_calculo.ativo.moeda_cotacao].qtdade_um_pai
		if debug: print "...Contrato", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento," usa moeda derivada", conv.moedas[contrato_calculo.ativo.moeda_cotacao].simbolo, ", convertendo para moeda pai", conv.moedas[moeda_pai].simbolo
		contrato_calculo.valor_moeda_pai = contrato_calculo.valor_original / fator
		contrato_calculo.simbolo_moeda_pai = conv.moedas[moeda_pai].simbolo
		contrato_calculo.moeda_pai = moeda_pai
		contrato_calculo.simbolo_moeda_original = conv.moedas[contrato_calculo.ativo.moeda_cotacao].simbolo
		if debug: print "....", contrato_calculo.valor_original, contrato_calculo.simbolo_moeda_original, "/", contrato_calculo.simbolo_unidade_original, "->", contrato_calculo.valor_moeda_pai, contrato_calculo.simbolo_moeda_pai, "/", contrato_calculo.simbolo_unidade_original
	else:
		if debug>1: print "....Contrato", contrato_calculo.familia.nome_res, contrato_calculo.ativo.vencimento, "não usa moeda derivada"
		contrato_calculo.valor_moeda_pai = contrato_calculo.valor_original
		contrato_calculo.simbolo_moeda_pai = contrato_calculo.simbolo_moeda_original = conv.moedas[contrato_calculo.ativo.moeda_cotacao].simbolo
		contrato_calculo.moeda_pai = contrato_calculo.ativo.moeda_cotacao


#
# converte_em_dolar: converte o valor escolhido da moeda pai para dolar usando a cotação escolhida
#
# escolha_usuario:
#			0: compra
#			1: venda
#			2: média Compra/venda (PTAX)	
def converte_em_dolar(debug, contrato_calculo, escolha_usuario):
	if contrato_calculo.simbolo_moeda_pai == "USD":
		# já está em dolar!
		contrato_calculo.valor_dolar_un_ori = contrato_calculo.valor_moeda_pai
		if debug: print "...Valor já está em USD, nada a fazer"
	else:
		cotacao_moeda = obtem_cotacao_moeda(debug, contrato_calculo.moeda_pai, contrato_calculo.cotacao.data)
		if escolha_usuario==0:
			fator = cotacao_moeda.par_compra
			if debug: print "....Convertendo de",contrato_calculo.simbolo_moeda_pai,"para Dolar pela cotação de compra:", fator
		elif escolha_usuario==1:
			fator = cotacao_moeda.par_venda
			if debug: print "....Convertendo de",contrato_calculo.simbolo_moeda_pai,"para Dolar pela cotação de venda:", fator
		else:
			fator = (cotacao_moeda.par_compra + cotacao_moeda.par_venda)/2
			if debug: print "....Convertendo de",contrato_calculo.simbolo_moeda_pai,"para Dolar pela médias das cotações de compra e venda:", fator 
		contrato_calculo.valor_dolar_un_ori = contrato_calculo.valor_moeda_pai * fator
		if debug: print "....", contrato_calculo.valor_moeda_pai, contrato_calculo.simbolo_moeda_pai, "/", contrato_calculo.simbolo_unidade_original, "->", contrato_calculo.valor_dolar_un_ori, "USD /", contrato_calculo.simbolo_unidade_original 



#
# converte_dolar_para_moeda: converte o valor escolhido de dolar para a moeda de normalização usando a cotação escolhida
#
# escolha_usuario:
#			0: compra
#			1: venda
#			2: média Compra/venda (PTAX)	
def converte_dolar_para_moeda(debug, contrato_calculo, moeda_norm, escolha_usuario):
	contrato_calculo.moeda_norm = moeda_norm
	contrato_calculo.simbolo_moeda_norm = conv.moedas[moeda_norm].simbolo
	if conv.moedas[moeda_norm].simbolo == "USD":
		# já está em dolar!
		contrato_calculo.valor_moeda_norm_un_ori = contrato_calculo.valor_dolar_un_ori
		if debug: print "...Valor já está na moeda de normalização (", contrato_calculo.simbolo_moeda_norm,"), nada a fazer"
	else:
		cotacao_moeda = obtem_cotacao_moeda(debug, contrato_calculo.moeda_norm, contrato_calculo.cotacao.data)
		if escolha_usuario==0:
			fator = cotacao_moeda.par_compra
			if debug: print "....Convertendo para",contrato_calculo.simbolo_moeda_norm,"pela cotação de compra:", fator
		elif escolha_usuario==1:
			fator = cotacao_moeda.par_venda
			if debug: print "....Convertendo para",contrato_calculo.simbolo_moeda_norm,"pela cotação de venda:", fator
		else:
			fator = (cotacao_moeda.par_compra + cotacao_moeda.par_venda)/2
			if debug: print "....Convertendo para",contrato_calculo.simbolo_moeda_norm,"pela médias das cotações de compra e venda:", fator 
		contrato_calculo.valor_moeda_norm_un_ori = contrato_calculo.valor_dolar_un_ori / fator
		if debug: print "....", contrato_calculo.valor_dolar_un_ori, "USD /", contrato_calculo.simbolo_unidade_original, "->", contrato_calculo.valor_moeda_norm_un_ori, contrato_calculo.simbolo_moeda_norm, "/", contrato_calculo.simbolo_unidade_original


	

#
# normaliza_dimensao_unidade: se necessário, converte entre unidade principal e secundária do contrato para usar a dimensão da unidade de normalização
#
# Há contratos que podem ser expressos tanto em unidade de Massa quanto em unidades de Volume; esta função converte entre elas
#
def normaliza_dimensao_unidade(debug, contrato_calculo, unidade_norm):
	if conv.unidades[contrato_calculo.ativo.unidade_cotacao].tipo == conv.unidades[unidade_norm].tipo:
		contrato_calculo.unidade_contrato_usada = contrato_calculo.ativo.unidade_cotacao
		contrato_calculo.simbolo_unidade_contrato = conv.unidades[contrato_calculo.ativo.unidade_cotacao].simbolo
		contrato_calculo.valor_moeda_norm_un_contr = contrato_calculo.valor_moeda_norm_un_ori
		if debug: print "....Unidade do Contrato (",contrato_calculo.simbolo_unidade_contrato,") tem mesma dimensão que unidade de normalização (",conv.unidades[unidade_norm].simbolo,")"
	elif conv.unidades[contrato_calculo.ativo.unidade_contrato_secundaria].tipo == conv.unidades[unidade_norm].tipo:
		contrato_calculo.unidade_contrato_usada = contrato_calculo.ativo.unidade_contrato_secundaria
		contrato_calculo.simbolo_unidade_contrato = conv.unidades[contrato_calculo.ativo.unidade_contrato_secundaria].simbolo
		if debug: print "....Unidade de Cotação",conv.unidades[contrato_calculo.ativo.unidade_cotacao].simbolo,"não tem mesma dimensão que a Unidade de Normalização",conv.unidades[unidade_norm].simbolo
		# unidade_cotação -> unidade_principal
		fator = conv.fator_conversao_unidade(debug, contrato_calculo.ativo.unidade_cotacao, contrato_calculo.ativo.unidade_contrato_principal)
		# unidade_principal -> unidade_secundária
		if debug: print "....Fator Principal -> Secundária:", contrato_calculo.ativo.fator_principal_secundaria
		fator = fator * contrato_calculo.ativo.fator_principal_secundaria
		if debug: print "....Fator final de normalização de dimensão de unidade:", fator
		contrato_calculo.valor_moeda_norm_un_contr = contrato_calculo.valor_moeda_norm_un_ori / fator
		if debug: print "....", contrato_calculo.valor_moeda_norm_un_ori,contrato_calculo.simbolo_moeda_norm, "/", contrato_calculo.simbolo_unidade_original," ->", contrato_calculo.valor_moeda_norm_un_contr, contrato_calculo.simbolo_moeda_norm, "/", contrato_calculo.simbolo_unidade_contrato
		
	else:
		print "PROBLEMAS!!! unidades de cotação", contrato_calculo.ativo.unidade_cotacao,"e secundária do contrato",contrato_calculo.ativo.unidade_contrato_secundaria,"não tem dimensão da unidade de normalização",unidade_norm
		sys.exit(100)



#
# Converte o valor da unidade usada no contrato para a unidade de normalização
# As unidades envolvidas já devem ter a mesma dimensão!
#
def converte_valor_para_unidade(debug, contrato_calculo, unidade_norm):
	contrato_calculo.simbolo_unidade_norm = conv.unidades[unidade_norm].simbolo
	contrato_calculo.unidade_norm = unidade_norm
	if contrato_calculo.unidade_contrato_usada == unidade_norm:
		contrato_calculo.valor_normalizado = contrato_calculo.valor_moeda_norm_un_contr
		if debug: print "....Unidade do Contrato (",contrato_calculo.simbolo_unidade_contrato,") é a Unidade de Normalização"
	else:
		fator = conv.fator_conversao_unidade(1, contrato_calculo.unidade_contrato_usada, unidade_norm)
		contrato_calculo.valor_normalizado = contrato_calculo.valor_moeda_norm_un_contr / fator
		if debug: print "....", contrato_calculo.valor_moeda_norm_un_contr, contrato_calculo.simbolo_moeda_norm, "/", contrato_calculo.simbolo_unidade_contrato, "->", contrato_calculo.valor_normalizado, contrato_calculo.simbolo_moeda_norm, "/", contrato_calculo.simbolo_unidade_norm



#
# normaliza_dimensao_volume: se necessário, converte entre unidade principal e secundária do contrato para usar a dimensão da unidade de normalização
#
# Há contratos que podem ser expressos tanto em unidade de Massa quanto em unidades de Volume; esta função converte entre elas
#
def normaliza_dimensao_volume(debug, contrato_calculo, unidade_norm):
	if contrato_calculo.cotacao.volume_contratos :	contrato_calculo.volume_contratos = contrato_calculo.cotacao.volume_contratos
	else:  contrato_calculo.volume_contratos = 0
	contrato_calculo.volume_merc_un_pri = contrato_calculo.volume_contratos * contrato_calculo.ativo.qtdade_contrato_principal
	contrato_calculo.simbolo_un_pri = conv.unidades[contrato_calculo.ativo.unidade_contrato_principal].simbolo

	if conv.unidades[contrato_calculo.ativo.unidade_contrato_principal].tipo == conv.unidades[unidade_norm].tipo:
		contrato_calculo.unidade_vol_usada = contrato_calculo.ativo.unidade_contrato_principal
		contrato_calculo.simbolo_un_vol_usada = conv.unidades[contrato_calculo.ativo.unidade_contrato_principal].simbolo
		contrato_calculo.volume_merc_un_vol_usada = contrato_calculo.volume_merc_un_pri
		if debug: print "....Unidade do Contrato (",contrato_calculo.simbolo_unidade_contrato,") tem mesma dimensão que unidade de normalização (",conv.unidades[unidade_norm].simbolo,")"
	elif conv.unidades[contrato_calculo.ativo.unidade_contrato_secundaria].tipo == conv.unidades[unidade_norm].tipo:
		contrato_calculo.unidade_vol_usada = contrato_calculo.ativo.unidade_contrato_secundaria
		contrato_calculo.simbolo_un_vol_usada = conv.unidades[contrato_calculo.ativo.unidade_contrato_secundaria].simbolo
		if debug: print "....Unidade do Contrato",conv.unidades[contrato_calculo.ativo.unidade_contrato_principal].simbolo,"não tem mesma dimensão que a Unidade de Normalização",conv.unidades[unidade_norm].simbolo
		# unidade_principal -> unidade_secundária
		if debug: print "....Fator Principal -> Secundária:", contrato_calculo.ativo.fator_principal_secundaria
		fator = contrato_calculo.ativo.fator_principal_secundaria
		contrato_calculo.volume_merc_un_vol_usada  = contrato_calculo.volume_merc_un_pri * fator
		if debug: print "....", contrato_calculo.volume_merc_un_pri, contrato_calculo.simbolo_un_pri, "->", contrato_calculo.volume_merc_un_vol_usada, contrato_calculo.simbolo_un_vol_usada		
	else:
		print "PROBLEMAS!!! unidades principal", contrato_calculo.ativo.unidade_contrato_principal,"e secundária do contrato",contrato_calculo.ativo.unidade_contrato_secundaria,"não tem dimensão da unidade de normalização",unidade_norm
		sys.exit(100)



#
# Converte volume de mercadoria da unidade usada no contrato para a unidade de normalização
# As unidades envolvidas já devem ter a mesma dimensão!
#
def converte_volume_para_unidade(debug, contrato_calculo, unidade_norm):
	contrato_calculo.simbolo_un_vol_norm = conv.unidades[unidade_norm].simbolo
	contrato_calculo.unidade_vol_norm = unidade_norm
	if contrato_calculo.unidade_vol_usada == unidade_norm:
		contrato_calculo.volume_merc_normalizado = contrato_calculo.volume_merc_un_vol_usada
		if debug: print "....Unidade de Volume Usada (",contrato_calculo.simbolo_un_vol_usada,") é a Unidade de Normalização"
	else:
		fator = conv.fator_conversao_unidade(1, contrato_calculo.unidade_vol_usada, unidade_norm)
		contrato_calculo.volume_merc_normalizado = contrato_calculo.volume_merc_un_vol_usada * fator
		if debug: print "....", contrato_calculo.volume_merc_un_vol_usada, contrato_calculo.simbolo_un_vol_usada, "->", contrato_calculo.volume_merc_normalizado, contrato_calculo.simbolo_un_vol_norm




#
# Rotina de cáculo de normalização para uma Família
#
def calcula_familia(debug, familia_id, parametros):
	familia = obtem_familia(debug, familia_id)
	if not familia:
		print "PROBLEMAS!!! família", familia_id,"não encontrada"
		sys.exit(100)
	sub_bolsa = obtem_sub_bolsa(debug, familia.subbolsa_id)
	if not sub_bolsa:
		print "PROBLEMAS!!! sub_bolsa", familia.subbolsa_id, "não encontrada"
		sys.exit(100)
	if debug: print ".Tratando Família", familia_id, familia.nome_res

	if parametros.delta_venc==None or parametros.delta_venc < 0:
		print "PROBLEMAS!!! delta de vencimento negativo", parametros.delta_venc,"(deve ser zero ou positivo!)"
		sys.exit(100)

	if debug: print "\n----------- Tratando Família", familia_id, familia.nome_res,"---------------"

	vencimento = commands.getoutput("date -d \""+parametros.data+" + "+str(parametros.delta_venc)+" months\" +%Y-%m")
	if debug: print ".Procurando Ativo com vencimento a partir de", vencimento, "na Família", familia.id, familia.nome_res

	ativo = obtem_ativo(debug, familia_id, vencimento)
	if not ativo:
		# Nenhum Contrato na base com vencimento igual ou posterior ao solicitado
		if debug: print "...não foram encontrados ativos com vencimento a partir de", vencimento, "na Família", familia_id, familia.nome_res, ", pulando família"
		return None
	if debug: "..Ativo", ativo.id, "com vencimento", ativo.vencimento, "selecionado, procurando cotação para", parametros.data

	cotacao = obtem_cotacao_ativo(debug, ativo, parametros.data)
	if not cotacao:
		# Nenhuma cotação para o Ativo na data solicitada
		if debug: print ".Não foi encontrada cotação parao Ativo", ativo.id, "na data", data, "ignorando família"
		return None
	if debug: print "..Cotação com VWAP", cotacao.vwap, ", fechamento", cotacao.fechamento, "e volume", cotacao.volume_contratos, "encontrada"

	# instanciar estrutura de cáculo (linha da planilha)
	linha_calc = ContratoCalculo(sub_bolsa, familia, ativo, cotacao)
	if debug>1: linha_calc.imprime(1)

	# selecionar campo de preço
	seleciona_campo(debug, linha_calc, parametros.campo)

	# Normalizar Moeda
	if debug: print "..Normalizando Valor: Moeda ", parametros.moeda_norm, conv.moedas[parametros.moeda_norm].simbolo
	trata_moeda_derivada(debug, linha_calc)
	converte_em_dolar(debug, linha_calc, parametros.cotacao_moeda)
	converte_dolar_para_moeda(debug, linha_calc, parametros.moeda_norm, parametros.cotacao_moeda)

	# Normalizar Unidade no preço
	if debug: print "..Normalizando Valor: Unidade", parametros.unidade_norm, conv.unidades[parametros.unidade_norm].simbolo
	normaliza_dimensao_unidade(debug, linha_calc, parametros.unidade_norm)
	converte_valor_para_unidade(debug, linha_calc, parametros.unidade_norm)

	# Normalizar Volume
	if debug: print "..Normalizando Volume: Unidade", parametros.unidade_vol_norm, conv.unidades[parametros.unidade_vol_norm].simbolo
	normaliza_dimensao_volume(debug, linha_calc, parametros.unidade_vol_norm)
	converte_volume_para_unidade(debug, linha_calc, parametros.unidade_vol_norm)

	if debug: linha_calc.imprime(0)

	return linha_calc


#
# Rotina de cálculo de normalização para uma lista de Famílias
# Devolve um objeto do tipo TabelaCalculo, que é uma lista de objetos ContratoCalculoDisplay
# Portanto cada linha contém uma "struct" com todos os valores intermediários na normalização de preço e volume
#
def calcula_tabela_normalizacao(debug, familias, parametros): 
	if debug: print "Tratando",len(familias),"Famílias"
	n = i = 0
	planilha = muap.TabelaCalculo()
	if debug: print "Planilha criada com", planilha.num_linhas(),"linhas"
	
	# obter dados de câmbio para reais e guardar em parametros
	obtem_taxa_cambio_reais(debug, parametros)
	if debug: parametros.imprime()

	for familia_id in familias:
		i = i + 1
		if debug: print "\n",i,"Família",familia_id,"======================"
		linha = calcula_familia(debug, familia_id, parametros)
		if linha:
			n = n + 1
			linha_display = linha.converte_display()
			if linha_display:
				if debug>1: linha_display.imprime(1)
				planilha.inclui(linha_display)
				if debug: print "Contrato",linha_display.sub_bolsa, linha_display.contrato.encode('utf-8'), linha_display.vencimento, "incluído, planilha com", planilha.num_linhas(),"linhas"
			else:
				print "PROBLEMAS!!! ao converter linha de cálculo em linha de display"
				linha.imprime()
				sys.exit(100)
		elif debug: print "Família", familia_id, "sem contrato que satisfaça os parâmetros de busca, ignorada..."
	if debug: print "Número de Contratos:", n
	return planilha			


#
# Calcula Médias
#
def calcula_tabela_medias(debug, tab_norm, parametros):
	if not isinstance(tab_norm, muap.TabelaCalculo):
		print "PROBLEMAS!!!! tab_norm passada para calcula_tabela_medias não é uma TabelaCalculo!"
		sys.exit(100)
	if debug: "..Calculando médias..."
	tab_medias = muap.TabelaMedias(conv.unidades[parametros.unidade_norm].simbolo, conv.moedas[parametros.moeda_norm].simbolo, parametros.data_cambio_reais)
	nt = tab_norm.num_linhas()
	sum_valor = 0
	sum_valor_ponderado = 0
	sum_volume = 0
	n = i = 0
	for linha in tab_norm.tabela:
		if linha.usar_na_media:
			i = i + 1
			if linha.valor_normalizado > 0:
				n = n + 1
				sum_valor = sum_valor + linha.valor_normalizado
				sum_valor_ponderado = sum_valor_ponderado + linha.valor_normalizado * linha.volume_mercadoria_normalizado
				sum_volume = sum_volume + linha.volume_mercadoria_normalizado
			if debug > 1: print "...",i, n, "valor:", linha.valor_normalizado, "volume:", linha.volume_mercadoria_normalizado, "sum_valor:", sum_valor, "sum_ponderado:", sum_valor_ponderado, "sum_volume:", sum_volume
	tab_medias.media_aritmetica = sum_valor / n
	tab_medias.media_ponderada = sum_valor_ponderado / sum_volume

	tab_medias.media_aritmetica_reais = tab_medias.media_aritmetica * parametros.taxa_cambio_reais
	tab_medias.media_ponderada_reais = tab_medias.media_ponderada * parametros.taxa_cambio_reais
	if debug: 
		print ".. média aritmética:", tab_medias.media_aritmetica, tab_medias.unidade_media, "\t\t", tab_medias.media_aritmetica_reais, tab_medias.unidade_media_reais
		print ".. média ponderada:", tab_medias.media_ponderada, tab_medias.unidade_media, "\t\t", tab_medias.media_ponderada_reais, tab_medias.unidade_media_reais

	return tab_medias



def gera_csv(debug, tab_norm, tab_medias, parametros, verbosity):
	saida = "Data de Negociação;" + parametros.data[8:10] + "/" + parametros.data[5:7] + "/" + parametros.data[0:4] + "\n\n"
	saida = saida + "Bolsa;Contrato;Vencimento;Campo Usado;Preço Original;Unidade;"
	if verbosity > 0:
		saida = saida + "Preço Moeda Pai;Unidade;Preço Dolar;Unidade;Preço Moeda Normalizada;Unidade;Preço Unidade Contrato;Unidade;"
	saida = saida + "Preço Normalizado;Unidade;Quantidade do Contrato;Unidade;Volume de Contratos;Volume Mercadoria;Unidade;"
	if verbosity > 0:
		saida = saida + "Volume Mercadoria;Unidade;"
	saida = saida + "Volume Normalizado;Unidade\n"

	for linha in tab_norm.tabela:
		saida = saida + linha.sub_bolsa.encode('utf-8') + ";" + linha.contrato.encode('utf-8') + ";" + linha.vencimento.encode('utf-8') + ";" + linha.campo_usado.encode('utf-8') + ";" + str(linha.valor_original) + ";" + linha.unidade_valor_original.encode('utf-8') + ";"
		if verbosity > 0:
			saida = saida + str(linha.valor_moeda_pai) + ";" + linha.unidade_valor_moeda_pai.encode('utf-8') + ";" + str(linha.valor_dolar) + ";" + linha.unidade_valor_dolar.encode('utf-8') + ";" + str(linha.valor_moeda_normalizada) + ";" + linha.unidade_valor_moeda_normalizada.encode('utf-8') + ";" + str(linha.valor_moeda_normalizada_unidade_contrato) + ";" + linha.unidade_valor_moeda_normalizada_unidade_contrato.encode('utf-8') + ";"
		saida = saida + str(linha.valor_normalizado) + ";" + linha.unidade_valor_normalizado.encode('utf-8') + ";" + str(linha.qtdade_contrato) + ";" + linha.unidade_qtdade_contrato.encode('utf-8') + ";" + str(linha.volume_contratos) + ";" + str(linha.volume_mercadoria_unidade_principal) + ";" + linha.unidade_volume_mercadoria_unidade_principal.encode('utf-8') + ";"
		if verbosity > 0:
			saida = saida + str(linha.volume_mercadoria_unidade_convertida) + ";" + linha.unidade_volume_mercadoria_unidade_convertida.encode('utf-8') + ";"
		saida = saida + str(linha.volume_mercadoria_normalizado) + ";" + linha.unidade_volume_normalizado.encode('utf-8') + "\n"

	saida = saida + "\n\n"
	saida = saida + ";Média Aritmética Simples;" + str(tab_medias.media_aritmetica) + ";" + tab_medias.unidade_media.encode('utf-8') + ";" + str(tab_medias.media_aritmetica_reais) + ";" + tab_medias.unidade_media_reais.encode('utf-8') + "\n"
	saida = saida + ";Média Ponderada por Volume;" + str(tab_medias.media_ponderada) + ";" + tab_medias.unidade_media.encode('utf-8') + ";" + str(tab_medias.media_ponderada_reais) + ";" + tab_medias.unidade_media_reais.encode('utf-8') + "\n"

	saida = saida + "\n\n"
	saida = saida + ";Normalização de moeda estrangeira usando "
	if parametros.cotacao_moeda == 0:
		saida = saida + "cotação de compra\n"
	elif parametros.cotacao_moeda == 1:
		saida = saida + "cotação de venda\n"
	else: saida = saida + "média das cotações de compra e venda\n"

	saida = saida + ";Conversão em reais usando "
	if parametros.cotacao_real == 0:
		saida = saida + "cotação de compra"
	elif parametros.cotacao_real == 1:
		saida = saida + "cotação de venda"
	else: saida = saida + "média das cotações de compra e venda"
	saida = saida + " de " + parametros.data_cambio_reais[8:10] + "/" + parametros.data_cambio_reais[5:7] + "/" + parametros.data_cambio_reais[0:4] + "\n"
	return re.sub(r'\.', ",", saida)
	
