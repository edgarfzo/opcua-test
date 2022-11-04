import asyncio
import logging
from iodd import IODD
from information_node import InformationNode
from asyncua import Client, ua

_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://192.168.1.250:4840/'
    print(url)
    async with Client(url=url) as client:
        # _logger.info("Root node is: %r", client.nodes.root)
        # _logger.info("Objects node is: %r", client.nodes.objects)

        # # Node objects have methods to read and write node attributes as well as browse or populate address space
        # _logger.info("Children of root are: %r", await client.nodes.root.get_children())

        # # setup our own namespace, not really necessary but should as spec
        # uri = 'http://nne_mi'
        # idx = await client.get_namespace_index(uri)
        # _logger.info("index of our namespace is %s", idx)
        # # get a specific node knowing its node id
        while client:
            with open('ifm-000404-20200110-IODD1.1.xml', 'r') as f:
                data = f.read()
            info_node = InformationNode("test",144,16,1)
            iodd_test = IODD(data,[''],[info_node],1)
            iodd_test._parse_information_nodes()
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
                    
            object_2_children = await object_2_node.get_children()
            
            # for i, node in enumerate(object_2_children):
            #     if i == 0:
            #         object_3_node = node
            # bname = object_3_node.nodeid
            vibration_node = client.get_node("ns=1;s=IOLM/Port 3/Attached Device/PDI Data Byte Array")
            value = await vibration_node.read_value()
            
            #print(type(value))
            result = info_node.byte_to_real_value(value)
            print("result ", result)
            print("- units: ['m/s', 'mm/s', 'in/s', 'm/s', 'mm/s', 'in/s']")
            for i in range (3): 
                print('')
            await asyncio.sleep(1)

       
        
       


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())