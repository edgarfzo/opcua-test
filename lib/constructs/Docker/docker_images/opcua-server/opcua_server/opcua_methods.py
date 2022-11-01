"""Server side methods of the NNE MI OPC UA server.

AFAIK we cannot create client side methods to add, modify and delete nodes in the OPC UA
server. There are security issues related to this. The methods are thus created server
side, and provided to the client via nodes that contain the methods. This module
contains the definitions of the functions - they are added in the actual creation of the
server later.

Functions
---------
add_folder_
    Handles the creation of a folder node.
add_object_
    Handles the creation of an object node.
add_variable_
    Handles the creation of a variable node, regardless of variable type.
delete_node_
    Handles the deletion of a given node.
validate_nodeid
    Validates a nodeid against the provided pattern.
write_value_to_node_
    Writes a new value to the given node.
"""
from itertools import compress
import logging
import re

from asyncua import Server, ua

from opcua_server.opcua_errors import NodeIdInvalidError, InconsistentArrayError

_logger = logging.getLogger("NNE-OPC-UA Server")


async def add_folder_(
    server: Server, parent_nodeid: str, nodeid: str, bname: str, descr: str
) -> None:
    """Add a folder as a child to specified parent node.

    :param server: OPC-UA server that will hold the new node
    :param parent_nodeid: NodeId of the parent node to the newly created one
    :param nodeid: NodeId of the node to be created
    :param bname: Browse name of the node to be created
    :param descr: Description of the node
    """
    validate_nodeid(nodeid)
    parent_node = server.get_node(parent_nodeid)
    node = await parent_node.add_folder(nodeid, bname=bname)
    await node.write_attribute(
        ua.AttributeIds.Description,
        ua.DataValue(ua.Variant(ua.LocalizedText(descr, "en"))),
    )
    _logger.debug(f"Successfully created folder {bname} @ {nodeid}")


async def add_object_(
    server: Server, parent_nodeid: str, nodeid: str, bname: str, descr: str
) -> None:
    """Add a variable as a child to specified parent node.

    :param server: OPC-UA server that will hold the new node
    :param parent_nodeid: NodeId of the parent node to the newly created one
    :param nodeid: NodeId of the node to be created
    :param bname: Browse name of the node to be created
    :param descr: Description of the node
    """
    validate_nodeid(parent_nodeid, nodeid)
    parent_node = server.get_node(parent_nodeid)
    node = await parent_node.add_object(nodeid, bname=bname)
    await node.write_attribute(
        ua.AttributeIds.Description,
        ua.DataValue(ua.Variant(ua.LocalizedText(descr, "en"))),
    )
    _logger.debug(f"Successfully created object {bname} @ {nodeid}")


async def add_variable_(
    server: Server,
    parent_nodeid: str,
    nodeid: str,
    bname: str,
    descr: str,
    val: str | int | float | list = None,
) -> None:
    """Add a variable as a child to specified parent node.

    :param server: OPC-UA server that will hold the new node
    :param parent_nodeid: NodeId of the parent node to the newly created one
    :param nodeid: NodeId of the node to be created
    :param bname: Browse name of the node to be created
    :param descr: Description of the node
    :param val: Initial value for the new variable node
    """
    if isinstance(val, list):
        if any([False if isinstance(li, type(val[0])) else True for li in val]):
            raise InconsistentArrayError(nodeid=nodeid, ls=val)
    validate_nodeid(parent_nodeid, nodeid)
    parent_node = server.get_node(parent_nodeid)
    node = await parent_node.add_variable(nodeid, bname=bname, val=val)
    await node.write_attribute(
        ua.AttributeIds.Description,
        ua.DataValue(ua.Variant(ua.LocalizedText(descr, "en"))),
    )
    await node.set_writable()
    _logger.debug(f"Successfully created variable {bname} with value {val} @ {nodeid}")


async def delete_node_(server: Server, nodeid: str) -> None:
    """Delete specified node from OPC-UA server.

    :param server: OPC-UA server that contains the nodes to be deleted
    :param nodeid: Node id as a string in form of "ns=XX;i=XX"
    """
    validate_nodeid(nodeid)
    node_to_delete = server.get_node(nodeid)
    browse_name = await node_to_delete.read_browse_name()
    await server.delete_nodes([node_to_delete], recursive=True)
    _logger.debug(f"Successfully deleted node {browse_name} @ {nodeid}")


def validate_nodeid(*nodeid: str | ua.NodeId) -> bool:
    """Check if provided node id matches required pattern.

    :param nodeid: Node id as a string or NodeId object
    :return: True if node id is valid, False otherwise
    """
    for i, nid in enumerate(nodeid):
        if isinstance(nid, ua.NodeId):
            nodeid[i] = nid.to_string()

    invalid = [
        True if re.search(r"(?:ns=)\d*(?:;i=)\d*$", nid) is None else False
        for nid in nodeid
    ]
    if any(invalid):
        raise NodeIdInvalidError(list(compress(nodeid, invalid)))


async def write_value_to_node_(
    server: Server, nodeid: str, val: str | int | float | list
) -> None:
    """Write a new value to the given node.

    :param server: OPCUA server that contains the node to write to
    :param nodeid: Node id as a string in form of "ns=XX;i=XX"
    :param val: value to write
    """
    validate_nodeid(nodeid)
    node_to_write_to = server.get_node(nodeid)
    await node_to_write_to.write_value(val)
