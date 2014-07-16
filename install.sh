#!/usr/bin/env bash
#Install Script for BrainSuite statistical toolbox for Linux/MacOSX
#
#__author__ = "Shantanu H. Joshi, Garrett Reynolds"
#__copyright__ = "Copyright 2014 Shantanu H. Joshi, Garrett Reynolds, David Shattuck, 
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

echo "This will install the BrainSuite Statistics toolbox. "
echo "This will also install a mini version of anaconda python, rpy2, statsmodels and R data.table."
VER=3.5.5
echo "Downloading anaconda python...This may take a few minutes..."
curl -o ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh http://repo.continuum.io/miniconda/Miniconda-${VER}-${platform}-x86_64.sh
chmod +x ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh
echo "Done."
echo -n "Installing anaconda python..."
${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh -b -f -p ${install_dir} 1> ${install_dir}/tmp/install.log
echo "Done."
   
R_data_table_package="data.table"
echo "'${R_data_table_package}' %in% rownames(installed.packages())" | R --quiet --no-save | grep -q "TRUE" #this will have exit code zero if package is installed
package_is_installed=$?
if [ $package_is_installed == 0 ]; then
    echo -e "\nGood, R package ${R_data_table_package} is already installed.\n"
else
	#Create a library path
    R_lib_path=${install_dir}/Rlibs
    mkdir $R_lib_path
    echo -e "\nR package ${R_data_table_package} is not installed, installing it now in ${R_lib_path}...\n"
    #install packages
    echo "install.packages('${R_data_table_package}', repos='http://cran.us.r-project.org', lib='${R_lib_path}')" | R --quiet --no-save 1>> ${install_dir}/tmp/install.log
    message_if_failed "ERROR: failed to install data.table package for R. Exitting..."
    #Create a .Rprofile in user's HOME to make sure R can find this library.
    echo -e ".libPaths( c( .libPaths(), '${R_lib_path}'))" >> "${HOME}/.Rprofile"
    message_if_failed "\nWARNING: Was not able to create a .Rprofile that would add ${R_lib_path} to the R's .libPaths()"
fi

${install_dir}/bin/conda install pip -q --yes 1>> ${install_dir}/tmp/install.log

echo -n "Installing rpy2...This may take a few minutes..."
if [[ "$platform" == "Linux" ]]; then
	${install_dir}/bin/conda install -c https://conda.binstar.org/r rpy2 --yes -q 1>> ${install_dir}/tmp/install.log
elif [[ "$platform" == "MacOSX" ]]; then
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

echo "R_LIBS=${R_lib_path}:$R_LIBS; export R_LIBS" >> ~/.bashrc
echo "R_LIBS=${R_lib_path}:$R_LIBS; export R_LIBS" >> ~/.bash_profile
echo "setenv R_LIBS ${R_lib_path}:$R_LIBS" >> ~/.tcshrc
source ~/.bashrc

# The following line is only to suppress the openpyxl warning in pandas. Will be removed in future installations.
${install_dir}/bin/conda install -q --yes openpyxl=1.8 >> ${install_dir}/tmp/install.log

echo -n "Installing BrainSuite statistical toolbox...This may take a few minutes..."
${install_dir}/bin/conda install --yes -c https://conda.binstar.org/shjoshi bss
echo "Done."
echo "BrainSuite statistical toolbox was installed successfully"
rm -r ${install_dir}/pkgs/
rm -r ${install_dir}/tmp/Miniconda-${VER}-${platform}-x86_64.sh
exit 0
