import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod

from opcua_server.opcua_methods import (
    add_folder_,
    add_object_,
    add_variable_,
    delete_node_,
    write_value_to_node_,
)
from opcua.iolink.settings import INTERNAL_OPCUA_ADDRESS, INTERNAL_OPCUA_PORT

server = None


@uamethod
async def add_folder(
    parent: ua.NodeId, parent_nodeid: str, nodeid: str, bname: str, descr: str
) -> None:
    """Alias for function to improve readability and to avoid circular imports.

    For full documentation on this function check opcua_methods.add_folder_()
    """
    global server
    return await add_folder_(
        server=server,
        parent_nodeid=parent_nodeid,
        nodeid=nodeid,
        bname=bname,
        descr=descr,
    )


@uamethod
async def add_object(
    parent: ua.NodeId, parent_nodeid: str, nodeid: str, bname: str, descr: str
) -> None:
    """Alias for function to improve readability and to avoid circular imports.

    For full documentation on this function check opcua_methods.add_object_()
    """
    global server
    return await add_object_(
        server=server,
        parent_nodeid=parent_nodeid,
        nodeid=nodeid,
        bname=bname,
        descr=descr,
    )


@uamethod
async def add_variable(
    parent: ua.NodeId, parent_nodeid: str, nodeid: str, bname: str, descr: str, val: str
) -> None:
    """Alias for function to improve readability and to avoid circular imports.

    For full documentation on this function check opcua_methods.add_variable_()
    """
    global server
    return await add_variable_(
        server=server,
        parent_nodeid=parent_nodeid,
        nodeid=nodeid,
        bname=bname,
        descr=descr,
        val=val,
    )


@uamethod
async def delete_node(parent: ua.NodeId, nodeid: str) -> None:
    """Alias for function to improve readability and to avoid circular imports.

    For full documentation on this function check opcua_methods.delete_node_()
    """
    global server
    return await delete_node_(server=server, nodeid=nodeid)


@uamethod
async def write_value_to_node(parent: ua.NodeId, nodeid: str, val) -> None:
    """Alias for function to improve readability and to avoid circular imports.

    For full documentation on this function check opcua_methods.write_value_to_node_()
    """
    global server
    return await write_value_to_node_(server=server, nodeid=nodeid, val=val)


async def main(
    nsidx: int,
    num_connections: int = 16,
    host: str = INTERNAL_OPCUA_ADDRESS,
    port: str = INTERNAL_OPCUA_PORT,
) -> None:
    """Set up an OPC-UA server with preconfigured nodes."""
    global server
    _logger = logging.getLogger("NNE-OPC-UA-Server")

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://{host}:{port}/nne/server/")
    server.set_server_name("NNE Unibio OPC-UA Server")

    # setup our own namespace, not really necessary but should as spec
    # Left in for now until we figure out if this is actually necessary
    # uri = "http://examples.freeopcua.github.io"
    # idx = await server.register_namespace(uri)
    idx = 6
    devices = await server.nodes.objects.add_object(idx, "Devices")
    functions = await server.nodes.objects.add_object(idx, "Functions")

    for i in range(1, num_connections + 1):
        # Adding Port object, which will host the name of the sensor connected to the
        # port as well as all its information points
        port = await devices.add_object(
            f"ns={nsidx};i=1{i:0>2}000", bname=f"{nsidx}:Port{i:0>2}"
        )
        await port.add_variable(
            f"ns={nsidx};i=1{i:0>2}100", bname=f"{nsidx}:SensorName", val=f"Sensor{i:0>2}"
        )  # Sensor name
        await port.add_object(
            f"ns={nsidx};i=1{i:0>2}200", bname=f"{nsidx}:InformationNodes"
        )  # Information points
        _logger.debug(f"Added node tree Port{i:0>2} with all child nodes")

    _logger.debug("Registering add_folder method")
    await functions.add_method(
        f"ns={nsidx};i=90001",
        f"{nsidx}:add_folder",
        add_folder,
        [
            ua.Argument(
                Name="parent_id",
                Description=ua.LocalizedText("Parent NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("New Node ID", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="browse_name",
                Description=ua.LocalizedText("Browse Name", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="description",
                Description=ua.LocalizedText("Description", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
        ],
        [],
    )

    _logger.debug("Registering add_object method")
    await functions.add_method(
        f"ns={nsidx};i=90002",
        f"{nsidx}:add_object",
        add_object,
        [
            ua.Argument(
                Name="parent_id",
                Description=ua.LocalizedText("Parent NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("New Node ID", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="browse_name",
                Description=ua.LocalizedText("Browse Name", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="description",
                Description=ua.LocalizedText("Description", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
        ],
        [],
    )

    _logger.debug("Registering delete_node method")
    await functions.add_method(
        f"ns={nsidx};i=90003",
        f"{nsidx}:delete_node",
        delete_node,
        [
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            )
        ],
        [],
    )

    _logger.debug("Registering add_float method")
    await functions.add_method(
        f"ns={nsidx};i=90101",
        f"{nsidx}:add_float",
        add_variable,
        [
            ua.Argument(
                Name="parent_id",
                Description=ua.LocalizedText("Parent NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("New Node ID", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="browse_name",
                Description=ua.LocalizedText("Browse Name", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="description",
                Description=ua.LocalizedText("Description", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="default_value",
                Description=ua.LocalizedText("Default float value", "en"),
                DataType=ua.NodeId(ua.ObjectIds.Float),
            ),
        ],
        [],
    )

    _logger.debug("Registering add_int method")
    await functions.add_method(
        f"ns={nsidx};i=90102",
        f"{nsidx}:add_int",
        add_variable,
        [
            ua.Argument(
                Name="parent_id",
                Description=ua.LocalizedText("Parent NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("New Node ID", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="browse_name",
                Description=ua.LocalizedText("Browse Name", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="description",
                Description=ua.LocalizedText("Description", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="default_value",
                Description=ua.LocalizedText("Default int value", "en"),
                DataType=ua.NodeId(ua.ObjectIds.Int64),
            ),
        ],
        [],
    )

    _logger.debug("Registering add_string method")
    await functions.add_method(
        f"ns={nsidx};i=90103",
        f"{nsidx}:add_string",
        add_variable,
        [
            ua.Argument(
                Name="parent_id",
                Description=ua.LocalizedText("Parent NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="node_id",
                Description=ua.LocalizedText("New Node ID", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="browse_name",
                Description=ua.LocalizedText("Browse Name", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="description",
                Description=ua.LocalizedText("Description", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="default_value",
                Description=ua.LocalizedText("Default string value", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
        ],
        [],
    )
    _logger.debug("Registering add_string method")
    await functions.add_method(
        f"ns={nsidx};i=90200",
        f"{nsidx}:write_value",
        write_value_to_node,
        [
            ua.Argument(
                Name="nodeid",
                Description=ua.LocalizedText("NodeId", "en"),
                DataType=ua.NodeId(ua.ObjectIds.String),
            ),
            ua.Argument(
                Name="new_value",
                Description=ua.LocalizedText("new value", "en"),
                DataType=ua.NodeId(ua.ObjectIds.Float),
            ),
        ],
        [],
    )

    _logger.info("Starting server!")
    return server


async def run_server(server: Server) -> None:
    """Run the OPC UA server.

    :param server: Server object with completed setup
    """
    async with server:
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    server = asyncio.run(main(nsidx=6, host="0.0.0.0", port="4840"), debug=True)
    asyncio.run(run_server(server))