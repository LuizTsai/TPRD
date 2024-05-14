
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

#################
# Açúcar 

# Açúcar No. 11 NYMEX
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 3, 1, "NYMEX No. 11 Sugar Futures", "No. 11 Sugar Futures", 0, "YO", 3, 2, 3, NULL, 112000, 0.0001, 0, -2, 'U', -1,  "http://www.cmegroup.com/trading/agricultural/softs/sugar-no11_contract_specifications.html");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar No. 11 ICE-US
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 5, 1, "Sugar No. 11 Futures", "Sugar No. 11 Futures", 1, "SB", 3, 3, 3, NULL, 112000, 0.01, 0, -1, 'U', -1,  "https://www.theice.com/productguide/ProductSpec.shtml?specId=23");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar No. 16 ICE-US
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 5, 1, "Sugar No. 16 Futures", "Sugar No. 16 Futures", 1, "SF", 3, 3, 3, NULL, 112000, 0.01, -1, 7, 'C', 1,  "https://www.theice.com/productguide/ProductSpec.shtml?specId=914");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar BMF 
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 9, 1, "Açúcar Cristal com Liquidação Financeira", "Açúcar Cristal Financeiro", 0, "ACF", 21, 1, 21, NULL, 508, 0.01, 0, 14, 'C', 1, "http://www.bmfbovespa.com.br/en_us/products/listed-equities-and-derivatives/commodities/cash-settled-crystal-sugar-futures.htm");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar  ICE-Eur London
# Açúcar  LIFFE-Eur London
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 11, 1, "White Sugar Futures", "White Sugar Futures", 1, "W", 5, 2, 5, NULL, 50, 0.1, 0, -16, 'C', -1,  "https://www.theice.com/products/37089080/White-Sugar-Futures");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar TOCOM 
# esta regra vale prá contratos com vencimento após nov/2013... os contratos com vencimento até set/2013 são de apenas 10 toneladas - corrigir direto na tabela Ativo após a carga dos dados
#
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 14, 1, "Raw Sugar", "Raw Sugar", 1, "211", 5, 5, 5, NULL, 50, 10, -1, -1, 'U', -1,  "http://www.tocom.or.jp/guide/youkou/raw_sugar/index.html");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar NCDEX 
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 18, 1, "Sugar S", "Sugar S", 1, "SUGARS", 19, 7, 5, NULL, 10, 1, 0, 19, 'C', -1, "http://www.ncdex.com/GlobalSearch/Search.aspx?SearchText=SUGARS&SearchTitle=SUGAR%20S");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar NCDEX 
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 18, 1, "Sugar M", "Sugar M", 1, "SUGARM200", 19, 7, 5, NULL, 10, 1, 0, 19, 'C', -1, "http://www.ncdex.com/GlobalSearch/Search.aspx?SearchText=SUGARM&SearchTitle=SUGAR%20M");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar NCDEX 
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 18, 1, "Sugar M Grade", "Sugar M Grade", 1, "SUGARM", 19, 7, 5, NULL, 10, 1, 0, 19, 'C', -1, "http://www.ncdex.com/GlobalSearch/Search.aspx?SearchText=SUGARM&SearchTitle=SUGAR%20M");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);


# Açúcar Mascavo NCDEX 
insert into dados.FamiliaContratos (subbolsa_id, tipo_id, nome, nome_res, fisico, cod_arq, 
	unidade_cotacao, moeda_cotacao, unidade_contrato_principal, unidade_contrato_secundaria, qtdade_contrato_principal, tick_size, delta_venc_m, delta_venc_d, tipo_delta, ajuste_fds, URL) 
	values ( 18, 1, "Gur", "Gur", 1, "GURCHMUZR", 27, 7, 5, NULL, 10, 0.5, 0, 19, 'C', -1, "http://www.ncdex.com/GlobalSearch/Search.aspx?SearchText=GURCHMUZR&SearchTitle=GUR");
insert into dados.CategoriasFamiliaContratos (familia_contratos_id, categoria_id) values (LAST_INSERT_ID(), 3);

