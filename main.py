from util.Enums import *
from util.GIG import *
import argparse

def parseBoolStr(arg : str) -> bool:
    if arg.lower() in ('true', 't', '1'):
        return True
    elif arg.lower() in ('false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected. Either use one of {"true", "t", "1"} or one of {"false", "f", "0"}')
    
def parseSeedParameterStr(arg : str) -> list[int]:
    result = []
    values = arg.strip().split(",")

    for v in values:
        try:
            val = int(v.strip())
            result.append(val)
        except:
            raise argparse.ArgumentTypeError('Must contain a single number (e.g., "x"), or a list of numbers seperated by comma (e.g., "x,y,z")')
    return result

def checkInputSeedSizeValue(seedSizeVal : list[int], instanceSizeVal : int):
    if len(seedSizeVal) == 1:
        assert instanceSizeVal % sum(seedSizeVal) == 0, "Given seed size does not divide instance size!"
    else:
        assert instanceSizeVal == sum(seedSizeVal), "Sum of given seed sizes does not add up to given instance size!"

def checkIfCyleSizeIsOdd(cycleSizes : list[int]):
    for val in cycleSizes:
        assert val % 2 == 1, "Specified cycle sizes must be odd!"

def main(args):
    bip = ProblemType.BIPARTITE if args.bip else ProblemType.NON_BIPARTITE
    sat = Satisfiability.SATISFIABLE if args.sat else Satisfiability.UNSATISFIABLE
    symOpt = SymmetryOption.SYMMETRIC if args.sym else SymmetryOption.NON_SYMMETRIC

    gig = GIG(instCount=args.iAmount,
              instSize=args.iSize,
              seedSizes=args.sSize,
              solutionCounts=args.sSolution,
              cycleSizes=args.cSize,
              cycleCounts=args.cAmount,
              cycleRankDistances=args.cRankDistance,
              p1=args.p1,
              p2=args.p2,
              upBound=args.ub,
              sat=sat,
              symOpt=symOpt,
              bipartite=bip,
              instFilePath=args.dir,
              copySeed=args.copy)

    gig.generateInstances()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-iAmount", type=int, help="Number of instances to generate [default = 20]", required=False, default=20)
    parser.add_argument("-iSize", type=int, help="Instance size (i.e., number of men for SMTI instance, number of agent for SRTI instance) [default = 25]", required=False, default=25)
    parser.add_argument("-sSize", type=parseSeedParameterStr, help="Seed size (either a single positive integer or a lists of positive integers separeted by comma). If a single integer is given, it should divide the instance size. If a list is given it should add up to instnce size [default = 5,7,6,7]", required=False, default="5,7,6,7")
    parser.add_argument("-sSolution", type=parseSeedParameterStr, help="Amount of solution in satisfiable seeds (must have the same type of seed size input (sSize)). [default = 2,4,3,4]", required=False, default="2,4,3,4")
    parser.add_argument("-cSize", type=parseSeedParameterStr, help="Size of the cycle in UNSAT SRTI seeds (must have the same type of seed size input (sSize), and must contain odd number(s)). [default = 3,3,3,5]", required=False, default="3,3,3,5")
    parser.add_argument("-cAmount", type=parseSeedParameterStr, help="Amount of cycles in UNSAT SRTI seeds (must have the same type of seed size input (sSize)). [default = 1,2,2,1]", required=False, default="1,2,2,1")
    parser.add_argument("-cRankDistance", type=parseSeedParameterStr, help="Distance of ranks of cycle agents in their preference lists (must have the same type of seed size input (sSize)). [default = 1,2,2,3]", required=False, default="1,2,2,3")
    parser.add_argument("-p1", type=float, help="Probability of incompleteness [default = 0.5]", required=False, default=0.5)
    parser.add_argument("-p2", type=float, help="Probability of ties [default = 0.5]", required=False,default=0.5)
    parser.add_argument("-sym", type=parseBoolStr, help="If set to true preference lists in the instances become symmetric. [default=False]", required=False, default='False')
    parser.add_argument("-bip", type=parseBoolStr, help="If set to true generates bipartite instance (SMTI), otherwise generates non-bipartite instance (SRTI) [default=True]", required=False, default='True')
    parser.add_argument("-sat", type=parseBoolStr, help="If set to true generates a satisfiable instance, otherwise generated instance will not have a stable matching. [default=True]", required=False,  default='True')
    parser.add_argument("-ub", type=int, help="Upper bound for preference lists [default=no upper bound]", required=False, default=-1)
    parser.add_argument("-copy", type=parseBoolStr, help="If copying the same seed to combine for each instance is desired, then this should be set to true. In that case seed size must be given as single number instead of a list. [default=False]", required=False,  default='False')
    parser.add_argument("-dir", type=str, help="Directory for the generated instance files [default=GeneratedInstances\\ directory under root of the program]", required=False, default="GeneratedInstances")
    args = parser.parse_args()

    print(args)

    if args.bip and not args.sat:
        print("Not a possible request! An SMTI instance cannot be unsatisfiable.")

    else:

        if args.ub <= 0:
            args.ub = -1
        
        if args.sat: # then a satisfiable intance will be generated, so sSize, sSolution must be checked.
            assert len(args.sSize) == len(args.sSolution), "sSize and sSolution parameters are not of the same size!"
            checkInputSeedSizeValue(args.sSize, args.iSize)
            if args.copy:
                assert len(args.sSize) == 1, "There should be a single seed size in order to copy the same seed!"

            main(args)

        else: # then an unsatisfiable intance will be generated, so sSize, cSize, cAmount, cRankDistance must be checked.
            assert len(args.sSize) == len(args.cSize) and len(args.cSize) == len(args.cAmount) and len(args.cAmount) == len(args.cRankDistance),  "sSize, cSze, cAmount, cRanksDistance parameters are not of the same size!"
            checkInputSeedSizeValue(args.sSize, args.iSize)
            checkIfCyleSizeIsOdd(args.cSize)
            if args.copy:
                assert len(args.sSize) == 1, "There should be a single seed size in order to copy the same seed!"

            main(args)