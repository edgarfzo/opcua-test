FROM alpine:edge

WORKDIR /database_docker
COPY . .
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add firefox
RUN /database_docker/add_testing_repo.sh
RUN apk update
RUN apk add geckodriver
RUN python3 -m ensurepip
RUN pip3 install -r requirements.txt
EXPOSE 360
CMD [ "python3", "database_api.py" ]