# HyP3 back-projection

HyP3 plugin for back-projection processing

## Usage
> [!WARNING]
> Running the workflows in this repository requires a compiled version of the [Stanford Radar Group Processor](https://github.com/asfhyp3/back-projection). For this reason, running this repository's workflows in a standard Python is not implemented yet. Instead, we recommend running the workflows from the docker container as outlined below.

The HyP3-back-projection plugin provides a set of workflows (currently only accessible via the docker container) that can be used to process SAR data using the [Stanford Radar Group Processor](https://github.com/asfhyp3/back-projection). The workflows currently included in this plugin are:

- `back_projection`: A workflow for creating geocoded Sentinel-1 SLCs from Level-0 data using the [back-projection methodology](https://doi.org/10.1109/LGRS.2017.2753580).

To run a workflow, you'll first need to build the docker container:
```bash
docker build -t back-projection:latest .
```
Then, run the docker container for your chosen workflow.
```bash
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    -e ESA_USERNAME=[YOUR_USERNAME_HERE] \
    -e ESA_PASSWORD=[YOUR_PASSWORD_HERE] \
    back-projection:latest \
    ++process [WORKFLOW_NAME] \
    [WORKFLOW_ARGS]
```
Here is an example command for the `back_projection` workflow:
```bash
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    -e ESA_USERNAME=[YOUR_USERNAME_HERE] \
    -e ESA_PASSWORD=[YOUR_PASSWORD_HERE] \
    back-projection:latest \
    ++process back_projection \
    S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42-RAW \
    S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38-RAW
```

## Earthdata Login and ESA Credentials

For all workflows, the user must provide their Earthdata Login credentials and ESA Copernicus Data Space Ecosystem (CDSE) credentials in order to download input data.

If you do not already have an Earthdata account, you can sign up [here](https://urs.earthdata.nasa.gov/home).

If you do not already have a CDSE account, you can sign up [here](https://dataspace.copernicus.eu).

Your credentials can be passed to the workflows via command-line options (`--esa-username` and  `--esa-password`), environment variables
(`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`, `ESA_USERNAME`, and `ESA_PASSWORD`), or via your `.netrc` file.

If you haven't set up a `.netrc` file
before, check out this [guide](https://harmony.earthdata.nasa.gov/docs#getting-started) to get started.

## GPU Setup:
In order for Docker to be able to use the host's GPU, the host must have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) installed and configured. 
The process is different for different OS's and Linux distros. The setup process for the most common distros, including Ubuntu, 
can be found [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration). Make sure to follow the [Docker configuration steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) after installing the package.

### EC2 Setup
When running on an EC2 instance, the following setup is recommended:
1. Create a [P3-family EC2 instance](https://aws.amazon.com/ec2/instance-types/p3/) with the [Amazon Linux 2 AMI with NVIDIA TESLA GPU Driver](https://aws.amazon.com/marketplace/pp/prodview-64e4rx3h733ru?sr=0-4&ref_=beagle&applicationId=AWSMPContessa)
2. Install Docker and the nvidia-container-toolkit on the EC2
```bash
sudo yum-config-manager --disable amzn2-graphics
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo yum install docker -y
sudo yum install nvidia-container-toolkit -y
sudo yum-config-manager --enable amzn2-graphics
```
3. Optionally, set up Docker to not require `sudo` and to start when the instance starts
```bash
sudo systemctl start docker && \
sudo usermod -a -G docker ec2-user && \
sudo systemctl enable docker
```
4. Exit the instance and re-enter
5. To test the GPU setup, run the base NVIDIA container:
```bash
docker run -it --gpus all nvidia/cuda:12.4.1-devel-ubuntu20.04 nvidia-smi
```
6. Build the actual container and run it:
```bash
docker build -t back-projection:gpu -f Dockerfile.gpu .
docker run --gpus=all --rm -it back-projection:gpu ++process back_projection --help
```
