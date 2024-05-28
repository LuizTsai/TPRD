#!/bin/sh

#
# Copyright 2015 Leandro Dybal Bertoni - All Rights Reserved
#


if [ $# -ne 3 ]; then
	echo "Uso: envia_bvd.sh <directory> <file> <password>"
  exit 1
fi

# Get script arguments
directory=$1
file=$2
password=$3
start_time=(`date  "+%Y%m%d%H%M"` + %s)
done_file="bvd_envio_$start_time.txt"

cd $directory

if [ ! -f "$file" ]; then
  echo "Erro: arquivo $file não existe" >> $LOG_DIRECTORY/$done_file
  echo "Executado para mais detalhes verificar o log na pasta $LOG_DIRECTORY"
  exit 1
fi

# VcqUgcrrp3cyxBbi

echo "1" > $LOG_DIRECTORY/$done_file
sftp tprd@sftpip.bvdinfo.com <<ENDSSH
passive
binary
put $directory/$file
ls
quit
ENDSSH

# Check for transfer errors
if [ $? -ne 0 ]; then
  error_message=$(tail -1 $LOG_DIRECTORY/$done_file)
  echo "Erro ao transferir o arquivo $file: $error_message" >> $LOG_DIRECTORY/$done_file
  echo "Executado para mais detalhes verificar o log na pasta $LOG_DIRECTORY"
  exit 1
fi

# Get transfer statistics
transferred_bytes=$(wc -c < $LOG_DIRECTORY/$done_file)
#transfer_time=$(($(date + %s) - $(date -d "$start_time" + %s)))

# Update Done.txt with success message
echo "Transferência do arquivo $arquivo concluída com sucesso." >> $LOG_DIRECTORY/$done_file
echo "Bytes transferidos: $transferred_bytes" >> $LOG_DIRECTORY/$done_file
#echo "Tempo total: $transfer_time segundos" >> $LOG_DIRECTORY/$done_file


echo "Executado para mais detalhes verificar o log na pasta $LOG_DIRECTORY"
# Exit with success code
exit 0