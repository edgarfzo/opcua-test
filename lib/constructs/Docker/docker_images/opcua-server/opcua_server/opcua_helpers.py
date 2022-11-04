"""Functions to aid the creation and maintenance of the NNE MI OPC UA server.

Methods
-------
check_for_existing_children
    Checks if the given node has any child nodes and gets rid of them if they exist.
create_information_node
    Handles the creation of an information node in the NNE MI OPC UA server with it's
    child nodes and initial values.
find_connected_sensors
    Queries the IO-Link masters OPC UA server to see which ports have what sensor (if
    any) connected to them.
handle_connect
    Handles a new connection of a sensor to the IoT Box. Manages the creation of the
    correct information nodes.
handle_disconnect
    Handles the disconnecting of a sensor to the IoT Box. Manages the deletion of the
    correct information nodes.
handle_writing
    Queries the IO-Link master OPC UA server for updated values and writes them to the
    correct value nodes in the NNE MI OPC UA server.
"""
import logging

from asyncua import Client, Node
from asyncua.ua import NodeId
from asyncua.ua.uaerrors import BadNoData, BadNotConnected
import requests

from iolink.iodd_collection_helpers import IODDCollection
from iolink.information_node import InformationNode
from opcua_server.method_node import MethodNode


async def check_for_existing_children(
    nnemi_client: Client, port_idx: int, method: MethodNode
) -> None:
    """Check if the InformationNodes parent node has any children. If so, delete them.

    :param nnemi_client: OPC UA Client connected to the NNE MI OPC UA server
    :param port_idx: Port index
    :param method: Method to call if the parent node has children
    """
    _logger = logging.getLogger("OPC UA Server Bridge")
    node_to_check = nnemi_client.get_node(f"ns=6;i=1{(port_idx+1):0>2}200")
    children: list[Node] = await node_to_check.get_children()
    if len(children) == 0:
        return
    _logger.warning(
        f"InformationNodes node ns=6;i=1{(port_idx+1):0>2}200 has existing children."
        "To avoid problems down the line, they will be deleted"
    )
    for child in children:
        _logger.warning(f"Deleting node {child.nodeid.to_string()}")
        await method.call(child.nodeid.to_string())


async def create_information_node(
    iotbox_client: Client,
    information_node: InformationNode,
    port_idx: int,
    inode_idx: int,
    methods: dict[MethodNode],
) -> NodeId:
    """Create an information point node that contains relevant information.

    The structure of the node will be:
    InformationNode Name
    └> Value
    └> LowerBound
    └> UpperBound
    └> Unit

    :param iotbox_client: OPC UA client connected to the IoT box for querying initial
    values
    :param information_node: Information Point object to handle conversion/bounds/units
    :param port_idx: the port the information point belongs to
    :param inode_idx: Index of the information point
    :param methods: Dictionary with available server methods (for NNE MI OPC UA server)
    :returns: NodeId of the Values node
    """
    _logger = logging.getLogger("OPC UA Server Bridge")
    # set up top level information node
    await methods["add_object"].call(
        f"ns=6;i=1{port_idx:0>2}200",  # parent nodeid
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}0",  # nodeid
        f"{information_node.name}",  # browse name
        "Name of InformationNode, manages Values, Bounds, Units",  # description
    )

    iotbox_node = iotbox_client.get_node(
        f"ns=1;s=IOLM/Port {port_idx}/Attached Device/PDI Data Byte Array"
    )
    start_values = await iotbox_node.read_value()

    # set up value, lower and upper bound nodes
    descr = (
        "Real values - if multiple values are present, they correspond to different"
        "units"
    )
    await methods["add_float"].call(
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}0",  # parent nodeid
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}1",  # nodeid
        "Values",  # browse name
        descr,  # description
        information_node.byte_to_real_value(start_values),  # initial value
    )
    descr = (
        "Real lower bounds - if multiple values are present, they correspond to"
        "different units"
    )
    await methods["add_float"].call(
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}0",  # parent nodeid
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}2",  # nodeid
        "Lower Bounds",  # browse name
        descr,  # description
        information_node.low_bounds,  # initial value
    )
    descr = (
        "Real upper bounds - if multiple values are present, they correspond to"
        "different units"
    )
    await methods["add_float"].call(
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}0",  # parent nodeid
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}3",  # nodeid
        "Upper Bounds",  # browse name
        descr,  # description
        information_node.up_bounds,  # initial value
    )
    descr = "Units - if multiple are present, they correspond to the different values"
    await methods["add_string"].call(
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}0",  # parent nodeid
        f"ns=6;i=1{port_idx:0>2}2{inode_idx}4",  # nodeid
        "Units",  # browse name
        descr,  # description
        information_node.units,  # initial value
    )
    _logger.warning(
        f"Created InformationNode {information_node.name} @"
        f"ns=6;i=1{(port_idx+1):0>2}2{inode_idx+1}0"
    )
    return NodeId(Identifier=int(f"1{port_idx:0>2}2{inode_idx}1"), NamespaceIndex=6)


async def find_connected_sensors(
    opcua_host: str, opcua_port: int, connections: int = 8
) -> list[dict]:
    """Find the sensors that are connected to the specified OPC-UA server.

    NodeIds are specific to Pepperl+Fuchs IO-Link Master, probably need to be more
    flexible for other vendors.

    :param opcua_host: Host URL of the OPC-UA server
    :param opcua_port: Port of the OPC-UA server
    :param connections: Number of ports of the IO-Link master, defaults to 8
    :return: List of dictionaries containing port number and sensor names (if available)
    """
    async with Client(f"opc.tcp://{opcua_host}:{opcua_port}") as client:
        connected_sensors: list = []
        for i in range(1, connections + 1):
            node = client.get_node(f"ns=1;s=IOLM/Port {i}/Attached Device/Product Name")
            connected_sensors.append({"port": i, "name": None})
            try:
                sensor = await node.read_value()
                connected_sensors[-1]["name"] = sensor
                logging.debug(f"Sensor {sensor} connected to port {i}")
            except BadNotConnected:
                logging.debug(f"No sensor connected to port {i}")
            except BadNoData:
                logging.debug(
                    f"Sensor connected to port {i}, but name could not be read. "
                    "Might be due to non IO-Link sensor connection."
                )

    return connected_sensors


async def handle_connect(
    iotbox_client: Client,
    iodd_collection: IODDCollection,
    methods: dict[str, MethodNode],
    connection: dict,
    name: str,
    port_idx: int,
) -> dict, IODDCollection:
    """Handle new connection to IoT box.

    This function creates the relevant nodes within the NNE MI OPC UA server and fills
    them with the respective information. If any nodes with the same ID exist already,
    they will be deleted just in case.

    :param iotbox_client: OPC UA Client connected to IO-Link master OPC UA server
    :param iodd_collection: IODDCollection to pick the sensor from
    :param methods: Dictionary of methods the NNE MI OPC UA server provides
    :param connection: Dictionary describing the new connection, used for keeping track
    :param name: Name of the sensor that was connected
    :param port_idx: port index
    :return: Updated connection dictionary
    """
    _logger = logging.getLogger("OPC UA Server Bridge")
    connection["name"] = name
    iodd = iodd_collection.lookup_sensor(name)
    if iodd is not None:
        connection["IODD"] = iodd
    else:
        requests.post(
            f"http://localhost:360/ioddcollection/add?sensor={name}&replace=true"
        )
        resp = requests.get("http://localhost:360/find?findall=true")
        iodd_collection.from_json(resp.json())
        iodd = iodd_collection.lookup_sensor(name)
        connection["IODD"] = iodd
    _logger.warning(f"{name} connected to Port {port_idx+1}")
    for idx, inode in enumerate(connection["IODD"].information_nodes):
        value_nodeid = await create_information_node(
            iotbox_client=iotbox_client,
            information_node=inode,
            port_idx=port_idx + 1,
            inode_idx=idx + 1,
            methods=methods,
        )
        connection["value_nodeids"].append(value_nodeid)
    return connection, iodd_collection


async def handle_disconnect(
    connection: dict, method: MethodNode, port_idx: int
) -> dict:
    """Handle the deletion of nodes when a sensor gets disconnected from the IoT box.

    :param connection: Dictionary used to keep track of connected sensors
    :param method: MethodNode to call the delete function
    :param port_idx: Port index
    :return: Updated connection dictionary
    """
    _logger = logging.getLogger("OPC UA Server Bridge")
    _logger.warning(f"Port {port_idx+1} dropped connection to {connection['name']}")
    for idx, _ in enumerate(connection["IODD"].information_nodes):
        _logger.warning(f"Deleting node ns=6;i=1{(port_idx+1):0>2}2{idx+1}0")
        await method.call(f"ns=6;i=1{(port_idx+1):0>2}2{idx+1}0")
    connection["name"] = None
    connection["IODD"] = None
    connection["value_nodeids"] = []
    return connection


async def handle_writing(
    iotbox_value_node: Node, connection: dict, method: MethodNode
) -> None:
    """Write updated values to the nodes.

    :param iotbox_value_node: Node of the IO-Link master OPC UA server that contains the
    raw byte values
    :param connection: Dictionary used to keep track of connected sensors
    :param method: MethodNode to call the write function
    """
    _logger = logging.getLogger("OPC UA Server Bridge")
    byte_values = await iotbox_value_node.read_value()
    for idx, inode in enumerate(connection["IODD"].information_nodes):
        nodeid = connection["value_nodeids"][idx].to_string()
        inode: InformationNode
        real_values = inode.byte_to_real_value(byte_values)
        await method.call(nodeid, real_values)
        _logger.warning(
            f"Wrote {real_values} to {inode.name}/Values @"
            f"{nodeid}"
        )
        data = {"sensorname": connection["name"], "informationnode": inode.name, "values": real_values, "lowerbounds": inode.low_bounds, "upperbounds": inode.up_bounds, "units": inode.units}
        print(inode.units)
        resp = requests.post(f"http://localhost:360/insert/{str(nodeid[8:10]).lstrip('0')}", json=data)
        print(resp.status_code)
