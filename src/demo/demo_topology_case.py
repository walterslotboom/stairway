"""
Demo suite/cases for topology instantiation

Goes through the process of defining a series of topology constraints, satisfying those constraints, and
running a simple step that utilizes node-specific functionality within the topology.
"""

import sys

from src.demo.demo_topology import DemoNodeConstraints, DemoConstraintSatisfier, DemoConstraintService
from src.test.itest import ITest
from src.test.testable import ACase, ASuite
from src.test.topology import ATopologyConstraint, IAgent, Operator, Constraint


class ATopoCase(ACase):
    """
    Generalized case that satisfies many potential topologies
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        agent = kwargs.get("agent", IAgent.IAgentType.native.name)

        self.demo_topology_constraint = ATopologyConstraint()

        # Build the topologies constraints from textual seeds of subclass cases.
        # These seeds dictate the industry. Agency is passed from CLI.
        for demo_node_factory_constraint_seed in self.demo_node_factory_constraint_seeds:
            demo_node_constraints = \
                DemoConstraintService.make_node_constraints(*demo_node_factory_constraint_seed)
            demo_node_agency_constraint = Constraint('agent', Operator.EQ, agent)
            demo_node_constraints.constraints.append(demo_node_agency_constraint)
            demo_node_name = '{}{}{}'.format(*demo_node_factory_constraint_seed[0],
                                             *demo_node_factory_constraint_seed[1],
                                             *demo_node_factory_constraint_seed[2])
            self.demo_topology_constraint.add_node_constraint(demo_node_name, demo_node_constraints)
        self.demo_topology = None

    def reserve(self):
        self.demo_topology = DemoConstraintSatisfier().satisfy_topology(self.demo_topology_constraint)

    def test(self):
        """
        Exercise base functionality of satisfied nodes

        :return: None
        """

        for node_name in self.demo_topology.nodes:
            # Drill down the industry / factory composition to the functionality
            industry = self.demo_topology.nodes[node_name].industry
            namer_factory = industry.make_name_factory()
            namer = namer_factory.make_namer()

            # Exercise a testable using that functionally
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
    """
    Gets node constraints from the command line

    Analog for passing in version and build number
    """
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
