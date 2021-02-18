# stairway
Basic Python testing framework

Includes core classes for running tests, recording results, and reporting those results. 

Testable hierarchy contains base classes for suites, cases, flights (collections of steps), and steps.  Results automatically propogate up through the testable heirarchy as tests run, and are summarized as they complete. Progress tracking and results is integrated into the running of the testable objects.

Automation topology and components are defined via logical constraints, which are dynamically satisfied into the appropriate factories. Tests then instantiate their version-specific objects as needed. The actual actions are performed via agents targeted against specific interfaces (REST, CLI, GUI, native).
