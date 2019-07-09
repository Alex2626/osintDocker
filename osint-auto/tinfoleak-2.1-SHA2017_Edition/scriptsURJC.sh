#!/bin/bash

users=(eldiarioes urjc la9deanon genbeta nonymousNews AnonNic )
words=(urjc URJC masterurjc cifuentes URJCHack)

sdate=$(date -d "1 week ago" -I)
edate=$(date -I)

#./tinfoleak.py -u la9deanon -t 1000 --sdate 2017:03:21 --edate 2018:06:05 --find [+]urjc  -o urjcPruebas.html

#./tinfoleak.py -u urjc -t 500 --sdate 2018-03-01 --edate 2018-06-07 --mentions --hashtags --find [+]urjc --search -o urjcPruebas2.html

#./tinfoleak.py -u urjc -t 500 -i --sdate 2018-06-01 --edate 2018-06-11 --mentions --find [+]urjc --search -o urjcPruebas1.html

#./tinfoleak.py -u eldiarioes -t 500 -i --sdate 2018-06-01 --edate 2018-06-11 --mentions --find [+]urjc --search -o urjcPruebas2.html

#Get all the tweets from one week ago where appear "urjc" in the TL of black list's users
function getReportsUsersURJC(){
	for user in "${users[@]}"
	do		
		ofileName="USER""$user""_""$edate".html
		./tinfoleak.py -u $user -t 200 -i --sdate $sdate --edate $edate --hashtags --mentions --find [+]urjc -o $ofileName
		saveReport
		
	done
}

#Get tweets in Global TL where appear any of black list's words
function getTwitterAdvancedSearch(){
	for word in "${words[@]}"
	do		
		ofileName="adSEARCH""$word""_""$edate".html		
		./tinfoleak.py -u urjc -t 200 -i --sdate $sdate --edate $edate --find [+]$word --search -o $ofileName
		#./tinfoleak.py -u urjc -t 200 -i --sdate 2018-1-01 --edate 2018-06-12 --find [+]urjc --search -o pruebaCOnsola1.html

		saveReport
		
	done
}

function saveReport(){
	cd ./Output_Reports
	mv $ofileName $edate
	echo "Se ha cambiado el fichero a su directorio correctamente"
	cd /root/Tools/tinfoleak-2.1-SHA2017_Edition
}


function createZip(){
	cd ./Output_Reports
	zip -r 'Tinfoleak-'${edate}.zip $edate 
}

function sendInform(){
	python /root/Tools/PythonScripts/sendMailZipOutlook.py -i /root/Tools/tinfoleak-2.1-SHA2017_Edition/Output_Reports/${edate}.zip
	
}

#######################################################################################################

echo Accediendo a Tinfoleak...
cd /root/Tools/tinfoleak-2.1-SHA2017_Edition
echo Ejecutando Tinfoleak

cd ./Output_Reports
mkdir $edate
cd $edate
echo "Creada carpeta correctamente"
cd /root/Tools/tinfoleak-2.1-SHA2017_Edition

cd ./Output_Reports
cp ./style.css $edate
echo "Se ha copiado el fichero CSS correctamente"
cd /root/Tools/tinfoleak-2.1-SHA2017_Edition

echo
echo "****************************************************************************"
echo "****************************************************************************"
echo "****************************************************************************"
echo "***********************   BUSQUEDA USERS BLACK LIST  ***********************"
echo "****************************************************************************"
echo "****************************************************************************"
echo "****************************************************************************"
echo 

getReportsUsersURJC

echo
echo "****************************************************************************"
echo "****************************************************************************"
echo "****************************************************************************"
echo "***********************   ADVANCED SEARCH            ***********************"
echo "****************************************************************************"
echo "****************************************************************************"
echo "****************************************************************************"
echo 

./tinfoleakCopia.py -u urjc -t 200 -i --sdate $sdate --edate $edate --find [+]urjc --search -o pruebaCOnsola2.html

getTwitterAdvancedSearch

echo
echo Comprimiendo carpeta...
echo

ls 
createZip

echo
echo Enviando informe...
echo

sendInform