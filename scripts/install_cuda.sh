# Script to install nvidia drivers and the nvidia cuda toolkit.

# Install Cuda Toolkit 12.4
# Source: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_local
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin && \
mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-ubuntu2004-12-4-local_12.4.1-550.54.15-1_amd64.deb && \
dpkg -i cuda-repo-ubuntu2004-12-4-local_12.4.1-550.54.15-1_amd64.deb && \
cp /var/cuda-repo-ubuntu2004-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/ && \
apt-get update && \
apt-get -y install cuda-toolkit-12-4
