#! /bin/bash

. ~/.bashrc
conda env create -f ./conda/environment_phenom_distribution_ppe.yml
conda activate phenom-distribution-ppe
conda install -y ipykernel

git clone https://github.com/tedwards2412/ripple.git ../ripple-phenom-distribution-ppe-temp
git -C ../ripple-phenom-distribution-ppe-temp checkout 320fcaa3fca680e12a1df6ec6213f54a9a19db53
cp ./conda/scripts-to-replace/ripple/IMRPhenomD.py ../ripple-phenom-distribution-ppe-temp/src/ripple/waveforms/IMRPhenomD.py
echo
echo "src/ripple/waveforms/IMRPhenomD.py has been modified to include inspiral ppE phasing"
cp ./conda/scripts-to-replace/ripple/setup.cfg ../ripple-phenom-distribution-ppe-temp/setup.cfg
echo
echo "setup.cfg has been modified to avoid reinstalling jax and jaxlib"
echo
pip3 install --force-reinstall --ignore-installed --no-cache-dir ../ripple-phenom-distribution-ppe-temp/
rm -rf ../ripple-phenom-distribution-ppe-temp

pip install jaxlib==0.4.1 -f https://storage.googleapis.com/jax-releases/jax_releases.html

git clone https://github.com/bilby-dev/bilby.git ../bilby-phenom-distribution-ppe-temp
git -C ../bilby-phenom-distribution-ppe-temp checkout 49c1c393808469c13dd266445732f050eb1e4f6a
cp ./conda/scripts-to-replace/bilby/source.py ../bilby-phenom-distribution-ppe-temp/bilby/gw/source.py
echo
echo "bilby/gw/source.py has been modified to include ripple_binary_black_hole and ripple_binary_black_hole_ppe"
cp ./conda/scripts-to-replace/bilby/joint.py ../bilby-phenom-distribution-ppe-temp/bilby/core/prior/joint.py
echo
echo "bilby/core/prior/joint.py has been modified to allow singular values in the multivariate Gaussian (line 578)"
cp ./conda/scripts-to-replace/bilby/requirements.txt ../bilby-phenom-distribution-ppe-temp/requirements.txt
echo
echo "requirements.txt has been modified to avoid package conflicts"
echo
pip3 install --force-reinstall --ignore-installed --no-cache-dir ../bilby-phenom-distribution-ppe-temp/
rm -rf ../bilby-phenom-distribution-ppe-temp

conda install -y conda-forge::python-nds2-client
conda install -y conda-forge::python-ldas-tools-framecpp
conda install -y -c conda-forge schwimmbad=0.3.2
pip install lalsuite==7.11
pip install mpi4py==3.1.6

read -rp "Create an IPython kernel named 'phenom-distribution-ppe'? [y/N] " ans
if [[ "$ans" =~ ^[Yy]$ ]]; then
  python -m ipykernel install --user --name=phenom-distribution-ppe
fi

echo
echo "If you need to remove the conda environment and the IPython kernel later, run:"
echo "  conda remove -n phenom-distribution-ppe --all"
echo "  jupyter kernelspec uninstall phenom-distribution-ppe"