#!/bin/sh

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

home=/devel/diego/TPRD

run_dir="/devel/diego/TPRD/capta/run/bmf"
bin_dir="${home}/carga"
. $bin_dir/carga


descompacta() {
	if [ -h "$1" ]; then
		zip=`ls -l $i | sed "s/.*-> //"`
		if [ -f "$zip" ] ; then
			echo "`date`: Processando arquivo $i ($zip)"
			mv $1 processando/
			cd processando
			dir=`basename $zip`
			mkdir $dir
			unzip $zip -d $dir
			carrega "bmf" $dir/BD_Final.txt
			r=$?
			 rm -rf $dir
			cd ..
			if [ $r -eq 0 ]; then
				mv processando/$1 processado/
			else
				mv processando/$1 erro/ 
			fi
			sleep 2
		fi
	fi
}

converte() {
        if [ -h "$1" ]; then
                pdf=`ls -l $i | sed "s/.*-> //"`
                if [ -f "$pdf" ] ; then
                        echo "`date`: Processando arquivo $i ($pdf)"
                        mv $1 processando/
                        cd processando
                        dir=`basename $pdf`
                        mkdir $dir
			$bin_dir/pdfparatxt $pdf > $dir/$pdf
			echo "pdfparatxt $pdf > $dir/pdf"
                        carrega "bmf" $dir/$pdf
                        r=$?
                         rm -rf $dir
                        cd ..
                        if [ $r -eq 0 ]; then
                                mv processando/$1 processado/
                        else
                                mv processando/$1 erro/
                        fi
                        sleep 2
                fi
        fi
}

echo $run_dir
cd $run_dir
for i in `ls`; do
	if [ -f $i ]; then
		echo "============================================================="


                        echo "`date`: Processando arquivo $i"
                        mv $1 processando/
                        cd processando
                        dir=`basename dir_$i`
                        mkdir $dir
echo "$bin_dir/pdfparatexto.py $run_dir/$i > $dir/$i"
                        $bin_dir/pdfparatexto.py $run_dir/$i > $dir/$i


		carrega "bmf" "$run_dir/processando/$dir/$i" 

                        r=$?
                         rm -rf $dir
                        cd ..
                        if [ $r -eq 0 ]; then
                                mv $i processado/
                        else
                                mv $i erro/
                        fi
                        sleep 2


	        echo ""
	fi
done

