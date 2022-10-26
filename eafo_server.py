import logging
import asyncio
import sys
sys.path.insert(0, "..")

from asyncua import ua, Server
from asyncua.common.methods import uamethod



@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger('EAFO')
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/nne_local/server/')

    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, 'MyObject')
    myvar = await myobj.add_variable(idx, 'Temperature', 6.7)
    myvar2 = await myobj.add_variable(idx, 'Pressure', 100)
    # Set MyVariable to be writable by clients
    await myvar.set_writable()
    await myvar2.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 1256), ua.QualifiedName('ServerMethod', 19), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    _logger.info('Starting server!')
    async with server:
        while True:
            await asyncio.sleep(5)
            new_val = await myvar.get_value() + 0.1
            new_val2 = await myvar2.get_value() + 1
            _logger.info('Set value of %s to %.1f', myvar, new_val)
            _logger.info('Set value of %s to %.1f', myvar2, new_val2)
   
            await myvar.write_value(new_val)
            await myvar2.write_value(new_val2)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main(), debug=True)