#!/bin/sh

##########################################################
# Change the following values as neccesary:              #
##########################################################
instpath="/usr/lib/python*"
lninstpath="/usr/bin"
docpath="/usr/share/doc/pak"

#########################################################
# Install module                                        #
########################################################
echo -e "Installing pak... \c"
rm ${lninstpath}/pak
cp ./pak.py $instpath
ln ${instpath}/pak.py ${lninstpath}/pak
echo "done"
pwd=`pwd`
mkdir $docpath
./generate.py
cp *.html $docpath
cd $pwd
echo "Done installing."
echo "The pak module is in $instpath and the documentation is in $docpath ."
echo
