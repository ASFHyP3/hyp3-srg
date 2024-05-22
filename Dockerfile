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

ARG DEBIAN_FRONTEND=noninteractive
ARG CONDA_UID=1000
ARG CONDA_GID=1000

ENV USEGPU=false
ENV FFTW_LIB=/usr/lib/x86_64-linux-gnu/libfftw3f.a
ENV PROC_HOME=/back-projection
ENV PYTHONDONTWRITEBYTECODE=true
ENV MYHOME=/home/conda

RUN apt-get update && apt-get install -y --no-install-recommends unzip git vim curl build-essential gfortran libfftw3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g "${CONDA_GID}" --system conda && \
    useradd -l -u "${CONDA_UID}" -g "${CONDA_GID}" --system -d /home/conda -m  -s /bin/bash conda && \
    chown -R conda:conda /opt && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /home/conda/.profile && \
    echo "conda activate base" >> /home/conda/.profile

SHELL ["/bin/bash", "-l", "-c"]

USER ${CONDA_UID}
WORKDIR /home/conda/

# TODO: change back to main when problem is fixed
RUN git clone -b fix_path https://github.com/ASFHyP3/back-projection.git /back-projection
COPY --chown=${CONDA_UID}:${CONDA_GID} ./scripts/build_proc.sh /back-projection
RUN cd /back-projection && ./build_proc.sh && cd /home/conda/

COPY --chown=${CONDA_UID}:${CONDA_GID} . /hyp3-back-projection/

RUN mamba env create -f /hyp3-back-projection/environment.yml && \
    conda clean -afy && \
    conda activate hyp3-back-projection && \
    sed -i 's/conda activate base/conda activate hyp3-back-projection/g' /home/conda/.profile && \
    python -m pip install --no-cache-dir /hyp3-back-projection

ENTRYPOINT ["/hyp3-back-projection/src/hyp3_back_projection/etc/entrypoint.sh"]
CMD ["-h"]
