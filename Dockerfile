FROM senhuang/pyfmi

MAINTAINER Sen

# Installing EnergyPlus 8.5
ENV ENERGYPLUS_VERSION 8.5.0
ENV ENERGYPLUS_TAG v8.5.0
ENV ENERGYPLUS_SHA c87e61b44b
ENV ENERGYPLUS_INSTALL_VERSION 8-5-0
ENV ENERGYPLUS_DOWNLOAD_BASE_URL https://github.com/NREL/EnergyPlus/releases/download/$ENERGYPLUS_TAG
ENV ENERGYPLUS_DOWNLOAD_FILENAME EnergyPlus-$ENERGYPLUS_VERSION-$ENERGYPLUS_SHA-Linux-x86_64.sh
ENV ENERGYPLUS_DOWNLOAD_URL $ENERGYPLUS_DOWNLOAD_BASE_URL/$ENERGYPLUS_DOWNLOAD_FILENAME

RUN apt-get update && apt-get install -y ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -SLO $ENERGYPLUS_DOWNLOAD_URL \
    && chmod +x $ENERGYPLUS_DOWNLOAD_FILENAME \
    && echo "y\r" | ./$ENERGYPLUS_DOWNLOAD_FILENAME \
    && rm $ENERGYPLUS_DOWNLOAD_FILENAME \
    && cd /usr/local/EnergyPlus-$ENERGYPLUS_INSTALL_VERSION \
    && rm -rf DataSets Documentation ExampleFiles WeatherData MacroDataSets PostProcess/convertESOMTRpgm \
    PostProcess/EP-Compare PreProcess/FMUParser PreProcess/ParametricPreProcessor PreProcess/IDFVersionUpdater

# Remove the broken symlinks
RUN cd /usr/local/bin \
    && find -L . -type l -delete

RUN ["ln", "-s", "/usr/local/EnergyPlus-8-5-0/Energy+.idd", "/usr/local/Energy+.idd"]

RUN pip install --user flask-restful pandas requests

RUN mkdir /home/developer

RUN mkdir /home/developer/fmu

WORKDIR /home/developer/fmu

COPY ./eplus /home/developer/fmu/eplus/

COPY ./web.py /home/developer/fmu/web.py

COPY ./testcase.py /home/developer/fmu/testcase.py

COPY ./config /home/developer/fmu/config


