FROM python:3.12-bookworm

COPY entrypoint.py /entrypoint.py
COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ENTRYPOINT [ "/entrypoint.py" ]
