import asyncio
import logging

from asyncua import Client, ua

_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://localhost:4840/nne_local/server/'
    url2 = "opc.tcp://localhost:4841/freeopcua/server/"
    print(url)
    async with Client(url=url) as client:
        while client:
            _logger.info("Node is: %r", client.nodes)
            _logger.info("Root node is: %r", client.nodes.root)
            _logger.info("Objects node is: %r", client.nodes.objects)
            
            
            # # Node objects have methods to read and write node attributes as well as browse or populate address space
            _logger.info("Children of root are: %r", await client.nodes.root.get_children())

            # # setup our own namespace, not really necessary but should as spec
            # uri = 'http://nne_mi'
            # idx = await client.get_namespace_index(uri)
            # _logger.info("index of our namespace is %s", idx)
            # # get a specific node knowing its node id

    
            root = client.get_node(client.nodes.root)
            _logger.info("2nd Root node is: %r", root)
            bname = await root.read_browse_name()
            print(bname)
            # bname2 = await root.read_display_name()
            # print(bname2)
            # bname3 = await root.read_description()
            # print(bname3)
            nodes_children = await root.get_children()
            _logger.info("2nd Children of root are: %r", nodes_children)
            for i, node in enumerate(nodes_children):
                bname = await node.read_browse_name()
                dname = await node.read_display_name()
                dename = await node.read_description()
                if i == 0:
                    object_node = node
            print(bname)
            object_children = await object_node.get_children()
            print("Object children", object_children)
            for i, node in enumerate(object_children):
                if i == 2:
                    object_2_node = node
            object_2_children = await object_2_node.get_children()
            print(object_2_children)
            for i, node in enumerate(object_2_children):
                if i == 0:
                    object_3_node = node
            bname = await object_3_node.read_
            value = await object_3_node.read_value()
            print(value,bname)
            for i in range (3): 
                print('')
            await asyncio.sleep(5)

       
        
       


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())