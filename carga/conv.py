#!/usr/bin/python
# coding=UTF8

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


import subprocess, string, re

moedas = { }
unidades = { }
unidade_padrao = {}

def my_str(s):
	if len(s) == 0:
		return None
	else : return s


def my_float(s):
	if len(s) == 0:
		return None
	else : 
		try:
			return float(s)
		except ValueError as e:
			return None


def my_long(s):
	if len(s) == 0:
		return None
	else : 
		try:
			return int(s)
		except ValueError as e:
			return None


def my_int(s):
	if len(s) == 0:
		return None
	else : 
		try:
			return int(s)
		except ValueError as e:
			return None


def calc_data_venc(debug, venc, delta_m, delta_d, tipo, ajuste):
	if debug > 2:
		print("........venc",venc,"delta_m", delta_m,"delta_d",delta_d,"tipo",tipo,"ajuste",ajuste)
	if delta_m is None:
		d_m = 0
	else:	d_m = delta_m
	if d_m == 0:
		data_ref = venc + "-01"
	elif d_m > 0:
		data_ref = subprocess.check_output(["date", "-d "+venc+"-01 + "+str(abs(d_m))+" month", "+%F"]).decode("utf-8")
	else:
		data_ref = subprocess.check_output(["date", "-d "+venc+"-01 - "+str(abs(d_m))+" month", "+%F"]).decode("utf-8")
		

	if delta_d < 0:
		sinal = " - "
	else: sinal = " + "

	if debug > 2: print(".........Data_ref",data_ref,"sinal",sinal)

	if tipo in "C": 	# delta em dias corridos 
		new_venc = subprocess.check_output(["date", "-d "+data_ref+sinal+str(abs(delta_d))+" day", "+%F"]).decode("utf-8")
		if debug > 2: print(".........Dias corridos, data vencimento",new_venc)
		# verificar se nova data cai em dia de semana
		ds = subprocess.check_output(["date", "-d "+new_venc,"+%u"]).decode("utf-8")
		if debug > 2: print("..........Dia da semana da data vencimento", ds)
		if int(ds) > 5:	# 5 é sexta-feira
			if ajuste is not None and ajuste < 0:
				if debug > 2: print(".........Vencimento em fim de semana, ajustar prá trás")
				new_venc = subprocess.check_output(["date", "-d "+new_venc+" - "+str(int(ds) - 5)+" day", "+%F"]).decode("utf-8")
			else:
				if debug > 2: print(".........Vencimento em fim de semana, ajustar prá frente")
				new_venc = subprocess.check_output(["date", "-d "+new_venc+" + "+str(8 - int(ds))+" day", "+%F"]).decode("utf-8")
	else: 	# delta em dias úteis
		new_venc = shift_data_dias_uteis(debug, data_ref, delta_d)
	return new_venc




def shift_data_dias_uteis(debug, data, delta):
	u=0; i=0;
	if delta is None: delta = 0
	if delta < 0:
		sinal = " - "
	else: sinal = " + "
	if debug>2: print("......shift de data",data,"de",delta,"dias úteis")
	while u < abs(delta):
		i = i + 1;
		ds = subprocess.check_output(["date", "-d "+data+sinal+str(i)+" day", "+%u"]).decode("utf-8")
		if debug > 2: print("........... i", i, "u", u, "ds", ds, data, sinal)
		if int(ds) <= 5: u = u + 1	# dia de semana
	new_data = subprocess.check_output(["date", "-d "+data+sinal+str(i)+" day", "+%F"]).decode("utf-8")
	if debug>2: print(".......data shiftada para",new_data)
	return new_data



# Devolve o fator pelo qual uma quantidade na unidade origem deve ser multiplicada para obter a quantidade equivalente na unidade destino
# Só funciona para pares de unidades do mesmo tipo, isto é ambas devem ser unidades de Massa, ou ambas unidades de Volume, ou ambas unidade de Energia
def fator_conversao_unidade(debug, unidade_origem, unidade_destino):
	if debug > 1:	print("Fator Conversão Unidade (",unidade_origem, unidade_destino,"):", unidades[unidade_origem].fator_para_padrao, unidades[unidade_destino].fator_para_padrao)
	if debug:	print("Fator Conversão de Unidade",unidade_origem,"para Unidade",unidade_destino,"é", unidades[unidade_origem].fator_para_padrao / unidades[unidade_destino].fator_para_padrao)
	return unidades[unidade_origem].fator_para_padrao / unidades[unidade_destino].fator_para_padrao



# Devolve o fator pelo qual uma quantidade na moeda origem deve ser multiplicada para obter a quantidade equivalente na moeda destino
# Só funciona para pares moeda derivada/moeda pai (em que a relação é fixa, como em Dolar e Centavos de Dolar
def fator_conversao_moeda(debug, moeda_origem, moeda_destino): 
	if int(moeda_origem) == int(moeda_destino):
		fator = 1
	elif moedas[moeda_origem].derivada==1:
		if moedas[moeda_origem].moeda_pai == moeda_destino:
			fator = 1 / moedas[moeda_origem].qtdade_um_pai
		else:
			print("!!!!PROBLEMAS na conversão de moedas: moeda destino (",moeda_destino,") não é moeda_pai da moeda origem (", moeda_origem,")")
			return None
	elif moedas[moeda_destino].derivada==1:
		if moedas[moeda_destino].moeda_pai == moeda_origem:
			fator = moedas[moeda_destino].qtdade_um_pai
		else:
			print("!!!!PROBLEMAS na conversão de moedas: moeda origem (",moeda_origem,") não é moeda_pai da moeda destino (", moeda_destino,")")
			return None
	else:
		print("!!!!PROBLEMAS na conversão de moedas: nem origem (",moeda_origem,") nem destino (", moeda_destino,") são moedas derivadas")
		return None
	if debug:	print("Fator de Conversão de Moeda", moeda_origem,"para Moeda",moeda_destino,"é", fator)
	return fator


def obtem_casas_decimais(debug, tick_size):
	if debug>1: print("Obtendo casas decimais de", tick_size)
	t = str(tick_size)
	p = string.find(t, '.')
	if p == -1:
		# sem ponto decimal
		t = re.match(r'\d*?(0*)$', t)
	elif p>1:
		# há dígitos antes do ponto, ignorar após o ponto
		t = re.match(r'[0-9]*?(0*)\.\d*', t)
	else:
		# apenas os dígitoa após o ponto
		t = re.match(r'[^\.]\.(\d*?)0*$', t)
	if not t: 
		print("PROBLEMAS no cálculo de casas decimais de", tick_size)
		return None
	casas = len(t.group(1))
	if p > -1 and p<=1:
		# casas após o ponto... potências negativas de 10 
		casas = - casas
	return int(casas)



def arredonda_casas(debug, valor, casas):
	vs = str(valor)
	p = string.find(vs, '.')
	if p == -1: 
		p = len(vs)
	else: vs = string.replace(vs,'.', '')

	d = int(p-casas)
	if d<len(vs):
		if int(vs[d])>=5:
			vs = str(int(vs[0:d])+1)
		else:	vs = vs[0:d]
	else: 
		if debug>1: print("arredonda_casas: número tem menos casas que o exigido, completando com zeros", d, len(vs))
		i = 0
		f = d-len(vs)
		while i<f: 
			vs = vs + "0"
			i = i + 1
	if debug>1: print("arredonda_casas: original=", valor, "sem ponto=", vs, "digitos=", d)
	if casas<0:
		# casas após o ponto
		if debug>1: print("arredonda_casas: inserindo ponto decimal com", -casas)
		vs = vs[0:len(vs)+casas]+"."+vs[len(vs)+casas:len(vs)]
	else:
		# número foi truncado antes do ponto decimal
		i = 0 
		while i<casas: 
			vs = vs + "0"
			i = i + 1

	if debug>1: print("Arredondando", valor, "com", -casas,"decimais:", vs)
	return float(vs)
