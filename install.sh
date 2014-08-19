#!/usr/bin/env bash
# Install Script for BrainSuite statistical toolbox for Linux/MacOSX
# This file is a part of the BrainSuite statistical toolbox

#Copyright (C) Shantanu H. Joshi, Garrett Reynolds, David Shattuck,
#Brain Mapping Center, University of California Los Angeles

#Bss is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#Bss is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
#__author__ = "Shantanu H. Joshi, Garrett Reynolds, Jonathan Pierce"
#__copyright__ = "Copyright 2014 Shantanu H. Joshi, Garrett Reynolds, Jonathan Pierce, David Shattuck,
#				  Ahmanson Lovelace Brain Mapping Center, University of California Los Angeles"
#__email__ = "sjoshi@bmap.ucla.edu"

message_if_failed() {
    #print out message and quit if last command failed
    if [ $? -ne 0 ]; then 
        echo -e >&2 $1
        exit 2
    fi
}
if [ $# -ne 1 ]
  then
    echo "usage: $0 <full path of the install directory>"
    echo "Install the BrainSuite Statistical toolbox in the specified directory."
    exit 0
fi

echo "This will install the BrainSuite Statistics toolbox. "
echo "This will also install a mini version of anaconda python, rpy2, and statsmodels."
# Check if curl exists
curl --help >> /dev/null
curl_exists=$?
if [ ${curl_exists} != 0 ]; then
    printf "\nThe program curl is not installed. Please install curl and retry installing the toolbox.\n"
    exit 0
fi

VER=3.5.5
R_data_table_package="data.table"
echo "'${R_data_table_package}' %in% rownames(installed.packages())" | R --quiet --no-save | grep -q "TRUE" #this will have exit code zero if package is installed
package_is_installed=$?
if [ $package_is_installed == 0 ]; then
    echo -e "\nGood, R package ${R_data_table_package} is already installed.\n"
else
    echo -e "\nR package ${R_data_table_package} is not installed. Please install data.table first then re-run the installation script.\n"
    printf "\nExiting now.\n"
    exit 0
fi

orig_dir=`pwd`
install_dir=$1

if [ -d "$install_dir" ]; then
	echo "Directory $install_dir exists. Aborting installation."
	exit 0
fi

mkdir "$install_dir"
mkdir "$install_dir"/"tmp"

osname=`uname`
if [[ "$osname" == "Darw"* ]]; then
	platform="MacOSX"
else
	platform="Linux"
fi;

echo "Downloading anaconda python...This may take a few minutes..."
curl -o ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh http://repo.continuum.io/miniconda/Miniconda-${VER}-${platform}-x86_64.sh
chmod +x ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh
echo "Done."
echo -n "Installing anaconda python..."
${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh -b -f -p ${install_dir} 1> ${install_dir}/tmp/install.log
echo "Done."
   
${install_dir}/bin/conda install pip -q --yes 1>> ${install_dir}/tmp/install.log

echo -n "Installing rpy2...This may take a few minutes..."
if [[ "$platform" == "Linux" ]]; then
    echo "LD_LIBRARY_PATH is "$LD_LIBRARY_PATH | tee -a ${install_dir}/tmp/install.log
    ${install_dir}/bin/pip install rpy2>> ${install_dir}/tmp/install.log
	#${install_dir}/bin/conda install -c https://conda.binstar.org/r rpy2 --yes -q 1>> ${install_dir}/tmp/install.log
elif [[ "$platform" == "MacOSX" ]]; then
    echo "DYLD_LIBRARY_PATH is "$DYLD_LIBRARY_PATH | tee -a ${install_dir}/tmp/install.log
	${install_dir}/bin/pip install rpy2>> ${install_dir}/tmp/install.log
fi;

if [ "$?" = "0" ]; then
	echo "Done."
else
	printf "There was a problem installing rpy2.\n" 1>&2
	printf "Either R was not installed as a shared library or R_HOME and/or LD_LIBRARY_PATH is not set\n" 1>&2
	printf "Please fix the R installation/paths and try reinstalling the toolbox.\n" 1>&2
	printf "Quitting without installing the BrainSuite Statistics toolbox.\n" 1>&2
	exit 1
fi

echo -n "Installing statsmodels...This may take a few minutes..."
${install_dir}/bin/conda install statsmodels -q --yes 1>> ${install_dir}/tmp/install.log
echo "Done."

# The following line is only to suppress the openpyxl warning in pandas. Will be removed in future installations.
${install_dir}/bin/conda install -q --yes openpyxl=1.8 >> ${install_dir}/tmp/install.log

echo -n "Installing BrainSuite statistical toolbox...This may take a few minutes..."
${install_dir}/bin/conda install --yes -c https://conda.binstar.org/shjoshi bss
echo "Done."
if [[ "$platform" == "Linux" ]]; then
    ${install_dir}/bin/conda remove -q --yes readline >> ${install_dir}/tmp/install.log # This is a workaround for the "libreadline.so not found" error. Temporary fix.
fi;

if [[ ${install_dir} = /* ]];
then
    # Absolute path
    install_bin_abs_path="${install_dir}/bin"
else
    # Relative path
    install_bin_abs_path=$(echo $PWD/$(basename ${install_dir})"/bin")
fi

if [[ -f ~/.bashrc ]]
then
    printf "Making a backup of the ~/.bashrc to ~/.bashrc.BAK just in case\n"
    cp ~/.bashrc ~/.bashrc.BAK
fi

if [[ "$platform" == "Linux" ]]; then
    R_HOME=`R RHOME`
    read -p "Would you like to modify your ~/.bashrc to add to LD_LIBRARY_PATH? [y/n] " yn
    case $yn in
        [Yy]* )
            echo "export LD_LIBRARY_PATH=${R_HOME}/lib:${LD_LIBRARY_PATH}" >> ~/.bashrc;
            printf "Modified ~/.bashrc\n";;
        [Nn]* )
            printf "~/.bashrc not modified. You may have to set the LD_LIBRARY_PATH manually as\n";
            printf "export LD_LIBRARY_PATH=${R_HOME}/lib:${LD_LIBRARY_PATH}\n";;
        * )
            printf "~/.bashrc not modified. You may have to set the LD_LIBRARY_PATH manually as\n";
            printf "export LD_LIBRARY_PATH=${R_HOME}/lib:${LD_LIBRARY_PATH}\n";;
    esac
    echo "export LD_LIBRARY_PATH=${R_HOME}/lib:${LD_LIBRARY_PATH}\n" 1>> ${install_dir}/tmp/install.log
fi

read -p "Would you like to modify your ~/.bashrc PATH to include paths to the installation directory? [y/n] " yn
case $yn in
    [Yy]* )
            echo "export PATH=${install_bin_abs_path}:\${PATH}" >> ~/.bashrc;
            printf "Modified ~/.bashrc to add the path ${install_bin_abs_path}\n";;
    [Nn]* )
            printf "~/.bashrc not modified. You may either have to set the PATH manually,\n";
            printf "or run the commands from ${install_dir}/bin\n";
            printf "export PATH=${install_bin_abs_path}:\${PATH}\n";;
    * )
            printf "~/.bashrc not modified. You may either have to set the PATH manually,\n";
            printf "or run the commands from ${install_dir}/bin\n";
            printf "export PATH=${install_bin_abs_path}:\${PATH}\n";;
esac

echo "export PATH=${install_bin_abs_path}:\${PATH}\n" 1>> ${install_dir}/tmp/install.log

printf "BrainSuite statistical toolbox was installed successfully.\n"
printf "Cleaning up temporary files..."
rm -r ${install_dir}/pkgs/
rm -r ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh
printf "Done.\n\n"

printf "To test...\n"
printf "Run source ~/.bashrc if you modified your bashrc.\n"
if [[ "$platform" == "Linux" ]]; then
    printf "Or set the LD_LIBRARY_PATH manually as shown above.\n"
fi
printf "Try running\n ${install_dir}/bin/bss_run.py -h \n"
printf "It should display help and then exit.\n\n\n"

exit 0
