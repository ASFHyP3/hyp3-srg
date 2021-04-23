FROM ubuntu:latest

# For opencontainers label definitions, see:
#    https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title="Back_projection"
LABEL org.opencontainers.image.description="This is a process to process L0 Raw Products using a back projection algorithm"
LABEL org.opencontainers.image.vendor="Alaska Satellite Facility"
LABEL org.opencontainers.image.authors="ASF APD/Tools Team <uaf-asf-apd@alaska.edu>"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL org.opencontainers.image.url="https://github.com/ASFHyP3/hyp3-back-projection"
LABEL org.opencontainers.image.source="https://github.com/ASFHyP3/hyp3-back-projection"
# LABEL org.opencontainers.image.documentation=""

# Dynamic lables to define at build time via `docker build --label`
# LABEL org.opencontainers.image.created=""
# LABEL org.opencontainers.image.version=""
# LABEL org.opencontainers.image.revision=""

RUN apt-get update && apt-get install -y --no-install-recommends wget gcc gfortran make unzip vim gdal-bin python3-pip libfftw3-dev libfftw3-doc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash user

USER user
SHELL ["/bin/bash", "-l", "-c"]
ENV PYTHONDONTWRITEBYTECODE=true
WORKDIR /home/user

COPY dist/*  /home/user/

RUN python3 -m pip install /home/user/back_projection-0.0.0.tar.gz && \
    tar -xvf back_projection-0.0.0.tar.gz && \
    cd back_projection-0.0.0/back_projection/src && \
    chmod +x * && \
    chmod +x */* && \
    source build_proc && \
    mkdir "/home/user/back_projection-0.0.0/back_projection/src/output"

ENV PROC_HOME="/home/user/back_projection-0.0.0/back_projection/src"

ENTRYPOINT ["python3", "/home/user/back_projection-0.0.0/back_projection/__main__.py"]
CMD ["-h"]
