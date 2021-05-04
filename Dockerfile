FROM senhuang/eplus8.5

WORKDIR /home/developer/fmu

COPY ./eplus /home/developer/fmu/eplus/

COPY ./web.py /home/developer/fmu/web.py

COPY ./testcase.py /home/developer/fmu/testcase.py

COPY ./config /home/developer/fmu/config




