#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

#passwd=`cat /home/capta/mysql.root`

popula() {
mysql -vvv -t -u root  < ${1}.sql > ${1}.log 2>&1
ret=$?
if [ $ret -ne 0 ]; then
	echo "Problemas ao popular $1"
	cat ${1}.log
	return $ret
fi

}

echo "Criando database e estrutura de dados"
mysql -vvv -t -u root  < modelo_dados.sql > db_create_dados.log 2>&1
ret=$?
if [ $ret -ne 0 ]; then
	echo "Problemas na criação da base de dados"
	cat db_create_dados.log
	exit 1
fi

mysql -vvv -t -u root  < modelo_carga.sql > db_create_carga.log 2>&1
ret=$?
if [ $ret -ne 0 ]; then
	echo "Problemas na criação da base de dados"
	cat db_create_carga.log
	exit 1
fi

mysql -vvv -t -u root  < modelo_texto.sql > db_create_texto.log 2>&1
ret=$?
if [ $ret -ne 0 ]; then
	echo "Problemas na criação da base de dados"
	cat db_create_texto.log
	exit 1
fi

for i in moeda tipo_ativo categoria unidade conversao_unidade unidade_padrao bolsa sub_bolsa familia_contratos_acucar familia_contratos_algodao familia_contratos_aluminio familia_contratos_arroz familia_contratos_aveia familia_contratos_batata familia_contratos_biodiesel familia_contratos_borracha familia_contratos_butano familia_contratos_cacau familia_contratos_cafe familia_contratos_canola familia_contratos_cardamomo familia_contratos_carvao familia_contratos_cevada familia_contratos_chili familia_contratos_chumbo familia_contratos_cobalto familia_contratos_cobre familia_contratos_coentro familia_contratos_cominho familia_contratos_coque familia_contratos_curcuma familia_contratos_dende familia_contratos_diesel familia_contratos_estanho familia_contratos_etano familia_contratos_etanol familia_contratos_etileno familia_contratos_feijao familia_contratos_ferro familia_contratos_gado familia_contratos_gas_natural familia_contratos_gasoil familia_contratos_gasolina familia_contratos_girassol familia_contratos_guar familia_contratos_la familia_contratos_leite familia_contratos_lentilha familia_contratos_madeira familia_contratos_mamona familia_contratos_manteiga familia_contratos_menta familia_contratos_milheto familia_contratos_milho familia_contratos_molibdenio familia_contratos_nafta familia_contratos_niquel familia_contratos_oleo_aquecimento familia_contratos_oleo_combustivel familia_contratos_ouro familia_contratos_paladio familia_contratos_petroleo familia_contratos_pimenta familia_contratos_platina familia_contratos_polietileno familia_contratos_polipropileno familia_contratos_prata familia_contratos_propano familia_contratos_propileno familia_contratos_pvc familia_contratos_queijo familia_contratos_querosene familia_contratos_querosene_aviacao familia_contratos_soja familia_contratos_sorgo familia_contratos_suco_laranja familia_contratos_tapioca familia_contratos_trigo familia_contratos_uranio familia_contratos_whey familia_contratos_zinco programa cadernos artigos; do
	echo "Populando $i"
	popula $i
	ret=$?
	if [ $ret -ne 0 ]; then
		exit 1
	fi
done
