#!/bin/sh

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#

log=$LOG_DIRECTORY/exporta_bvd.log

dump_tabela() {
	mysql -uroot  --batch --default-character-set=utf8 -e "$3" dados > "$1"/"$2".txt
	if [ ! -f "$1"/"$2".txt ]; then
		echo "PROBLEMAS: arquivo $1/$2.txt não gerado"
		exit 2
	fi

	cat "$1"/"$2".txt | sed "s/^/\"/" | sed "s/$/\"/" | perl -p -p -e 's/\t/\",\"/g' > "$1"/"$2".txt.2
	mv "$1"/"$2".txt.2 "$1"/"$2".csv
	rm "$1"/"$2".txt
}

data=`date  "+%Y%m%d%H%M"`
dir="bvd_$data"
cd /tmp
echo "Acessando a pasta /tmp" >> $log
echo "Acessando a pasta /tmp"

rm bvd_*
mkdir $dir
echo "Criando pasta: $dir" >> $log
echo "Criando pasta: $dir"

dump_tabela $dir "Exchange" "select idBolsa as ID_exchange, mnemonico as acronym, nome as name, URL from Bolsa;"
echo "Exchange finalizado..." >> $log
echo "Exchange finalizado..."

dump_tabela $dir "Category" "select idCategoria as ID_category, nome_en as name, pai as father_id, raiz as root, dimensoes as dimensions, densidade as density, unidade_preco_default as unit_price_id, unidade_volume as unit_volume_id from Categoria;"
echo "Category finalizado..." >> $log
echo "Category finalizado..."

dump_tabela $dir "Category_contract_set" "select id as ID_CSC, familia_contratos_id as contract_set_id, categoria_id as category_id from CategoriasFamiliaContratos;"
echo "Category_contract_set finalizado..." >> $log
echo "Category_contract_set finalizado..."

dump_tabela $dir "Contract_set" "select idFamiliaContratos as ID_contract_set, nome as name, nome_res as name_acr, subbolsa_id as subexchange_id, tipo_id as type_id, fisico as settlement_type, cod_arq, URL, unidade_cotacao as quote_unit_id, moeda_cotacao as quote_currency_id, unidade_contrato_principal as unit_contract_main_id, unidade_contrato_secundaria as unit_contract_secondary_id, qtdade_contrato_principal as quantity_contract_main, densidade as density, tick_size, tipo_vencimento as type_maturity from FamiliaContratos;"
echo "Contract_set finalizado..." >> $log
echo "Contract_set finalizado..."

dump_tabela $dir "Currency" "select idMoeda as ID_currency, simbolo as symbol, acronym, name, derivada as derivative, moeda_pai as currency_father, qtdade_um_pai as quantity_unit_father from Moeda;"
echo "Currency finalizado..." >> $log
echo "Currency finalizado..."

dump_tabela $dir "Sub_exchange" "select idSubBolsa as ID_subexchange, bolsa_id as exchange_id, mnemonico as acronym, nome as name, country from SubBolsa;"
echo "Sub_exchange finalizado..." >> $log
echo "Sub_exchange finalizado..."

dump_tabela $dir "Type_contract" "select idTipoAtivo as ID_typeContract, nome as name from TipoAtivo;"
echo "Type_contract finalizado..." >> $log
echo "Type_contract finalizado..."

dump_tabela $dir "Unit" "select idUnidade as ID_unit, tipo as type, simbolo as symbol, name, display from Unidade;"
echo "Unit finalizado..." >> $log
echo "Unit finalizado..."

dump_tabela $dir "Quotecontract" "select ativo_id as ID_contract, data as date, abertura as opening_price, fechamento as closing_price, vwap, ultimo as last_price, maximo as max_price, minimo as min_price, negocios as trades, volume_contratos as volume_contracts, volume_financeiro as volume_financial, contratos_aberto as open_interest, compra as bestbuying, venda as bestselling from CotacaoAtivo;"
echo "Quotecontract finalizado..." >> $log
echo "Quotecontract finalizado..."

dump_tabela $dir "Contract" "select idAtivo as ID_contract, subbolsa_id as sub_exchange_id, familia_contratos_id as contract_set_id, tipo_id as type_id, vencimento as maturity, data_vencimento as date_maturity, pri_neg, ult_neg, unidade_cotacao as quote_unit_id, moeda_cotacao as quote_currency_id, unidade_contrato_principal as unit_contract_main_id, unidade_contrato_secundaria as unit_contract_secondary_id, qtdade_contrato_principal as quantity_contract_main, densidade as density, tick_size, tipo_vencimento as type_maturity, delta_vencimento as delta_maturity from Ativo;"
echo "Contract finalizado..." >> $log
echo "Contract finalizado..."

echo "Mudando para a pasta: $dir"
cd $dir

echo "Compatando arquivo para o formato tgz" >> $log
echo "Compatando arquivo para o formato tgz"
tar czvf ../bvd_$data.tgz *csv

echo "Voltando para pasta /tmp e removendo a pasta criada $dir" >> $log
echo "Voltando para pasta /tmp e removendo a pasta criada $dir"
cd ..
rm -rf $dir/*
rmdir $dir

#$HOME/bin/envia_bvd.sh /tmp bvd_$data.tgz
