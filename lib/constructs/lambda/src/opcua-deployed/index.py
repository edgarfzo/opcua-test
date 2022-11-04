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

from asyncua import Client


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

EXTERNAL_OPCUA_ADDRESS = "192.168.1.250"
EXTERNAL_OPCUA_PORT = "4840"
TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()


async def main_runtime():
    i = 0
    url = 'opc.tcp://192.168.1.250:4840/'
    print(url)
    async with Client(url=url) as client:

            for i in range (3): 
                print('')
            root = client.get_node(client.nodes.root)
            # bname = await root.read_browse_name()
            # print(bname)
            # bname2 = await root.read_display_name()
            # print(bname2)
            # bname3 = await root.read_description()
            # print(bname3)
            nodes_children = await root.get_children()
            #print(nodes_children)
            for i, node in enumerate(nodes_children):
                bname = await node.read_browse_name()
                dname = await node.read_display_name()
                dename = await node.read_description()
                if i == 0:
                    object_node = node
            
            object_children = await object_node.get_children()
            #print(object_children)
            for i, node in enumerate(object_children):
                if i == 1:
                    object_2_node = node
                    print(node)
            object_2_children = await object_2_node.get_children()
            print(object_2_children)
            # for i, node in enumerate(object_2_children):
            #     if i == 0:
            #         object_3_node = node
            # bname = object_3_node.nodeid
            vibration_node = client.get_node("ns=1;s=IOLM/Port 3/Attached Device/PDI Data Byte Array")
            value = await vibration_node.read_value()
            print(value)
            for i in range (3): 
                print('')
            await asyncio.sleep(1)


main_runtime()

def handler(event, context):
  return True