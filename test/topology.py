from __future__ import annotations

from typing import List

from util.enums import TextualEnum


class Operator:
    LT = '<'
    LE = '<='
    EQ = '=='
    NE = "!="
    GE = '>='
    GT = '>'

    VALIDS = [LT, LE, EQ, NE, GE, GT]


class Constraint:
    """
    Limiting criteria for aspect of test entities

    :ivar: trait: Name of trait to constrain
    :ivar: operator: How to constrain the trait
    :ivar: value: Delimiter for the constraint
    """

    def __init__(self, trait: str or None = None, operator: Operator or None = None, value: str or None = None):
        self.trait = trait
        self.operator = operator  # @todo make operator into property with validation
        self.value = value


class Constraints:
    """
    Constraints to apply to a specific test entity

    :ivar: constraints: List of constraints
    """
    VALIDS = {}

    # @todo make constraints into property with validation
    def __init__(self, constraints: List[Constraint]) -> None:
        self.constraints = []
        if constraints is None:
            constraints = []
        for constraint in constraints:
            self.add_constraint(constraint)

    def add_constraint(self, constraint: Constraint) -> None:
        """
        Add a constraint to the entity's constraints

        Check validity before adding

        :param constraint: Constraint to add
        """
        if self.is_valid_constraint(constraint):
            self.constraints.append(constraint)
        else:
            raise "Invalid constraint: {}".format(constraint)

    def is_valid_constraint(self, constraint: Constraint) -> bool:
        """
        Checks if constraint is valid

        :param constraint: Constraint to check validity of
        :return: boolean indicating if constraint is valid
        """
        is_valid = False
        if constraint.trait in self.VALIDS:
            if constraint.value in self.VALIDS[constraint.trait]:
                is_valid = True
        return is_valid


class ANodeConstraints(Constraints):
    """
    Constraints specific to nodes in test topology

    Currently abstract with no content. Just planning ahead.
    """
    pass


class ATopologyConstraint:
    """
    Collections of constraints for all nodes in the topology.

    All of these must be satisfied for the topology as a whole to be satisfied.

    :ivar: nodes_constraints: dictionary of node constraints
    """
    def __init__(self) -> None:
        self.nodes_constraints = {}

    def add_node_constraint(self, node_name: str, node_constraints: ANodeConstraints) -> None:
        """
        Add a node constraint to the topology constraint
        :param node_name: Unique identifier of the node will be used to access it from resultant topology
        :param node_constraints:
        """
        self.nodes_constraints[node_name] = node_constraints

    def remove_node_constraint(self, node_name: str) -> ANodeConstraints:
        """
        Remove a node constraint from the topology's constraints

        :param node_name: Name of node whose constraints to remove
        :return: Removed node constraint
        """
        node_constraint = self.nodes_constraints.pop(node_name)
        return node_constraint


class ATopology:
    """
    Topology resulting from the satisfaction of the topology constraints

    Currently a dictionary of nodes, but can include other resources like networking and cloud.

    :ivar: nodes = Nodes constituting the topology
    """

    def __init__(self):
        self.nodes = {}


class ANode:
    """
    Node resulting from satisfaction of node constraints.

    :ivar: context: Relevant properties of the node that are instance specific (e.g. IP address)
    :ivar: industry: Factory for making the node's factories
    :ivar: agency: Contains the agents via which the node's actions will be executed
    """

    def __init__(self):
        self.context = {}
        self.industry = None
        self.agency = None


class ConstraintSatisfier:
    """
    Resolves constraints into usable objects

    The satisfaction algorithm can be arbitrarily complex.
    In more sophisticated frameworks this will include resource reservation.
    """

    def satisfy_topology(self, topology_constraint: ATopologyConstraint) -> ATopology:
        """
        Resolve topology constraints into usuable topology objects.

        :param topology_constraint: Topology constraint to be resolved into topology.
        :return: Topology containing usable nodes
        """
        topology = ATopology()
        for node_name, node_constraints in topology_constraint.nodes_constraints.items():
            constraints = node_constraints.constraints
            node = self.satisfy_node(constraints)
            topology.nodes[node_name] = node
        return topology

    def satisfy_node(self, constraints: ANodeConstraints) -> ANode:
        """
        Resolve nodes constraints into usuable nodes.

        :param constraints: Node constraints to resolve.
        """
        raise NotImplementedError


class AIndustry:

    def __init__(self, agency=None):
        self.agency = agency


class AFactory(AIndustry):
    pass


class IAgent:

    class IAgentType(TextualEnum):
        native = 0  # executes in immediate environment using standard Python libraries
        cli = 1  # executes via CLI drivers like Sarge or PExpect
        rest = 2  # executes via a REST client to REST server

    # @todo this should be demo-specific and empty tuple here
    AGENT_TYPES = (IAgentType.native, IAgentType.cli, IAgentType.rest)


class AAgent:
    pass


# @todo subclasses should be demo-specific! should subclasses be pushed down or extracted?
class AAgency:

    class NativeAgent(AAgent):
        pass

    class CliAgent(AAgent):

        def __init__(self):
            super().__init__()
            self.ip = None
            self.id = None
            self.pw = None

    class RestAgent(AAgent):
        pass

    def __init__(self):
        self.agents = {}
        self.active_agent = None
        self.default_agent = None


class Context:
    def __init__(self):
        self.default_agent = None
        self.kwargs = None  # arbitrary additional context is case-specific
