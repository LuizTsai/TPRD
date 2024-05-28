#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#
export data=`date "+%Y%m%d"`


mysqldump -uroot -p`cat $HOME/mysql.root` --single-transaction --tz-utc --complete-insert --no-autocommit  tprd | gzip > $HOME/backup/db/tprd/tprd_$data.sql.gz
mysqldump -uroot -p`cat $HOME/mysql.root` --single-transaction --tz-utc --complete-insert --no-autocommit  dados | gzip > $HOME/backup/db/tprd/dados_$data.sql.gz
mysqldump -uroot -p`cat $HOME/mysql.root` --single-transaction --tz-utc --complete-insert --no-autocommit  texto | gzip > $HOME/backup/db/tprd/texto_$data.sql.gz
mysqldump -uroot -p`cat $HOME/mysql.root` --single-transaction --tz-utc --complete-insert --no-autocommit  carga | gzip > $HOME/backup/db/tprd/carga_$data.sql.gz
