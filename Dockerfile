FROM python:3.9-slim

COPY . /build
WORKDIR /build

RUN pip install poetry

RUN poetry build -f wheel

FROM python:3.9-slim

COPY --from=0 /build/dist /dist
COPY docker_entrypoint.sh /usr/local/bin/entrypoint.sh
COPY template_hqbot.json /etc/hqbot/hqbot.json

RUN apt-get update; \
    apt-get install -y ffmpeg libffi-dev libnacl-dev python3-dev; \
    apt-get install -y gosu; \
    rm -rf /var/lib/apt/lists/*

RUN pip install dist/*.whl

ENTRYPOINT ["/usr/local/bin/entrypoint.sh", "hqbot"]

