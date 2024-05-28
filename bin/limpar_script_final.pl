#!/usr/bin/perl

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#



while (<STDIN>) {
	if (m/<\/html>/) {
		print $_;
		exit;
	}
	else {
		print $_;
	}
}
