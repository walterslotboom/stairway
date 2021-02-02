"""
Core topology constraints and resultant topologies

Topologies are defined via a set of constraints regarding their component nodes and connections.
They are then resolved into version-specific nodes which provide access to the underlying automation.
This access is via industries and agencies.
"""
from __future__ import annotations
from typing import List
from util.enums import TextualEnum


class Operator:
    """
    Comparison operators that can be used with constraints.

    Not implemented. Currently assumes equivalence only.
    """
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
    """
    Factory of factories for making nodes' automation objects.

    Each node in the topology has an industry by which all of its (many) factories and services are made.
    These factories in turn create the automation objects that do the actual interactions.
    The industry is specific to that nodes versioning, which is dervied from the constraints.
    The motivation is that once the node is resolved, the tests can be oblivious to the implementation details.

    :ivar: agency: The agency the industry will pass onto its factories
    """

    def __init__(self, agency: AAgency or None = None) -> None:
        self.agency = agency


class AFactory(AIndustry):
    """
    Factory for making a node's automation objects.

    Created by a corresponding industry, a factory creates component/purpose-specific automation objects.
    The industry is specific to that nodes versioning, which is derived from the constraints.
    The exact mechanism for the automation will be dependent on the factory's agency/agents.
    The motivation is that once the node is resolved, the tests can be oblivious to the implementation details.
    """
    pass


class IAgent:
    """
    Interface-style class for define agent globals,
    """

    class IAgentType(TextualEnum):
        """
        Possible agent types
        """
        native = 0  # executes in immediate environment using standard Python libraries
        cli = 1  # executes via CLI drivers like Sarge or PExpect
        rest = 2  # executes via a REST client to REST server

    # Valid agent types
    # @todo this should be demo-specific and empty tuple here
    AGENT_TYPES = (IAgentType.native, IAgentType.cli, IAgentType.rest)


class AAgent:
    """
    The mechanism by which automation actions are performed.

    Specific automation actions need to be performed a specific technology (e.g. REST, CLI, GUI).
    An agent provides a collection of associated capability(s) for a specific component (e.g. networking, logs).
    """
    pass


class NativeAgent(AAgent):
    """
    Performs actions via the system's local libraries.

    Example: Python's file modules creating, modifying, and deleting files.
    """
    pass


class CliAgent(AAgent):
    """
    Performs actives via a CLI interface.

    Examples: Connection via telnet/SSH driven by pexpect or sarge.

    :ivar: ip: IP address for connecting
    :ivar: id: username / ID for logging in
    :ivar: pw: password for logging in
    """

    def __init__(self) -> None:
        super().__init__()
        self.ip = None
        self.id = None
        self.pw = None


class RestAgent(AAgent):
    """
    Performs actions via a standard REST interface
    """
    pass


class AAgency:
    """
    The collection of agents for a node

    Returns on-demand agents for use by the automation objects.
    A single component can have multiple polymorphic agents to accomplish capabilities in different ways.
    The motivation is that the test can remain oblivious to the exact mechanism of its implementation.

    :ivar: agents: All valid agents for the node.
    :ivar: active_agent: The currently active agent that will be used for requested actions.
    :ivar: default_agent: The agent to use if none are explicitly specified.
    """

    def __init__(self) -> None:
        # @ todo make agents a list of agent names
        self.agents = []
        self.active_agent = None
        self.default_agent = None


class Context:
    """
    Arbitrary test-specific environment variables.

    :ivar: default_agent: The agent to use if none are explicitly specified.
    :ivar: kwargs: test specific enviroment variables
    """
    def __init__(self) -> None:
        self.default_agent = None
        self.kwargs = None  # arbitrary additional context is case-specific
