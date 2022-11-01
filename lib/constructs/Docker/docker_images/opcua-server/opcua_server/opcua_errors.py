from asyncua.ua import NodeId


class NodeIdInvalidError(Exception):
    """Exception to handle invalid Node IDs.

    This exception is deliberately different from asyncua's BadNodeIdInvalid so that we
    can provide error messages.
    """

    def __init__(self, nodeid: str | list[str]) -> None:
        """Create NodeIdInvalidError object.

        :param nodeid: list of Node IDs or single Node ID
        """
        self.nodeid = nodeid if isinstance(nodeid, list) else [nodeid]
        super().__init__()

    def __str__(self) -> str:
        """Change standard error message."""
        return "\n".join(
            [
                f"NodeId does not match pattern: {nid} -> ns=[0-9]*;i=[0-9]*"
                for nid in self.nodeid
            ]
        )


class InvalidVariableTypeError(Exception):
    """Exception to handle invalid types when creating OPC UA Variable nodes."""

    def __init__(
        self, nodeid: str | NodeId, var_type: type, desired_type: type
    ) -> None:
        """Create InvalidVariableTypeError object.

        :param nodeid: Node ID of the node that was about to be created
        :param var_type: invalid variable type
        :param desired_type: type that the variable was supposed to be
        """
        self.nodeid = nodeid if isinstance(nodeid, str) else nodeid.to_string()
        self.var_type = var_type
        self.desired_type = desired_type
        super().__init__()

    def __str__(self) -> str:
        """Change standard error message."""
        return (
            f"Invalid type {self.var_type} for Variable node with ID {self.nodeid}. "
            f"Variable should be of type: {self.desired_type}"
        )


class InconsistentArrayError(Exception):
    """Exception to handle array type inputs where the elements have different types."""

    def __init__(self, nodeid: str | NodeId, ls: list) -> None:
        """Create InconsistentArrayError object.

        :param nodeid: Node ID of the node that is supposed to be assigned the list as
        its value
        :param ls: list of values that have inconsistent types
        """
        self.nodeid = nodeid if isinstance(nodeid, str) else nodeid.to_string()
        self.ls = ls
        super().__init__()

    def __str__(self) -> str:
        """Change standard error message."""
        return (
            "Invalid array of values: Values have different types from each other: "
            f"{self.ls} -> type() -> {[type(li) for li in self.ls]}"
        )
