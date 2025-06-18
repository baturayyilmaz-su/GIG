from enum import Enum

class Satisfiability(Enum):
    SATISFIABLE = 1
    UNSATISFIABLE = 2

class Gender(Enum):
    NONE = 0
    MAN = 1
    WOMAN = 2

class ProblemType(Enum):
    BIPARTITE = 1
    NON_BIPARTITE = 2

class SymmetryOption(Enum):
    SYMMETRIC = 1
    NON_SYMMETRIC = 2


