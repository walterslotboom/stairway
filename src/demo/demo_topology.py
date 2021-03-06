"""
Example of purpose-specific topology subclasses

Provides a rudimentary example of extending the abstract topology classes.
Examples are impractical but provide analogies for more meaningful usage.
"""

from src.test.topology import ANodeConstraints, AIndustry, AFactory, AAgency, ConstraintSatisfier, ANode, \
    Constraint, Operator, IAgent
from src.util.service.misc_service import ListService
from src.util.service.report_service import ReportService


class DemoNodeConstraints(ANodeConstraints):
    """
    Three constraint types are defined, each with three valid possible values.

    Uppercase can be construed to represent a node category like client, dut, and server
    Lowercase can be construed to represent a node refinement like client OS type or cloud vendor
    Number can be construed to represent a version and/or build number
    """

    UPPERCASE = 'uppercase'
    UPPERCASE_A = 'A'
    UPPERCASE_B = 'B'
    UPPERCASE_C = 'C'
    UPPERCASES = [UPPERCASE_A, UPPERCASE_B, UPPERCASE_C]

    LOWERCASE = 'lowercase'
    LOWERCASE_A = 'a'
    LOWERCASE_B = 'b'
    LOWERCASE_C = 'c'
    LOWERCASES = [LOWERCASE_A, LOWERCASE_B, LOWERCASE_C]

    NUMBER = 'number'
    NUMBER_1 = '1'
    NUMBER_2 = '2'
    NUMBER_3 = '3'
    NUMBERS = [NUMBER_1, NUMBER_2, NUMBER_3]

    VALIDS = {NUMBER: NUMBERS,
              UPPERCASE: UPPERCASES,
              LOWERCASE: LOWERCASES}


class ANamer:
    """
    Automation that transcends particular agent.

    Contains the non-interface/agency-specific processing that needs to be done.
    This minimal example simply returns a name unique to the class.
    Actual name will differ based on constraint-driven node satisfaction into appropriate subclasses.
    """
    NAME = None

    @property
    def name(self):
        return self.NAME


class NamerNative(ANamer):
    """
    Agent-specific wrapper for basic automation

    This native agent simply outputs the unique name to standard out.
    """
    def print_name(self):
        ReportService.report('Node name: {}'.format(self.name))


class NameFactory(AFactory):
    """
    Factory for making agent-specific automation objects.

    Will use default agent type if none supplied.
    """
    NAMER_NATIVE = NamerNative

    def make_namer(self, agent=None):
        if agent is None:
            self.agency.active_agent = self.agency.default_agent
        if self.agency.active_agent == IAgent.IAgentType.native.name:
            return self.NAMER_NATIVE()


class DemoIndustry(AIndustry):
    """
    Factory for creating factories of agent-specific automation objects.

    Will use default agent type if none supplied.
    """
    NAME_FACTORY = NameFactory

    def make_name_factory(self, agent=None):
        if agent is None:
            self.agency.active_agent = self.agency.default_agent
        return self.NAME_FACTORY(self.agency)

# The following are several uppercase/lowercase/number (e.g. client / OS family / OS version) permutations


class Aa1NamerNative(NamerNative):
    NAME = 'Aa1'


class Aa1NameFactory(NameFactory):
    NAMER_NATIVE = Aa1NamerNative


class Aa1Industry(DemoIndustry):
    NAME_FACTORY = Aa1NameFactory


class Aa2NamerNative(NamerNative):
    NAME = 'Aa2'


class Aa2NameFactory(NameFactory):
    NAMER_NATIVE = Aa2NamerNative


class Aa2Industry(DemoIndustry):
    NAME_FACTORY = Aa2NameFactory


class Bc3NamerNative(NamerNative):
    NAME = 'Bc3'


class Bc3NameFactory(NameFactory):
    NAMER_NATIVE = Bc3NamerNative


class Bc3Industry(DemoIndustry):
    NAME_FACTORY = Bc3NameFactory


class DemoAgency(AAgency):
    """
    Agency specific to demo

    Only supports native agent for now.
    """

    def __init__(self):
        super().__init__()
        self.agents = [IAgent.IAgentType.native]


# convenience wrapper
class DemoConstraintService:
    """
    Convenience wrapper for creating demo node constraints

    Normal constraints will likely use convenience wrappers as well.
    This is because the node constraint API is very generalized, but most constraints very similar.
    """

    @staticmethod
    def make_constraints(uppercase, lowercase, number):
        return [Constraint(DemoNodeConstraints.UPPERCASE, Operator.EQ, uppercase),
                Constraint(DemoNodeConstraints.LOWERCASE, Operator.EQ, lowercase),
                Constraint(DemoNodeConstraints.NUMBER, Operator.EQ, number)]

    @staticmethod
    def make_node_constraints(uppercase, lowercase, number):
        demo_constraints = DemoConstraintService.make_constraints(uppercase, lowercase, number)
        demo_node_constraints = DemoNodeConstraints(demo_constraints)
        return demo_node_constraints


class DemoConstraintSatisfier(ConstraintSatisfier):
    """
    Example of a hierarchical constraint satisfaction

    An individual node's constraints are extracted and used to instantiate its specific industry and agency.
    """

    def satisfy_node(self, constraints):
        node = ANode()
        node.agency = DemoAgency()

        uppercase_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.UPPERCASE)
        lowercase_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.LOWERCASE)
        number_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.NUMBER)
        uppercase = uppercase_constraint.value
        lowercase = lowercase_constraint.value
        number = number_constraint.value
        if uppercase is DemoNodeConstraints.UPPERCASE_A:
            if lowercase is DemoNodeConstraints.LOWERCASE_A:
                if number is DemoNodeConstraints.NUMBER_1:
                    node.industry = Aa1Industry(node.agency)
                elif number is DemoNodeConstraints.NUMBER_2:
                    node.industry = Aa2Industry(node.agency)
        elif uppercase is DemoNodeConstraints.UPPERCASE_B:
            if lowercase is DemoNodeConstraints.LOWERCASE_C:
                if number is DemoNodeConstraints.NUMBER_3:
                    node.industry = Bc3Industry(node.agency)

        agent_constraint = ListService.get_item_by_value(constraints, 'trait', 'agent')
        node.agency.default_agent = agent_constraint.value
        node.agency.active_agent = agent_constraint.value

        return node
