# HyP3 SRG

HyP3 plugin for Stanford Radar Group (SRG) SAR Processor

## Usage
> [!WARNING]
> Running the workflows in this repository requires a compiled version of the [Stanford Radar Group Processor](https://github.com/asfhyp3/srg). For this reason, running this repository's workflows in a standard Python is not implemented yet. Instead, we recommend running the workflows from the docker container as outlined below.

The HyP3-SRG plugin provides a set of workflows (currently only accessible via the docker container) that can be used to process SAR data using the [Stanford Radar Group Processor](https://github.com/asfhyp3/srg). This set of workflow uses the [SRG alogorithms]((https://doi.org/10.1109/LGRS.2017.2753580)) to process Level-0 Sentinel-1 (S1) data to geocoded, user-friendly products that can be used for time-series analysis. The workflows currently included in this plugin are:

- [`back_projection`](#back-projection): A workflow for creating geocoded Sentinel-1 SLCs,
- [`time_series`](#time-series): A workflow for creating a deformation timeseries of geocoded Sentinel-1 SLCs. 

To run a workflow, you'll first need to build the docker container:
```bash
docker build -t hyp3-srg:latest .
```
Then, run the docker container for your chosen workflow.
```bash
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    hyp3-srg:latest \
    ++process [WORKFLOW_NAME] \
    [WORKFLOW_ARGS]
```

### Back-projection 
The `back_projection` processing type produces geocoded SLCs using Level-0 Sentinel-1 data as input. The workflow takes a list of Level-0 Sentinel-1 granule names and outputs them as geocoded SLCs (GSLCs).
An example command for the `back_projection` workflow is:
```bash
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    hyp3-srg:latest \
    ++process back_projection \
    S1A_IW_RAW__0SDV_20231229T134339_20231229T134411_051870_064437_4F42-RAW \
    S1A_IW_RAW__0SDV_20231229T134404_20231229T134436_051870_064437_5F38-RAW
```

### Time-series
The `time_series` workflow takes a list of up to 50 Sentinel-1 GSLC granule names, along with a bounding box, and produces a time-series. **Note that all of the input GSLSs must have been generated with the provided bounding box.**  Stacks are created with `10` range looks, `10` azimuth looks,  and temporal and spatial baselines of `1000` and `1000`, respectively. Candidate reference points are chosen with a correlation threshold of `0.5` - meaning the correlation must be above `0.5` in all scenes at that point. A tropospheric correction is applied using an elevation-dependent regression.
 The following command will run the `time_series` workflow: 
```
docker run -it --rm \
    -e EARTHDATA_USERNAME=[YOUR_USERNAME_HERE] \
    -e EARTHDATA_PASSWORD=[YOUR_PASSWORD_HERE] \
    hyp3-srg:latest \
    ++process time_series \
   S1A_IW_RAW__0SDV_20240828T020812_20240828T020844_055407_06C206_6EA7 \
   S1A_IW_RAW__0SDV_20240816T020812_20240816T020844_055232_06BB8A_C7CA \
   S1A_IW_RAW__0SDV_20240804T020812_20240804T020844_055057_06B527_1346
```
### Earthdata Login

For all workflows, the user must provide their Earthdata Login credentials in order to download input data.

If you do not already have an Earthdata account, you can sign up [here](https://urs.earthdata.nasa.gov/home).

Your credentials can be passed to the workflows via environment variables (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`) or via your `.netrc` file.

If you haven't set up a `.netrc` file
before, check out this [guide](https://harmony.earthdata.nasa.gov/docs#getting-started) to get started.


## Developer setup
### GPU Setup
In order for Docker to be able to use the host's GPU, the host must have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html) installed and configured. 
The process is different for different OS's and Linux distros. The setup process for the most common distros, including Ubuntu, 
can be found [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration). Make sure to follow the [Docker configuration steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) after installing the package.

The AWS ECS-optimized GPU AMI has the configuration described already set up. You can find the latest version of this AMI by calling:
```bash
aws ssm get-parameters --names /aws/service/ecs/optimized-ami/amazon-linux-2/gpu/recommended --region us-west-2
```

### GPU Docker Container
Once you have a compute environment set up as described above, you can build the GPU version of the container by running:
```bash
docker build --build-arg="GPU_ARCH={YOUR_ARCH}" -t ghcr.io/asfhyp3/hyp3-srg:{RELEASE}.gpu -f Dockerfile.gpu .
```

You can get the value of `COMPUTE_CAPABILITY_VERSION` by running `nvidia-smi` on the instance to obtain GPU type, then cross-reference this information with NVIDIA's [GPU type compute capability list](https://developer.nvidia.com/cuda-gpus). For a g6.2xlarge instance, this would be:
```bash
docker --build-arg="GPU_ARCH=89" -t ghcr.io/asfhyp3/hyp3-srg:{RELEASE}.gpu -f Dockerfile.gpu .
```
The compute capability version will always be the same for a given instance type, so you will only need to look this up once per instance type.
The default value for this argument is `89` - the correct value for g6.2xlarge instances.
**THE COMPUTE CAPABILITY VERSION MUST MATCH ON BOTH THE BUILDING AND RUNNING MACHINE!**

The value of `RELEASE` can be obtained from the git tags.

You can push a manual container to HyP3-SRG's container repository by following [this guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#pushing-container-images).

### EC2 Setup
> [!CAUTION]
> Running the docker container on an Amazon Linux 2023 Deep Learning AMI runs, but will result in all zero outputs. Work is ongoing to determine what is causing this issue. For now, we recommend using option 2.3.

When running on an EC2 instance, the following setup is recommended:
1. Create a [G6-family EC2 instance](https://aws.amazon.com/ec2/instance-types/g6/) that has **at least 32 GB of memory**.
2. Launch your instance with one of the following setups (**option i is recommended**):
    1. Use the latest [Amazon Linux 2023 AMI](https://docs.aws.amazon.com/linux/al2023/ug/ec2.html) with `scripts/amazon_linux_setup.sh` as the [user script on launch](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).
    2. Use the latest [Ubuntu AMI](https://cloud-images.ubuntu.com/locator/ec2/) with the `scripts/ubuntu_setup.sh` as the [user script on launch](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).
    3. Use the latest AWS ECS-optimized GPU AMI (`aws ssm get-parameters --names /aws/service/ecs/optimized-ami/amazon-linux-2/gpu/recommended --region us-west-2`)
3. Build the GPU docker container with the correct compute capability version (see section above). To determine this value, run `nvidia-smi` on the instance to obtain GPU type, then cross-referencke this information with NVIDIA's [GPU type compute capability list](https://developer.nvidia.com/cuda-gpus). For a g6.2xlarge instance, this would be:
```bash
docker --build-arg="GPU_ARCH=89" -t ghcr.io/asfhyp3/hyp3-srg:{RELEASE}.gpu -f Dockerfile.gpu .
```
