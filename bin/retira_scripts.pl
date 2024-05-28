#!/usr/bin/perl

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


$buff = "";
$script = 0;
while (<STDIN>) {
	if ($script==0 && m/\<script type="text\/javascript"/) {
		$buf = $_;
		$script = 1;
	}
	if ($script==1 && m/\<\/script\>/) {
		if ($buf ne $_) {
			$buf = $buf . $_;
		}
		$buf =~ s/\<script type="text\/javascript".*?\<\/script\>//gs;
		print $buf;
		$buf = "";
		$script = 0;
	}
	elsif ($script==1) {
		$buf = $buf . $_;
	}
	else {
		print $_;
	}
}
