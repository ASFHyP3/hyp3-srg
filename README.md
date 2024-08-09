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
    back-projection:latest \
    ++process [WORKFLOW_NAME] \
    [WORKFLOW_ARGS]
```
Here is an example command for the `back_projection` workflow:
```bash
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    back-projection:latest \
    ++process back_projection \
    S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42-RAW \
    S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38-RAW
```

## Earthdata Login and ESA Credentials

For all workflows, the user must provide their Earthdata Login credentials and ESA Copernicus Data Space Ecosystem (CDSE) credentials in order to download input data.

If you do not already have an Earthdata account, you can sign up [here](https://urs.earthdata.nasa.gov/home).

If you do not already have a CDSE account, you can sign up [here](https://dataspace.copernicus.eu).

(`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`), or via your `.netrc` file.

If you haven't set up a `.netrc` file
before, check out this [guide](https://harmony.earthdata.nasa.gov/docs#getting-started) to get started.

## GPU Setup:
In order for Docker to be able to use the host's GPU, the host must have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) installed and configured. 
The process is different for different OS's and Linux distros. The setup process for the most common distros, including Ubuntu, 
can be found [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration). Make sure to follow the [Docker configuration steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) after installing the package.

### EC2 Setup
> [!CAUTION]
> Running the docker container on an Amazon Linux 2023 Deep Learning AMI runs, but will result in all zero outputs. Work is ongoing to determine what is causing this issue. For now, we recommend using option 2.i.

When running on an EC2 instance, the following setup is recommended:
1. Create a [G6-family EC2 instance](https://aws.amazon.com/ec2/instance-types/g6/) that has **at least 32 GB of memory**.
2. Launch your instance with one of the following setups (**option i is recommended**):
    1. Use the latest [Amazon Linux 2023 AMI](https://docs.aws.amazon.com/linux/al2023/ug/ec2.html) with `scripts/amazon_linux_setup.sh` as the [user script on launch](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).
    2. Use the latest [Ubuntu AMI](https://cloud-images.ubuntu.com/locator/ec2/) with the `scripts/ubuntu_setup.sh` as the [user script on launch](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).
    3. Use the [Ubuntu Deep Learning Base OSS Nvidia Driver GPU AMI](https://aws.amazon.com/releasenotes/aws-deep-learning-base-gpu-ami-ubuntu-22-04/) (no install script required).
3. Build the GPU docker container with the correct compute capability version. To determine this value, run `nvidia-smi` on the instance to obtain GPU type, then cross-reference this information with NVIDIA's [GPU type compute capability list](https://developer.nvidia.com/cuda-gpus). For a g6.2xlarge instance, this would be:
```bash
docker --build-arg="GPU_ARCH=89" -t back-projection:gpu-89 -f Dockerfile.gpu .
```
The compute capability version will always be the same for a given instance type, so you will only need to look this up once per instance type.
The default value for this argument is `89` - the correct value for g6.2xlarge instances.
