
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 1, "BRL", "Real", "Real", "Real", "Real", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 2, "USD", "Dolar", "US Dollar", "Dolar Americano", "United States Dollar", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada, Moeda_pai, qtdade_um_pai) values ( 3, "cUSD", "Cents de Dolar", "US Cents", "Centavos de Dolar Americano", "United States Cents", 1, 2, 100 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 4, "EUR", "Euro", "Euro", "Euro", "Euro", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 5, "JPY", "Yen", "Yen", "Yen", "Yen", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 6, "GBP", "Libra", "Pound", "Libra Esterlina", "Pound STerling", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 7, "INR", "Rupia", "Rupee", "Rúpia Indiana", "Indian Rupee", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 8, "ZAR", "Rand", "Rand", "Rand Sul-Africano", "South African Rand", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values ( 9, "CAD", "Dolar Canadense", "Canadian DOllar", "Dolar Canadense", "Canadian Dollar", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values (10, "THB", "Thai Baht", "Thai Baht", "Thai Baht", "Thai Baht", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada) values (11, "AUD", "Dolar Australiano", "AU Dollar", "Dolar Australiano", "Australian DOllar", 0 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada, Moeda_pai, qtdade_um_pai) values ( 12, "cAUD", "Cents de Dolar Australiano", "AU Cents", "Centavos de Dolar Australiano", "Australian Cents", 1, 11, 100 );
insert into dados.Moeda (idMoeda, simbolo, mnemonico, acronym, nome, name, derivada, Moeda_pai, qtdade_um_pai) values ( 13, "cGBP", "Pence", "Pence", "Centavos de Libra Esterlina", "Pence STerling", 1, 6, 100 );

