FROM google/cloud-sdk:latest

WORKDIR /app

COPY requirements.txt .

# passing the key json as argument with single quotes and replaced \n with \\n
# single quotes to interpret double qoutes
# \\n to interpret \n as \n not newline
ARG GOOGLE_APPLICATION_CREDENTIALS='picked from github secrets'


# convert arg variable into a json file required for gcp auth
RUN echo -n ${GOOGLE_APPLICATION_CREDENTIALS} > key.json

RUN gcloud auth activate-service-account viz-platform-data@crucial-oven-386720.iam.gserviceaccount.com --key-file=key.json --project=crucial-oven-386720

# downloading solved pypsa earth data
RUN command gsutil cp -r  gs://viz-platform-data/pypsa-earth .

# copying our app into the container
COPY . /app/pypsa-earth-lit/

# overwriting default config with the config attched to solved pypsa earth data
RUN command gsutil cp -r  gs://viz-platform-data/pypsa-earth-lit-config/config.yaml /app/pypsa-earth-lit/app/pages/utils/config.yaml

# Install necessary system packages
RUN apt-get update && apt-get install -y wget bzip2

# Download and install MambaForge (a faster variant of Conda)
RUN wget -qO /tmp/mambaforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
    && bash /tmp/mambaforge.sh -b -p /opt/conda \
    && rm /tmp/mambaforge.sh

ENV PATH /opt/conda/bin:$PATH

RUN pip install --no-cache-dir -r requirements.txt

RUN mamba install -c conda-forge cartopy

EXPOSE 8501

ENV PORT 8501

COPY commands.sh /scripts/commands.sh
RUN ["chmod", "+x", "/scripts/commands.sh"]
ENTRYPOINT ["/scripts/commands.sh"]
