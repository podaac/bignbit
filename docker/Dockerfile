# Define global args
ARG FUNCTION_DIR="/home/dockeruser/app"
ARG GDAL_VERSION="3.6.3"

FROM osgeo/gdal:ubuntu-small-${GDAL_VERSION} as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  python3-pip \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

RUN adduser --quiet --disabled-password --shell /bin/sh --home /home/dockeruser --gecos "" --uid 993 dockeruser
USER dockeruser
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /home/dockeruser
COPY ./bignbit ./bignbit

COPY --chown=dockeruser poetry.lock pyproject.toml README.md ./
RUN /home/dockeruser/.local/bin/poetry lock --no-update
RUN mkdir -p "${FUNCTION_DIR}" && \
    /home/dockeruser/.local/bin/poetry install --only main --sync && \
    cp -r $(/home/dockeruser/.local/bin/poetry env list --full-path | awk '{print $1}')/lib/python*/site-packages/* ${FUNCTION_DIR} && \
    cp -r ./bignbit ${FUNCTION_DIR} && \
    touch ${FUNCTION_DIR}/bignbit/__init__.py && \
    pip install --target ${FUNCTION_DIR} awslambdaric


FROM osgeo/gdal:ubuntu-small-${GDAL_VERSION}
ARG FUNCTION_DIR
RUN adduser --quiet --disabled-password --shell /bin/sh --home /home/dockeruser --gecos "" --uid 993 dockeruser
USER dockeruser
ENV HOME /home/dockeruser
WORKDIR ${FUNCTION_DIR}

COPY --chown=dockeruser --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD --chown=dockeruser https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /home/dockeruser/.local/bin/aws-lambda-rie
COPY --chown=dockeruser docker/docker-entrypoint.sh /home/dockeruser/.local/bin/
RUN chmod 755 /home/dockeruser/.local/bin/aws-lambda-rie /home/dockeruser/.local/bin/docker-entrypoint.sh && \
    touch bignbit/__init__.py
ENTRYPOINT [ "/home/dockeruser/.local/bin/docker-entrypoint.sh" ]
CMD [ "bignbit.apply_opera_hls_treatment.lambda_handler" ]