#!/bin/bash

#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#


. $HOME/bin/http_proxy 
. $HOME/bin/funcoes_download

data_dir="$HOME/data/mcx"
#data_dir="$HOME/tmp"

echo ""
if [ $# -eq 0 ]; then
        data=`date -d yesterday "+%Y%m%d"`
        echo "Baixando arquivo da MCX para ontem ($data)"
else
        data=$1
        echo "Baixando arquivo da MCX para o dia $data"
fi

ano=`echo $data | sed -n "s/^\([0-9]\{4\}\).*/\1/p"`
mes=`echo $data | sed -n "s/^[0-9]\{4\}\([0-9]\{2\}\).*/\1/p"`
dia=`echo $data | sed -n "s/^[0-9]\{6\}\([0-9]\{2\}\).*/\1/p"`

#mes_a=$(($mes-1))
mes_a=$((`echo $mes | sed -n "s/^0*//p"` - 1))

delay

cd $data_dir
run_dir="/home/capta/run/mcx"

while [ 1 ]; do
	download=`date "+%Y%m%d%H%M"`
	#baixa "http://www.mcxindia.com/SitePages/BhavCopyDateWise.aspx" "lixo/lixo" "html"
	baixa "https://www.mcxindia.com/market-data/bhavcopy" "lixo/lixo" "html" "--save-cookies /tmp/cookies-mcx-1 --keep-session-cookies"
	ret=$?
	if [ $ret -eq 0 ]; then
		eventTarget=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__EVENTTARGET\"" | head -n 1 | sed -n "s/^.*name=\"__EVENTTARGET\" id=\"__EVENTTARGET\" value=\"\([^\"]*\)\".*/\1/p"`
		eventTarget=`echo -n $eventTarget | percent_encode`

		eventArgument=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__EVENTARGUMENT\"" | head -n 1 | sed -n "s/^.*name=\"__EVENTTARGET\" id=\"__EVENTTARGET\" value=\"\([^\"]*\)\".*/\1/p"`
		eventTarget=`echo -n $eventTarget | percent_encode`

		eventValidation=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__EVENTVALIDATION\"" | head -n 1 | sed -n "s/^.*name=\"__EVENTTARGET\" id=\"__EVENTTARGET\" value=\"\([^\"]*\)\".*/\1/p"`
		eventTarget=`echo -n $eventTarget | percent_encode`

		viewState=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__VIEWSTATE\"" | head -n 1 | sed -n "s/^.*name=\"__VIEWSTATE\" id=\"__VIEWSTATE\" value=\"\([^\"]*\)\".*/\1/p"`
		viewState=`echo -n $viewState | percent_encode`

		TSM_CombinedScripts_1=`cat tudo/lixo/lixo_${data}_${download}.html | grep "_TSM_CombinedScripts_"  |i head -n 1 | sed -n "s/^.*_TSM_CombinedScripts_=\([^\"]*\)\".*/\1/p" | tr -d '\n'`
		TSM_CombinedScripts_todos=`cat tudo/lixo/lixo_${data}_${download}.html | grep "_TSM_CombinedScripts_"  | sed -n "s/^.*_TSM_CombinedScripts_=\([^\"]*\)\".*/\1/p" | tr -d '\n'`


		viewState=`cat tudo/lixo/lixo_${data}_${download}.html | grep "name=\"__VIEWSTATE\"" | head -n 1 | sed -n "s/^.*name=\"__VIEWSTATE\" id=\"__VIEWSTATE\" value=\"\([^\"]*\)\".*/\1/p"`
		viewState=`echo -n $viewState | percent_encode`
		sm_TSM=`cat tudo/lixo/lixo_${data}_${download}.html | grep "TSM_HiddenField" | head -n 1 | sed -n "s/^.*_TSM_CombinedScripts_=\([^\"]*\)\".*/\1/p"`
		ctl07_TSSM=`cat tudo/lixo/lixo_${data}_${download}.html | grep "hf.value +=" | head -n 1 | sed -n "s/^.*hf.value *+= *'\([^']*\)'.*/\1/p"`
		ctl07_TSSM=`echo -n $ctl07_TSSM | percent_encode`
##		rm $data_dir/tudo/lixo*

		#echo -n "__EVENTARGUMENT=&__EVENTTARGET=ctl00%24cph_InnerContainerRight%24C001%24lnkExpToCSV&__EVENTVALIDATION=${eventValidation}&__VIEWSTATE=${viewState}&__VIEWSTATEENCRYPTED=&__VIEWSTATEGENERATOR=${viewStateGenerator}&}&ctl00_cph_InnerContainerRight_BreadCrumb_T9DC6B4FB006_ctl00_ctl00_Breadcrumb_ClientState=&ctl00_cph_InnerContainerRight_C001_ddlSymbols_ClientState=&ctl00_cph_InnerContainerRight_C001_rg_ClientState=&ctl00_cph_nav_container_searchbox_T9DC6B4FB016_radDDL_ClientState=&ctl00%24cph_InnerContainerRight%24C001%24ddlSymbols=ALL&ctl00%24cph_InnerContainerRight%24C001%24hdnCommodityInstrumentName=&ctl00%24cph_InnerContainerRight%24C001%24hdnExpiry=&ctl00%24cph_InnerContainerRight%24C001%24hdnFromDate=&ctl00%24cph_InnerContainerRight%24C001%24hdnInstrumentName=ALL&ctl00%24cph_InnerContainerRight%24C001%24hdnSymbols=&ctl00%24cph_InnerContainerRight%24C001%24hdnToDate=&ctl00%24cph_InnerContainerRight%24C001%24txtDate_hid_val=${ano}${mes}${dia}&ctl00%24cph_nav_container_navbar_header_mobile_main_menu2%24T9DC6B4FB018%24ctl00%24ctl00%24langsSelect=https://www.mcxindia.com/market-data/bhavcopy&ctl00%24cph_nav_container_searchbox_mobile%24T9DC6B4FB019%24ddlProducts=GetQuote&ctl00%24cph_nav_container_searchbox%24T9DC6B4FB016%24radDDL=Get+Quotectl00%24cph_nav_container_topbar_language%24T9DC6B4FB015%24ctl00%24ctl00%24langsSelect=https://www.mcxindia.com/market-data/bhavcopy&ctl00%24hdnCurrentCulture=en&ctl00%24sm&sm_TSM=${sm_TSM}&ctl07_TSSM=${ctl07_TSSM}" > tudo/post_data.txt
		echo -n "__EVENTARGUMENT=&__EVENTTARGET=ctl00%24cph_InnerContainerRight%24C001%24lnkExpToCSV&__EVENTVALIDATION=${eventValidation}&__VIEWSTATE=${viewState}&__VIEWSTATEENCRYPTED=&__VIEWSTATEGENERATOR=${viewStateGenerator}&ctl00%24cph_InnerContainerRight%24C001%24txtDate_hid_val=${ano}${mes}${dia}&ctl00_cph_InnerContainerRight_BreadCrumb_T9DC6B4FB006_ctl00_ctl00_Breadcrumb_ClientState=&ctl00_cph_InnerContainerRight_C001_ddlSymbols_ClientState=&ctl00_cph_InnerContainerRight_C001_rg_ClientState=&ctl00_cph_nav_container_searchbox_T9DC6B4FB016_radDDL_ClientState=&ctl00%24cph_InnerContainerRight%24C001%24ddlSymbols=ALL&ctl00%24cph_InnerContainerRight%24C001%24hdnCommodityInstrumentName=&ctl00%24cph_InnerContainerRight%24C001%24hdnExpiry=&ctl00%24cph_InnerContainerRight%24C001%24hdnFromDate=&ctl00%24cph_InnerContainerRight%24C001%24hdnInstrumentName=ALL&ctl00%24cph_InnerContainerRight%24C001%24hdnSymbols=&ctl00%24cph_InnerContainerRight%24C001%24hdnToDate=&ctl00%24cph_nav_container_navbar_header_mobile_main_menu2%24T9DC6B4FB018%24ctl00%24ctl00%24langsSelect=https://www.mcxindia.com/market-data/bhavcopy&ctl00%24cph_nav_container_searchbox_mobile%24T9DC6B4FB019%24ddlProducts=GetQuote&ctl00%24cph_nav_container_searchbox%24T9DC6B4FB016%24radDDL=Get+Quotectl00%24cph_nav_container_topbar_language%24T9DC6B4FB015%24ctl00%24ctl00%24langsSelect=https://www.mcxindia.com/market-data/bhavcopy&ctl00%24hdnCurrentCulture=en&ctl00%24sm&ctl07_TSSM=${TSM_CombinedScripts_1}&sm_TSM=${TSM_CombinedScripts_todos}" > tudo/post_data.txt

		baixa "https://www.mcxindia.com/market-data/bhavcopy" "MCX" "csv" "--load-cookies /tmp/cookies-mcx-1  --referer=\"http://www.mcxindia.com/market-data/bhavcopy\" --no-cache --post-file=tudo/post_data.txt"
		ret=$?
			if [ $ret -eq 0 ]; then
        			fl=`file "tudo/MCX_${data}_${download}.csv" | grep "HTML document"`
			        if [ -n "$fl" ]; then
			                echo "`date`: Arquivo tudo/MCX_${data}_${download}.csv é HTML, descartando"
					mailx -s "down_mcx: arquivo MCX para $data inválido (HTML ao invés de CSV!)"  capta <<FIM
				                `head -n 3 tudo/MCX_${data}_${download}.csv`
FIM
			                mv "tudo/MCX_${data}_${download}.csv" "tudo/lixo/MCX_${data}_${download}.html"
				        #        rm "tudo/MCX_${data}_${download}.csv"
			                exit 1
			        fi
			        fl=`file "tudo/MCX_${data}_${download}.csv" | grep "text"`
			        if [ -z "$fl" ]; then
			                echo "`date`: Arquivo tudo/MCX_${data}_${download}.csv não é texto, mudando de proxy e tentando novamente..."
			                mv "tudo/MCX_${data}_${download}.csv" "tudo/lixo/MCX_${data}_${download}.csv"
			       #        rm "tudo/MCX_${data}_${download}.csv"
					sleep 8
					obtem_proxy
        			else
				        fl=`grep -e "Date,Commodity Symbol,Contract/Expiry Month,Open(Rs),High(Rs),Low(Rs),Close(Rs),PCP(Rs),Volume(In Lots),Volume(In 000's),Value(In Lakhs),OI(In Lots)" -e "\"Date\",\"Symbol\",\"Expiry Date\",\"Open\",\"High\",\"Low\",\"Close\",\"Previous Close\",\"Volume\",\"Volume(In 000's)\",\"Value\",\"Open Interest\"" "tudo/MCX_${data}_${download}.csv"`
				        if [ -z "$fl" ]; then
				                echo "PROBLEMAS: Linha de cabeçalho não encontrada no arquivo baixado, possível mudança de layout!"
				                mailx -s "down_mcx: arquivo MCX para $data inválido" capta <<FIM
		 Linha de cabeçalho não encontrada em `echo tudo/MCX_${data}_${download}.csv`

                `head -n 3 tudo/MCX_${data}_${download}.csv`
FIM
			                	mv "tudo/MCX_${data}_${download}.csv" "tudo/lixo/MCX_${data}_${download}.csv"

                				exit 2
				        fi
				        linka_se_novo "MCX" "csv"
				        ret=$?
					rm tudo/lixo/lixo*
				        exit $ret
				fi
			fi
	fi
done
