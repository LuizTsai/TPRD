#!/usr/bin/perl

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


while (<STDIN>) {
if (m/.*Clique para obter a tabela completa \(<A href ="([^"]*)".*/) {print $1; exit;} 
}

