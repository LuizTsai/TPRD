#!/usr/bin/python
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



class ParametrosCalculo:
	def __init__(self, data, delta_venc, campo, moeda_norm, unidade_norm, unidade_vol_norm, cotacao_moeda, delta_cambio_real, cotacao_real, tipo_media):
		self.data = data
		self.delta_venc = int(delta_venc)
		self.campo = int(campo)
		self.moeda_norm = int(moeda_norm)
		self.unidade_norm = int(unidade_norm)
		self.unidade_vol_norm = int(unidade_vol_norm)
		self.cotacao_moeda = int(cotacao_moeda)
		self.delta_cambio_real = int(delta_cambio_real)
		self.cotacao_real = int(cotacao_real)
		self.tipo_media = int(tipo_media)
		self.taxa_cambio_reais = None
		self.data_cambio_reais = None
	def imprime(self):
		print "\tParâmetros de Cálculo"
		print "\t\tdata:", self.data
		print "\t\tdelta_venc:", self.delta_venc
		print "\t\tcampo:", self.campo,"0=VWAP, 1=Fechamento, 2=VWAP, senão Fechamento"
		print "\t\tmoeda normalização:", self.moeda_norm
		print "\t\tunidade normalização preço:", self.unidade_norm
		print "\t\tunidade normalização volume:", self.unidade_vol_norm
		print "\t\tcotação moeda:", self.cotacao_moeda, "0=compra, 1=venda, 2=média compra/venda"
		print "\t\tdelta para câmbio do real:", self.delta_cambio_real
		print "\t\tcotacao do real:", self.cotacao_real, "0=compra, 1=venda, 2=média compra/venda" 
		print "\t\ttipo de média:", self.tipo_media, "0=simples, 1=ponderada"
		print "\t\ttaxa câmbio reais:", self.taxa_cambio_reais
		print "\t\tdata câmbio reais:", self.data_cambio_reais



# Classe com os dados relevantes do cálculo de um contrato já formatados
class ContratoCalculoDisplay:
        def __init__(self, sub_bolsa, contrato, vencimento, campo_usado, valor_original, unidade_valor_original, valor_moeda_pai, unidade_valor_moeda_pai, valor_dolar, unidade_valor_dolar, valor_moeda_normalizada, unidade_valor_moeda_normalizada, valor_moeda_normalizada_unidade_contrato, unidade_valor_moeda_normalizada_unidade_contrato, valor_normalizado, unidade_valor_normalizado, qtdade_contrato, unidade_qtdade_contrato, volume_contratos, volume_mercadoria_unidade_principal, unidade_volume_mercadoria_unidade_principal, volume_mercadoria_unidade_convertida, unidade_volume_mercadoria_unidade_convertida, volume_mercadoria_normalizado, unidade_volume_normalizado):
                self.sub_bolsa = sub_bolsa      # mnemonico
                self.contrato = contrato        # nome_res da família
                self.vencimento = vencimento    # MMM/AAAA
                self.campo_usado = campo_usado
                self.valor_original = valor_original
                self.unidade_valor_original = unidade_valor_original    # símbolo ( moeda / unidade )
                self.valor_moeda_pai = valor_moeda_pai
                self.unidade_valor_moeda_pai = unidade_valor_moeda_pai  # símbolo ( moeda / unidade )
                self.valor_dolar = valor_dolar
                self.unidade_valor_dolar = unidade_valor_dolar          # símbolo ( moeda / unidade )
                self.valor_moeda_normalizada = valor_moeda_normalizada
                self.unidade_valor_moeda_normalizada = unidade_valor_moeda_normalizada  # símbolo ( moeda / unidade )
                self.valor_moeda_normalizada_unidade_contrato = valor_moeda_normalizada_unidade_contrato
                self.unidade_valor_moeda_normalizada_unidade_contrato = unidade_valor_moeda_normalizada_unidade_contrato        # símbolo ( moeda / unidade )
                self.valor_normalizado = valor_normalizado
                self.unidade_valor_normalizado = unidade_valor_normalizado      # símbolo ( moeda / unidade )
                self.qtdade_contrato = qtdade_contrato
                self.unidade_qtdade_contrato = unidade_qtdade_contrato  # símbolo
                self.volume_contratos = volume_contratos
                self.volume_mercadoria_unidade_principal = volume_mercadoria_unidade_principal
                self.unidade_volume_mercadoria_unidade_principal = unidade_volume_mercadoria_unidade_principal
                self.volume_mercadoria_unidade_convertida = volume_mercadoria_unidade_convertida
                self.unidade_volume_mercadoria_unidade_convertida = unidade_volume_mercadoria_unidade_convertida
                self.volume_mercadoria_normalizado = volume_mercadoria_normalizado
                self.unidade_volume_normalizado = unidade_volume_normalizado
		self.usar_na_media = True
        def imprime(self, nivel):
                print "--- ContratoCalculoDisplay ---"
                print "\tBolsa:", self.sub_bolsa
                print "\tContrato:", self.contrato.encode('utf-8')
                print "\tVencimento:", self.vencimento
                print "\tCampo Usado:", self.campo_usado
                print "\tPreço Original:", self.valor_original, self.unidade_valor_original
                if nivel>0:
                        print "\tPreço Moeda Pai:", self.valor_moeda_pai, self.unidade_valor_moeda_pai
                        print "\tPreço Dolar:", self.valor_dolar, self.unidade_valor_dolar
                        print "\tPreço Moeda Normalizada, Unidade Original:", self.valor_moeda_normalizada, self.unidade_valor_moeda_normalizada
                        print "\tPreço Moeda Normalizada, Unidade Convertida:", self.valor_moeda_normalizada_unidade_contrato, self.unidade_valor_moeda_normalizada_unidade_contrato
                print "\tPreço Normalizado:", self.valor_normalizado, self.unidade_valor_normalizado
                print "\tQuantidade um Contrato:", self.qtdade_contrato, self.unidade_qtdade_contrato
                print "\tVolume de Contratos:", self.volume_contratos
                print "\tVolume Mercadoria:", self.volume_mercadoria_unidade_principal, self.unidade_volume_mercadoria_unidade_principal
                if nivel>0:
                        print "\tVolume Mercadoria Unidade Convertida:", self.volume_mercadoria_unidade_convertida, self.unidade_volume_mercadoria_unidade_convertida
                print "\tVolume Mercadoria Normalizado:", self.volume_mercadoria_normalizado, self.unidade_volume_normalizado
		print "\tUsar na Média:", self.usar_na_media



# Classe com a tabela de cálculo de normalização (preço e volume) com um contrato em cada linha
class TabelaCalculo:
	def __init__(self):
		self.tabela = []
	def num_linhas(self):
		return len(self.tabela)
	def inclui(self, linha):
		if isinstance(linha, ContratoCalculoDisplay):
			self.tabela.append(linha)
	def usar_na_media(self, i, uso):
		if uso:
			self.tabela[i].usar_na_media = True
		else:	self.tabela[i].usar_na_media = False


# Classe com a tabela de médias
class TabelaMedias:
	def __init__(self, simb_unidade, simb_moeda, data_cambio_reais):
		self.media_aritmetica = 0
		self.media_ponderada = 0
		self.media_aritmetica_reais = 0
		self.media_ponderada_reais = 0
		self.unidade_media = simb_moeda+"/"+simb_unidade
		self.unidade_media_reais = "R$/"+simb_unidade
		self.data_cambio_reais = data_cambio_reais
	def imprime(self):
		print "--- Médias ---"
		print "\tMédia Aritmética Simples:\t", self.media_aritmetica, self.unidade_media,"\t\t", self.media_aritmetica_reais, self.unidade_media_reais
		print "\tMédia Ponderada por Volume:\t", self.media_ponderada, self.unidade_media, "\t\t", self.media_ponderada_reais, self.unidade_media_reais
		print "\tData do Câmbio para Reais:\t", self.data_cambio_reais
  
