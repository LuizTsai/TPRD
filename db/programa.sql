
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

insert into carga.Programa (idPrograma, nome, descricao) values (  1, "bacen", "Câmbio do BACEN");

insert into carga.Programa (idPrograma, nome, descricao) values (  2, "cme_agro", "Agro do grupo CME");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 2, 1);	# CBOT
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 2, 2);	# CME
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 2, 26);	# MGEX

insert into carga.Programa (idPrograma, nome, descricao) values (  3, "ice_us", "ICE US");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 3, 5);	# ICE-US

insert into carga.Programa (idPrograma, nome, descricao) values (  4, "liffe_eur_london", "LIFFE Europe London");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 4, 11);	# LIFFE Europe, Londres
insert into carga.Programa (idPrograma, nome, descricao) values (  12, "liffe_eur_paris", "LIFFE Europe Paris");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 12, 12);	# LIFFE Europe, Paris

insert into carga.Programa (idPrograma, nome, descricao) values (  5, "bmf", "Bovespa/BMF");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 5, 9);	# ICE-US

insert into carga.Programa (idPrograma, nome, descricao) values (  6, "tocom", "TOCOM");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 6, 14);	# TOCOM

insert into carga.Programa (idPrograma, nome, descricao) values (  7, "mcx", "MCX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 7, 17);	# MCX

insert into carga.Programa (idPrograma, nome, descricao) values (  8, "ncdex", "NCDEX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 8, 18);	# NCDEX

insert into carga.Programa (idPrograma, nome, descricao) values (  9, "safex", "SAFEX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values ( 9, 21);	# SAFEX

insert into carga.Programa (idPrograma, nome, descricao) values ( 10, "nymex", "NYMEX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (10, 3);	# NYMEX

insert into carga.Programa (idPrograma, nome, descricao) values ( 11, "ice_canada", "ICE-Canada");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (11, 7);	# ICE-Canada

insert into carga.Programa (idPrograma, nome, descricao) values ( 13, "afet", "AFET");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (13, 19);	# AFET

insert into carga.Programa (idPrograma, nome, descricao) values ( 14, "ice_europe_s2f", "ICE Europe S2F");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (14, 27);	# ICE Europe S2F

insert into carga.Programa (idPrograma, nome, descricao) values ( 15, "asx", "ASX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (15, 20);	# ASX

insert into carga.Programa (idPrograma, nome, descricao) values ( 16, "ice_europe", "ICE Europe");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (16, 6);	# ICE-EUR
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (16, 11);	# ICE-EUR London

insert into carga.Programa (idPrograma, nome, descricao) values ( 17, "euronext", "Euronext");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (17, 12);	# Euronext, Paris

insert into carga.Programa (idPrograma, nome, descricao) values ( 18, "lme", "LME");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (18, 13);	# LME

insert into carga.Programa (idPrograma, nome, descricao) values ( 19, "comex", "COMEX");
insert into carga.ProgramaSubBolsa(programa_id, subbolsa_id) values (19, 4);	# COMEX





















