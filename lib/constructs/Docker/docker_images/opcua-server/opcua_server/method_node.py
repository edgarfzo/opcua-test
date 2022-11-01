from asyncua import Client, Node
from asyncua.ua import NodeId


class MethodNode:
    """Manages method nodes to make them easier to access.

    Attributes
    ----------
    nodeid : NodeId
        ID of the node with the method to manage
    node : Node
        Node with the method to manage

    Methods
    -------
    call:
        Tells the node to call its method
    """

    def __init__(self, client: Client, nodeid: str | NodeId) -> None:
        """Create MethodNode object.

        :param client: Client connected to the server that contains the node
        :param nodeid: ID of the node that has the method to manage.
        """
        if isinstance(nodeid, NodeId):
            self.nodeid = nodeid
        else:
            self.nodeid = NodeId(
                int(nodeid.split(";")[1][2:]), int(nodeid.split(";")[0][3:])
            )
        self.node: Node = client.get_node(nodeid)

    async def call(self, *args):
        """Call the nodes method.

        Arguments should match those of the method you want to call.
        """
        await self.node.call_method(self.nodeid, *args)
