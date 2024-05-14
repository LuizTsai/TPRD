#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (1,'Commodities',NULL,1,NULL,NULL,NULL,NULL,'Commodities');
insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (2,'Agro',1,1,NULL,NULL,NULL,NULL,'Agriculture');
insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (3,'Açúcar',2,1,'M',NULL,5,5,'Sugar');
#insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (5,'Fibra de Algodão',133,1,'M',NULL,5,5,'Cotton');
insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (8,'Arroz',2,1,'M',NULL,5,5,'Rice');
insert into dados.Categoria (idCategoria, nome, pai, raiz, dimensoes, densidade, unidade_preco_default, unidade_volume, nome_en) values (9,'Aveia',2,1,'MV',489.13027,5,5,'Oats');
