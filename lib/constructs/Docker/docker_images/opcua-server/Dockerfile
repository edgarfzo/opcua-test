FROM alpine:edge

WORKDIR /server
COPY opcua_server opcua_server/
COPY ["nnemi_opcua_server.py", "requirements_opcua_server.txt", "./"]
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install -r requirements_opcua_server.txt
EXPOSE 4840