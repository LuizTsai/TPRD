#!/usr/bin/python
# -*- coding: utf8 -*-

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


class FamiliaContratos:
	def __init__(self, id,  subbolsa_id, tipo_id, nome, nome_res, cod_arq, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL, fisico, tipo_vencimento):
		self.id = int(id)
		self.subbolsa_id = int(subbolsa_id)
		self.tipo_id = int(tipo_id)
		self.nome = nome
		self.nome_res = nome_res
		self.fisico = int(fisico)
		self.cod_arq = cod_arq
		self.unidade_cotacao = int(unidade_cotacao)
		self.moeda_cotacao = int(moeda_cotacao)
		if unidade_contrato_principal: self.unidade_contrato_principal = int(unidade_contrato_principal)
		else: self.unidade_contrato_principal = None
		if unidade_contrato_secundaria: self.unidade_contrato_secundaria = int(unidade_contrato_secundaria)
		else: self.unidade_contrato_secundaria = None
		if qtdade_contrato_principal: self.qtdade_contrato_principal = float(qtdade_contrato_principal)
		else: self.qtdade_contrato_principal = None
		if densidade: self.densidade = float(densidade)
		else: self.densidade = 0 #None
		if tick_size: self.tick_size = float(tick_size)
		else: self.tick_size = None
		if delta_venc_m:
			self.delta_venc_m = int(delta_venc_m)
		else:	self.delta_venc_m = None
		if delta_venc_d:
			self.delta_venc_d = int(delta_venc_d)
		else:	self.delta_venc_d = None
		self.tipo_delta = tipo_delta
		if ajuste_fds:
			self.ajuste_fds = int(ajuste_fds)
		else:	self.ajuste_fds = None
		self.URL = URL
		self.tipo_vencimento = tipo_vencimento
	def __unicode__(self):
		return str(self.id)+","+self.nome
	def imprime(self):
		print("\tFamília de Contratos")
		print("\t\tID:", self.id)
		print("\t\tSub Bolsa:", self.subbolsa_id)
		print("\t\tTipo:", self.tipo_id)
		print("\t\tNome:", self.nome.encode('utf-8'))
		print("\t\tNome Resumido:", self.nome_res.encode('utf-8'))
		print("\t\tFísico:", self.fisico)
		print("\t\tTipo Vencimento:", self.tipo_vencimento)
		print("\t\tCódigo nos Arquivos:", self.cod_arq)
		print("\t\tUnidade Cotação:", self.unidade_cotacao)
		print("\t\tMoeda Cotação:", self.moeda_cotacao)
		print("\t\tUnidade do Contrato (principal):", self.unidade_contrato_principal)
		print("\t\tUnidade do Contrato (secundária):", self.unidade_contrato_secundaria)
		print("\t\tQuantidade do Contrato (unidade principal):", self.qtdade_contrato_principal)
		print("\t\tDensidade:", self.densidade, "kg / m3")
		print("\t\tTick Size:", self.tick_size)
		print("\t\tDelta do Vencimento (em meses):", self.delta_venc_m)
		print("\t\tDelta do Vencimento (em dias):", self.delta_venc_d)
		print("\t\tTipo de Delta (C=dias corridos, U=dias úteis):", self.tipo_delta)
		print("\t\tAjuste de Dia Não-Útil (1=dia posterior, -1=dia anterior):", self.ajuste_fds)
		print("\t\tDescrição do Contrato", self.URL)

class Ativo:
	def __init__(self, id,  subbolsa_id, familia_contratos_id, tipo_id, vencimento, data_vencimento, pri_neg, ult_neg, unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, densidade, tick_size, tipo_vencimento, delta_vencimento=None):
		self.id = int(id)
		self.subbolsa_id = int(subbolsa_id)
		self.familia_contratos_id = int(familia_contratos_id)
		self.tipo_id = int(tipo_id)
		self.vencimento = str(vencimento)
		self.data_vencimento = str(data_vencimento)
		if pri_neg: self.pri_neg = str(pri_neg)
		else: self.pri_neg = None
		if ult_neg: self.ult_neg = str(ult_neg)
		else: self.ult_neg = None
		self.unidade_cotacao = int(unidade_cotacao)
		self.moeda_cotacao = int(moeda_cotacao)
		if unidade_contrato_principal: self.unidade_contrato_principal = int(unidade_contrato_principal)
		else: self.unidade_contrato_principal = None
		if unidade_contrato_secundaria: self.unidade_contrato_secundaria = int(unidade_contrato_secundaria)
		else: self.unidade_contrato_secundaria = None
		if qtdade_contrato_principal: self.qtdade_contrato_principal = float(qtdade_contrato_principal)
		else: self.qtdade_contrato_principal = None
		if densidade: self.densidade = float(densidade)
		else: self.densidade = None
		if tick_size: self.tick_size = float(tick_size)
		else: self.tick_size = None
		self.tipo_vencimento = tipo_vencimento
		if self.tipo_vencimento == "D": self.delta_vencimento = int(delta_vencimento)
		else: self.delta_vencimento = None
	def imprime(self):
		print("\tAtivo:")
		print("\t\tID", self.id)
		print("\t\tSub Bolsa", self.subbolsa_id)
		print("\t\tFamília de Contratos", self.familia_contratos_id)
		print("\t\tTipo", self.tipo_id)
		print("\t\tTipo Vencimento:", self.tipo_vencimento)
		print("\t\tVencimento", self.vencimento)
		print("\t\tData de Vencimento", self.data_vencimento)
		print("\t\tDelta Vencimento:", self.delta_vencimento)
		print("\t\tData Primeiro Negócio", self.pri_neg)
		print("\t\tData Último Negócio", self.ult_neg)
		print("\t\tUnidade Cotação", self.unidade_cotacao)
		print("\t\tMoeda Cotação", self.moeda_cotacao)
		print("\t\tUnidade do Contrato (principal)", self.unidade_contrato_principal)
		print("\t\tUnidade do Contrato (secundaria)", self.unidade_contrato_secundaria)
		print("\t\tQuantidade do Contrato (unidade principal)", self.qtdade_contrato_principal)
		print("\t\tDensidade", self.densidade)
		print("\t\tTick Size", self.tick_size)




class CotacaoAtivo:
	def __init__(self, ativo_id, data, abertura, ultimo, fechamento, vwap, maximo, minimo, negocios, volume_contratos, volume_financeiro, contratos_aberto, volume_mercadoria_principal=None, compra=None, venda=None):
		self.ativo_id = int(ativo_id)
		self.data = str(data) 
		if abertura is not None: self.abertura = float(abertura) 
		else: self.abertura = None
		if ultimo is not None: self.ultimo = float(ultimo) 
		else: self.ultimo = None
		if fechamento is not None: self.fechamento = float(fechamento)
		else: self.fechamento = None
		if vwap is not None: self.vwap = float(vwap)
		else: self.vwap = None
		if maximo is not None: self.maximo = float(maximo) 
		else: self.maximo = None
		if minimo is not None: self.minimo = float(minimo) 
		else: self.minimo = None
		if negocios is not None: self.negocios = int(negocios)
		else: self.negocios = None
		if volume_contratos is not None: self.volume_contratos = int(volume_contratos) 
		else: self.volume_contratos = None
		if volume_financeiro is not None: self.volume_financeiro = float(volume_financeiro) 
		else: self.volume_financeiro = None
		if contratos_aberto is not None: self.contratos_aberto = int(contratos_aberto)
		else: self.contratos_aberto = None
		if volume_mercadoria_principal is not None: self.volume_mercadoria_principal = float(volume_mercadoria_principal) 
		else: self.volume_mercadoria_principal = None
		if compra is not None: self.compra = float(compra)
		else: self.compra = None
		if venda is not None: self.venda = float(venda)
		else: self.venda = None
	def imprime(self):
		print("\tCotação de Ativo:")
		print("\t\tAtivo ID", self.ativo_id)
		print("\t\tData", self.data)
		print("\t\tAbertura", self.abertura)
		print("\t\tÚltimo", self.ultimo)
		print("\t\tFechamento", self.fechamento)
		print("\t\tVwap", self.vwap)
		print("\t\tMáximo", self.maximo)
		print("\t\tMínimo", self.minimo)
		print("\t\tCompra", self.compra)
		print("\t\tVenda", self.venda)
		print("\t\tNegócios", self.negocios)
		print("\t\tVolume Contratos", self.volume_contratos)
		print("\t\tVolume Financeiro", self.volume_financeiro)
		print("\t\tContratos em Aberto", self.contratos_aberto)
		print("\t\tVolume Mercadoria (unidade principal)", self.volume_mercadoria_principal)



class CotacaoMoeda:
	def __init__(self, moeda_id, data, compra, venda, par_compra, par_venda): 
		self.moeda_id = int(moeda_id)
		self.data = str(data) 
		self.compra = float(compra) 
		self.venda = float(venda) 
		self.par_compra = float(par_compra) 
		self.par_venda = float(par_venda) 
	def imprime(self):
		print("\tCotação de Moeda:")
		print("\t\tMoeda ID", self.moeda_id)
		print("\t\tData", self.data)
		print("\t\tCompra", self.compra)
		print("\t\tVenda", self.venda)
		print("\t\tParidade de Compra", self.par_compra)
		print("\t\tParidade de Venda", self.par_venda)



class Unidade:
	def __init__(self, id, tipo, simbolo, nome, padrao, fator_para_padrao):
		self.id = int(id)
		self.tipo = tipo
		self.simbolo = simbolo
		self.nome = nome
		self.padrao = padrao
		self.fator_para_padrao = float(fator_para_padrao)
	def imprime(self):
		print("\t\tID", self.id)
		print("\t\tTipo", self.tipo)
		print("\t\tSimbolo", self.simbolo)
		print("\t\tNome:", self.nome.encode('utf-8'))
		print("\t\tUnidade Padrão", self.padrao)
		print("\t\tFator para Padrão", self.fator_para_padrao)


class Moeda:
	def __init__(self, id, simbolo, mnemonico, nome, derivada, moeda_pai, qtdade_um_pai):
		self.id = int(id)
		self.simbolo = simbolo 
		self.mnemonico = mnemonico
		self.nome = nome
		self.derivada = int(derivada)
		if self.derivada==1: self.moeda_pai = int(moeda_pai)
		else: self.moeda_pai = None
		if self.derivada==1: self.qtdade_um_pai = float(qtdade_um_pai)
		else: self.qtdade_um_pai = None
	def imprime(self):
		print("\t\tID:", self.id)
		print("\t\tSímbolo:", self.simbolo)
		print("\t\tMnemônico:", self.mnemonico)
		print("\t\tNome:", self.nome.encode('utf-8'))
		print("\t\tDerivada:", self.derivada)
		print("\t\tMoeda Pai:", self.moeda_pai)
		print("\t\tQuantidade um Pai:", self.qtdade_um_pai)


class SubBolsa:
	def __init__(self, bolsa, sub_bolsa, mnemonico, nome):
		self.bolsa = int(bolsa)
		self.sub_bolsa = int(sub_bolsa)
		self.mnemonico = mnemonico
		self.nome = nome
	def imprime(self):
		print("\t\tBolsa:", self.bolsa)
		print("\t\tSub-Bolsa:", self.sub_bolsa)
		print("\t\tMnemônico:", self.mnemonico)
		print("\t\tNome:", self.nome.encode('utf-8'))
