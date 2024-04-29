# HyP3 back-projection

HyP3 plugin for back-projection processing

### GPU Setup:
In order for Docker to be able to use the host's GPU, the host must have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) installed and configured. 
The process is different for different OS's and Linux distros. The setup process for the most common distros, including Ubuntu, 
can be found [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration). Make sure to follow the [Docker configuration steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) after installing the package. **This process is not necessary when running in AWS while using an EC2 image made with GPU support.**