import sys
import logging
import json
import awsiot.greengrasscoreipc
import time
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
)
import boto3 

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()

def greengrass_mean():
    i = 1
    s3 = boto3.client('s3')
    while True:
        id = str(i)
        #following line just for testing 
        request = PublishToIoTCoreRequest()
        request.topic_name = "cloud-gg-topic"
        msg = str(i) + " number Hello from avgz while true loopMQTT prototype in greengrass"
        message_dict = {"message" : msg }
        request.payload = bytes(json.dumps(message_dict), "utf-8")
        request.qos = QOS.AT_LEAST_ONCE
        
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        future = operation.get_response()
        future.result(TIMEOUT)
        json_object = {"id": "json-to-s3 with id " + id}
        s3.put_object(
        Body=json.dumps(json_object),
        Bucket='avgz-iotbox-trials',
        Key='basic/file' + id +".json"
        )
        i = i + 1
        id = str(i)
        time.sleep(5)


# Execute the function above
greengrass_mean()

def lambda_handler(event, context):
  logger.info("avgz mqtt pub is ONLINE")
  logger.info(json.dumps(event))
    
  # Let's publish a response back to AWS IoT
  request = PublishToIoTCoreRequest()
  request.topic_name = "cloud-gg-topic"
  message_dict = {"message" : "Hello from avgz MQTT prototype in greengrass"}
  request.payload = bytes(json.dumps(message_dict), "utf-8")
  request.qos = QOS.AT_LEAST_ONCE
  
  operation = ipc_client.new_publish_to_iot_core()
  operation.activate(request)
  
  future = operation.get_response()
  future.result(TIMEOUT)

  return True