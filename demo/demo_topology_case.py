import sys

from demo.demo_topology import DemoNodeConstraints, DemoConstraintSatisfier, DemoConstraintService
from test.itest import ITest
from test.testable import ACase, ASuite
from test.topology import ATopologyConstraint, IAgent, Operator, Constraint


# @todo define default agent in topology. Use context object; constructed during satisfy; replaces direct agent?
# @todo overwrite default agent from command line


class ATopoCase(ACase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        agent = kwargs.get("agent", IAgent.IAgentType.native.name)

        self.demo_topology_constraint = ATopologyConstraint()

        for demo_node_factory_constraint_seed in self.demo_node_factory_constraint_seeds:
            demo_node_constraints = \
                DemoConstraintService.make_node_constraints(*demo_node_factory_constraint_seed)
            demo_node_constraint = Constraint('agent', Operator.EQ, agent)
            demo_node_constraints.constraints.append(demo_node_constraint)
            self.demo_topology_constraint.add_node_constraint('{}{}{}'.format(*demo_node_factory_constraint_seed[0],
                                                                              *demo_node_factory_constraint_seed[1],
                                                                              *demo_node_factory_constraint_seed[2]),
                                                              demo_node_constraints)
        self.demo_topology = None

    def reserve(self):
        self.demo_topology = DemoConstraintSatisfier().satisfy_topology(self.demo_topology_constraint)

    def test(self):
        for node_name in self.demo_topology.nodes:
            industry = self.demo_topology.nodes[node_name].industry
            namer_factory = industry.make_name_factory()
            namer = namer_factory.make_namer()

            with self.stepper() as stepper:
                namer.print_name()
                name = namer.name
                stepper.result.description = 'Property extracted from satisfied topology node'
                stepper.result.state = ITest.State.PASS
                stepper.result.message = 'Demo node name: {}'.format(name)

    @property
    def demo_node_factory_constraint_seeds(self):
        return []

    @staticmethod
    def make_arg_parser():
        # funny super call syntax required for static method?
        parser = super(ATopoCase, ATopoCase).make_arg_parser()
        agent_choices = tuple(str(agent) for agent in IAgent.AGENT_TYPES)
        parser.add_argument('--agent', '-a', required=False, choices=agent_choices,
                            default=IAgent.IAgentType.native.name)
        return parser


class OneNodeTopoCase(ATopoCase):
    DESCRIPTION = "Single-node topology instantiation"

    @property
    def demo_node_factory_constraint_seeds(self):
        return [(DemoNodeConstraints.UPPERCASE_A, DemoNodeConstraints.LOWERCASE_A, DemoNodeConstraints.NUMBER_1)]


class ThreeNodeTopoCase(ATopoCase):
    DESCRIPTION = "Three-node topology instantiation"

    @property
    def demo_node_factory_constraint_seeds(self):
        return [(DemoNodeConstraints.UPPERCASE_A, DemoNodeConstraints.LOWERCASE_A, DemoNodeConstraints.NUMBER_1),
                (DemoNodeConstraints.UPPERCASE_A, DemoNodeConstraints.LOWERCASE_A, DemoNodeConstraints.NUMBER_2),
                (DemoNodeConstraints.UPPERCASE_B, DemoNodeConstraints.LOWERCASE_C, DemoNodeConstraints.NUMBER_3)]


class CliConstraintTopoCase(ATopoCase):
    # Analog for passing in version and build number
    DESCRIPTION = "CLI-based parameter topology instantiation"

    def __init__(self, **kwargs):
        self.uppercase = kwargs.get(DemoNodeConstraints.UPPERCASE, DemoNodeConstraints.UPPERCASE_A)
        self.lowercase = kwargs.get(DemoNodeConstraints.LOWERCASE, DemoNodeConstraints.LOWERCASE_A)
        self.number = kwargs.get(DemoNodeConstraints.NUMBER, DemoNodeConstraints.NUMBER_1)
        super().__init__(**kwargs)

    @staticmethod
    def make_arg_parser():
        # funny super call syntax required for static method?
        parser = super(CliConstraintTopoCase, CliConstraintTopoCase).make_arg_parser()
        uppercase_choices = tuple(uppercase for uppercase in DemoNodeConstraints.UPPERCASES)
        parser.add_argument('--%s' % DemoNodeConstraints.UPPERCASE, '-u', required=False, choices=uppercase_choices,
                            default=DemoNodeConstraints.UPPERCASE_A)
        lowercase_choices = tuple(lowercase for lowercase in DemoNodeConstraints.LOWERCASES)
        parser.add_argument('--%s' % DemoNodeConstraints.LOWERCASE, '-w', required=False, choices=lowercase_choices,
                            default=DemoNodeConstraints.LOWERCASE_A)
        number_choices = tuple(number for number in DemoNodeConstraints.NUMBERS)
        parser.add_argument('--%s' % DemoNodeConstraints.NUMBER, '-n', required=False, choices=number_choices,
                            default=DemoNodeConstraints.NUMBER_1)
        return parser

    @property
    def demo_node_factory_constraint_seeds(self):
        return [(self.uppercase, self.lowercase, self.number)]


class AllToposSuite(ASuite):

    DESCRIPTION = "All topology demo suites and cases"

    def __init__(self, **kwargs):
        testables = [OneNodeTopoCase(**kwargs), ThreeNodeTopoCase(**kwargs), CliConstraintTopoCase(**kwargs)]
        super().__init__(testables, **kwargs)


if __name__ == '__main__':
    arg_parser = AllToposSuite.make_arg_parser()
    args = AllToposSuite.parse_args(arg_parser, sys.argv[1:])
    AllToposSuite(**args).execute()
