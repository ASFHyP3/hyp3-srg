# HyP3 back-projection

HyP3 plugin for back-projection processing

## Usage
> [!WARNING]
> Running the workflows in this repository requires a compiled version of the [Stanford Radar Group Processor](https://github.com/asfhyp3/back-projection). For this reason, running this repository's workflows in a standard Python is not implemented yet. Instead, we recommend running the workflows from the docker container as outlined below.

The HyP3-back-projection plugin provides a set of workflows (currently only accessible via the docker container) that can be used to process SAR data using the [Stanford Radar Group Processor](https://github.com/asfhyp3/back-projection). The workflows currently included in this plugin are:

`back_projection`: A workflow for creating geocoded Sentinel-1 SLCs from Level-0 data using the [back-projection methodology](https://doi.org/10.1109/LGRS.2017.2753580).

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
