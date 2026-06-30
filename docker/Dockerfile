# Define global args
ARG FUNCTION_DIR="/home/dockeruser/app"
# GDAL 3.13.x base images moved to Ubuntu 26.04 / Python 3.14. Pin to 3.12.4, the newest
# osgeo/gdal release whose base (Ubuntu 24.04 LTS) still ships Python 3.12, to keep the
# Lambda runtime on the same Python version used in dev/CI. The PyPI gdal binding version
# installed via the "gdal" extra in pyproject.toml must match this base image's libgdal.
ARG GDAL_VERSION="3.12.4"

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION} AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install aws-lambda-cpp build dependencies.
# The newer minimal Ubuntu base behind osgeo/gdal:ubuntu-small no longer ships curl,
# pip/venv, or the Python dev headers, so install them explicitly:
#   curl         -> fetch the Poetry installer
#   python3-venv -> provides ensurepip so the Poetry installer can build its venv
#   python3-dev  -> Python.h, required to compile the GDAL bindings from the PyPI sdist
RUN apt-get update && \
  apt-get install -y \
  curl \
  python3-pip \
  python3-dev \
  python3-venv \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

RUN useradd --create-home --home-dir /home/dockeruser --shell /bin/sh --uid 993 --user-group --comment "" dockeruser
USER dockeruser
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /home/dockeruser
COPY ./bignbit ./bignbit

COPY --chown=dockeruser poetry.lock pyproject.toml README.md ./
RUN /home/dockeruser/.local/bin/poetry lock
RUN mkdir -p "${FUNCTION_DIR}" && \
    /home/dockeruser/.local/bin/poetry install --only main --extras gdal --sync && \
    cp -r $(/home/dockeruser/.local/bin/poetry env list --full-path | awk '{print $1}')/lib/python*/site-packages/* ${FUNCTION_DIR} && \
    cp -r ./bignbit ${FUNCTION_DIR} && \
    touch ${FUNCTION_DIR}/bignbit/__init__.py && \
    pip install --target ${FUNCTION_DIR} awslambdaric


FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION}
ARG FUNCTION_DIR
RUN useradd --create-home --home-dir /home/dockeruser --shell /bin/sh --uid 993 --user-group --comment "" dockeruser
USER dockeruser
ENV HOME=/home/dockeruser
WORKDIR ${FUNCTION_DIR}

COPY --chown=dockeruser --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD --chown=dockeruser https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /home/dockeruser/.local/bin/aws-lambda-rie
COPY --chown=dockeruser docker/docker-entrypoint.sh /home/dockeruser/.local/bin/
RUN chmod 755 /home/dockeruser/.local/bin/aws-lambda-rie /home/dockeruser/.local/bin/docker-entrypoint.sh && \
    touch bignbit/__init__.py
ENTRYPOINT [ "/home/dockeruser/.local/bin/docker-entrypoint.sh" ]
CMD [ "bignbit.apply_opera_hls_treatment.lambda_handler" ]