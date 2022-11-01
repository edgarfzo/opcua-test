import asyncio
import inspect
import logging
import time
import json
import sys
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
)

import asyncua


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

EXTERNAL_OPCUA_ADDRESS = "192.168.10.100"
EXTERNAL_OPCUA_PORT = "4840"
TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()


def main_runtime():
    i = 0
    while True:
        #following line just for testing
        # # read from OPCUA FIRST STEP finding the nodes they are constant for the same iolink master MVP:find them and hardcode them
        
        # Translate to data using the iodd file always publicly available, select and download manually
        # we need to assure that no matter where they put the sensor( ports 1-8), we tranalste correctly
        # Publish first to iotcore, future local for second lambda
        request = PublishToIoTCoreRequest()
        request.topic_name = "cloud-gg-topic-0"
        msg = str(i) + " number Hello from opcua-trial from pipeline"
        message_dict = {"message" : msg }
        request.payload = bytes(json.dumps(message_dict), "utf-8")
        request.qos = QOS.AT_LEAST_ONCE
        
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        future = operation.get_response()
        future.result(TIMEOUT)
        i = i + 1
        time.sleep(5)


main_runtime()

def handler(event, context):
  return True