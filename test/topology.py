# @todo currently not used in any meaningful way
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
    # @todo make operator into property with validation
    def __init__(self, trait=None, operator=None, value=None):
        self.trait = trait
        self.operator = operator
        self.value = value


class Constraints:
    VALIDS = {}

    # @todo make constraints into property with validation
    def __init__(self, constraints=None):
        self.constraints = []
        if constraints is None:
            constraints = []
        for constraint in constraints:
            self.add_constraint(constraint)

    def add_constraint(self, constraint):
        if self.is_valid_constraint(constraint):
            self.constraints.append(constraint)
        else:
            raise "Invalid constraint: {}".format(constraint)

    # must match all fields of constraint
    def remove_constraint(self, constraint):
        pass

    def is_valid_constraint(self, constraint):
        is_valid = False
        if constraint.trait in self.VALIDS:
            if constraint.value in self.VALIDS[constraint.trait]:
                is_valid = True
        return is_valid


class ANodeConstraints(Constraints):
    pass


class ATopologyConstraint:

    def __init__(self):
        self.nodes_constraints = {}

    def add_node_constraint(self, node_name, node_constraints):
        self.nodes_constraints[node_name] = node_constraints

    def remove_node_constraint(self, node_name):
        self.nodes_constraints.pop(node_name)


class ATopology:

    def __init__(self):
        self.nodes = {}


class ANode:

    def __init__(self):
        self.context = {}
        self.industry = None
        self.agency = None


class ConstraintSatisfier:

    def satisfy_topology(self, topology_constraint):
        # the satisfaction method here can be arbitrarily complex
        # demo code here is just an example
        topology = ATopology()
        for node_name, node_constraints in topology_constraint.nodes_constraints.items():
            constraints = node_constraints.constraints
            node = self.satisfy_node(constraints)
            topology.nodes[node_name] = node
        return topology

    def satisfy_node(self, constraints):
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
