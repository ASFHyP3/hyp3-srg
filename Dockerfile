FROM condaforge/mambaforge:latest

# For opencontainers label definitions, see:
#    https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title="HyP3 back-projection"
LABEL org.opencontainers.image.description="HyP3 plugin for back-projection processing"
LABEL org.opencontainers.image.vendor="Alaska Satellite Facility"
LABEL org.opencontainers.image.authors="ASF Tools Team <UAF-asf-apd@alaska.edu>"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL org.opencontainers.image.url="https://github.com/ASFHyP3/hyp3-back-projection"
LABEL org.opencontainers.image.source="https://github.com/ASFHyP3/hyp3-back-projection"
LABEL org.opencontainers.image.documentation="https://hyp3-docs.asf.alaska.edu"

# Dynamic lables to define at build time via `docker build --label`
# LABEL org.opencontainers.image.created=""
# LABEL org.opencontainers.image.version=""
# LABEL org.opencontainers.image.revision=""

ARG DEBIAN_FRONTEND=noninteractive

ARG USEGPU="false"
ENV USEGPU=${USEGPU}

ENV PYTHONDONTWRITEBYTECODE=true
ENV PROC_HOME=/home/conda/back-projection
ENV MYHOME=/home/conda

RUN apt-get update && apt-get install -y --no-install-recommends unzip vim curl build-essential gfortran libfftw3-dev nvidia-driver-535 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG CONDA_UID=1000
ARG CONDA_GID=1000
ARG BACK_PROJECTION_TAG=0.2.0
ARG FFTW_TAG=3.3.9

RUN groupadd -g "${CONDA_GID}" --system conda && \
    useradd -l -u "${CONDA_UID}" -g "${CONDA_GID}" --system -d /home/conda -m  -s /bin/bash conda && \
    chown -R conda:conda /opt && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /home/conda/.profile && \
    echo "conda activate base" >> /home/conda/.profile

SHELL ["/bin/bash", "-l", "-c"]

COPY ./scripts/install_cuda.sh ./
RUN chmod +x ./install_cuda.sh
RUN if [[ $USEGPU == "true" ]] ; then ./install_cuda.sh ; else echo "Skipping CUDA install..." ; fi

USER ${CONDA_UID}
WORKDIR /home/conda/

ENV PATH="$PATH:/usr/local/cuda-12.4/bin"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-12.4/lib64"

RUN curl -sL https://github.com/ASFHyP3/back-projection/archive/refs/tags/v${BACK_PROJECTION_TAG}.tar.gz > ./back-projection.tar.gz && \
    mkdir -p ./back-projection && \
    tar -xvf ./back-projection.tar.gz -C ./back-projection/ --strip=1 && \
    rm ./back-projection.tar.gz && \
    rm -rf ./back-projection/fft

COPY --chown=${CONDA_UID}:${CONDA_GID} ./scripts/build_proc.sh ./back-projection
RUN cd /home/conda/back-projection && \
    chmod +x ./build_proc.sh && \
    ./build_proc.sh && \
    find $PROC_HOME -type f -name "*.py" -exec chmod +x {} + && \
    cd /home/conda/

COPY --chown=${CONDA_UID}:${CONDA_GID} . /hyp3-back-projection/

RUN mamba env create -f /hyp3-back-projection/environment.yml && \
    conda clean -afy && \
    conda activate hyp3-back-projection && \
    sed -i 's/conda activate base/conda activate hyp3-back-projection/g' /home/conda/.profile && \
    python -m pip install --no-cache-dir /hyp3-back-projection

ENTRYPOINT ["/hyp3-back-projection/src/hyp3_back_projection/etc/entrypoint.sh"]
CMD ["-h"]
