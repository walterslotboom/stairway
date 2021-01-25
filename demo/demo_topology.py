from test.topology import ANodeConstraints, AIndustry, AFactory, AAgency, ConstraintSatisfier, ANode, \
    Constraint, Operator, IAgent
from util.service.misc_service import ListService
from util.service.report_service import ReportService


class DemoNodeConstraints(ANodeConstraints):
    # These can be construed to represent a node category like client, dut, and server
    UPPERCASE = 'uppercase'
    UPPERCASE_A = 'A'
    UPPERCASE_B = 'B'
    UPPERCASE_C = 'C'
    UPPERCASES = [UPPERCASE_A, UPPERCASE_B, UPPERCASE_C]

    # These can be construed to represent a node subcategory like product category or branch
    LOWERCASE = 'lowercase'
    LOWERCASE_A = 'a'
    LOWERCASE_B = 'b'
    LOWERCASE_C = 'c'
    LOWERCASES = [LOWERCASE_A, LOWERCASE_B, LOWERCASE_C]

    # These can be construed to represent a version and/or build number
    NUMBER = 'number'
    NUMBER_1 = '1'
    NUMBER_2 = '2'
    NUMBER_3 = '3'
    NUMBERS = [NUMBER_1, NUMBER_2, NUMBER_3]

    VALIDS = {NUMBER: NUMBERS,
              UPPERCASE: UPPERCASES,
              LOWERCASE: LOWERCASES}


class DemoIndustry(AIndustry):

    class NameFactory(AFactory):

        class ANamer:
            NAME = None  # This is an example of dynamically supplied context

            @property
            def name(self):
                return self.NAME

        class NamerNative(ANamer):

            def print_name(self):
                ReportService.report('Node name: {}'.format(self.name))

        def make_namer(self, agent=None):
            if agent is None:
                self.agency.active_agent = self.agency.default_agent
            if self.agency.active_agent == IAgent.IAgentType.native.name:
                return self.NamerNative()

    def make_name_factory(self, agent=None):
        if agent is None:
            self.agency.active_agent = self.agency.default_agent
        return self.NameFactory(self.agency)


class Aa1Industry(DemoIndustry):
    class NameFactory(DemoIndustry.NameFactory):
        class NamerNative(DemoIndustry.NameFactory.NamerNative):
            NAME = 'Aa1'


class Aa2Industry(DemoIndustry):
    class NameFactory(DemoIndustry.NameFactory):
        class NamerNative(DemoIndustry.NameFactory.NamerNative):
            NAME = 'Aa2'


class Bc3Industry(DemoIndustry):
    class NameFactory(DemoIndustry.NameFactory):
        class NamerNative(DemoIndustry.NameFactory.NamerNative):
            NAME = 'Bc3'


class DemoAgency(AAgency):

    def __init__(self):
        super().__init__()
        self.agents[IAgent.IAgentType.native.name] = self.NativeAgent()
        self.agents[IAgent.IAgentType.cli.name] = self.CliAgent()
        self.agents[IAgent.IAgentType.native.name] = self.RestAgent()


class Aa1Agency(DemoAgency):
    pass


class Aa2Agency(DemoAgency):
    pass


class Bc3Agency(DemoAgency):
    pass


# convenience wrapper
class DemoConstraintService:

    @staticmethod
    def make_factory_constraints(uppercase, lowercase, number):
        return [Constraint(DemoNodeConstraints.UPPERCASE, Operator.EQ, uppercase),
                Constraint(DemoNodeConstraints.LOWERCASE, Operator.EQ, lowercase),
                Constraint(DemoNodeConstraints.NUMBER, Operator.EQ, number)]

    @staticmethod
    def make_node_factory_constraints(uppercase, lowercase, number):
        demo_constraints = DemoConstraintService.make_factory_constraints(uppercase, lowercase, number)
        demo_node_constraints = DemoNodeConstraints(demo_constraints)
        return demo_node_constraints


class DemoConstraintSatisfier(ConstraintSatisfier):

    # An example of a hierarchical constraint satisfaction
    def satisfy_node(self, constraints):
        node = ANode()

        uppercase_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.UPPERCASE)
        lowercase_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.LOWERCASE)
        number_constraint = ListService.get_item_by_value(constraints, 'trait', DemoNodeConstraints.NUMBER)
        uppercase = uppercase_constraint.value
        lowercase = lowercase_constraint.value
        number = number_constraint.value
        if uppercase is DemoNodeConstraints.UPPERCASE_A:
            if lowercase is DemoNodeConstraints.LOWERCASE_A:
                if number is DemoNodeConstraints.NUMBER_1:
                    node.agency = Aa1Agency()
                    node.industry = Aa1Industry(node.agency)
                elif number is DemoNodeConstraints.NUMBER_2:
                    node.agency = Aa2Agency()
                    node.industry = Aa2Industry(node.agency)
        elif uppercase is DemoNodeConstraints.UPPERCASE_B:
            if lowercase is DemoNodeConstraints.LOWERCASE_C:
                if number is DemoNodeConstraints.NUMBER_3:
                    node.agency = Bc3Agency()
                    node.industry = Bc3Industry(node.agency)

        agent_constraint = ListService.get_item_by_value(constraints, 'trait', 'agent')
        node.agency.default_agent = agent_constraint.value
        node.agency.active_agent = agent_constraint.value

        return node
