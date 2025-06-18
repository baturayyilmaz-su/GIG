from util.Enums import *
from util.SeedGenerator import UNSAT_SRTI_SeedGenerator, SAT_SRTI_SeedGenerator, SAT_SMTI_SeedGenerator
from util.Seed import SAT_SRTI_Seed, SMTI_Seed, UNSAT_SRTI_Seed
from util.Instance import Instance
from util.SeedCombiningProcedure import *
from copy import deepcopy
import sys
import os
import time
import traceback

class GIG:
    def __init__(self, instCount, instSize, seedSizes, solutionCounts, cycleSizes, cycleCounts, cycleRankDistances, p1, p2, upBound, sat, symOpt, bipartite, instFilePath, copySeed) -> None:
        self.instCount = instCount
        self.instSize = instSize
        self.seedSizes = seedSizes
        self.solutionCounts = solutionCounts
        self.cycleSizes = cycleSizes
        self.cycleCounts = cycleCounts
        self.cycleRankDistances = cycleRankDistances
        self.p1 = p1
        self.p2 = p2
        self.upBound = upBound
        self.sat = sat
        self.symOpt = symOpt
        self.bipartite = bipartite
        self.instFilePath = instFilePath
        self.copySeed = copySeed

        self.__handleParameterLists()
        self.seedGenerator = self.__getRespectiveSeedGenerator()

    def __handleParameterLists(self):
        if len(self.seedSizes) == 1:
            amountOfSeedsRequires = int(self.instSize / self.seedSizes[0])

            for i in range(0, amountOfSeedsRequires-1):
                self.seedSizes.append(self.seedSizes[0])

                if self.sat == Satisfiability.SATISFIABLE:
                    self.solutionCounts.append(self.solutionCounts[0])
                else: # self.sat == Satisfiability.UNSATISFIABLE:
                    self.cycleSizes.append(self.cycleSizes[0])
                    self.cycleCounts.append(self.cycleCounts[0])
                    self.cycleRankDistances.append(self.cycleRankDistances[0])


    def __getRespectiveSeedGenerator(self):
        if self.bipartite == ProblemType.BIPARTITE:
            return SAT_SMTI_SeedGenerator(self.seedSizes[0], self.upBound, self.symOpt, self.p1, self.p2, self.solutionCounts[0])

        elif self.bipartite == ProblemType.NON_BIPARTITE and self.sat == Satisfiability.SATISFIABLE:
            return SAT_SRTI_SeedGenerator(self.seedSizes[0], self.upBound, self.symOpt, self.p1, self.p2, self.solutionCounts[0])
        
        elif self.bipartite == ProblemType.NON_BIPARTITE and self.sat == Satisfiability.UNSATISFIABLE:
            return UNSAT_SRTI_SeedGenerator(self.seedSizes[0], self.upBound, self.symOpt, self.p1, self.p2, self.cycleSizes[0], self.cycleCounts[0], self.cycleRankDistances[0])
        
        else:
            raise RuntimeError(f"Illegal set of arguments bipartite option is {self.bipartite} and satisfiablity is {self.sat}")

    def __generateSeeds(self):
        seedList = []

        for i in range(len(self.seedSizes)):
            if i == 0 or not self.copySeed: # if it is not the first iteration and the copying seed option is selected, no new seed is generated. The same one will be appended
                self.seedGenerator.setSeedSize(self.seedSizes[i])
                if self.sat == Satisfiability.SATISFIABLE:
                    self.seedGenerator.setSolutionCountInSeed(self.solutionCounts[i])
                else:
                    self.seedGenerator.setCycleCount(self.cycleCounts[i])
                    self.seedGenerator.setCycleSize(self.cycleSizes[i])
                    self.seedGenerator.setRankDistance(self.cycleRankDistances[i])
            
                seed = self.seedGenerator.generateSeed()
            
            if self.copySeed:
                seedList.append(deepcopy(seed))
            else:
                seedList.append(seed)

        return seedList

    def __generateInstances(self):
        startTime = time.time()
        L = []
        ub = sys.maxsize if self.upBound == -1 else self.upBound
    
        for _ in range(self.instCount):
            try:
                seedList = self.__generateSeeds()
                seedCombiner = SeedCombiningProcedure(seedList, self.bipartite, self.p1, self.p2, ub, self.symOpt, self.sat)
                instance = seedCombiner.combineSeeds()

                if self.bipartite == ProblemType.BIPARTITE:
                    L.append(instance.getAsSMTI_Instance())
                elif self.bipartite == ProblemType.NON_BIPARTITE:
                    L.append(instance.getAsSRTI_Instance())
            except:
                print("A problem occured during instance generation!")
                traceback.print_exc()
                break

        endTime = time.time()
        return L, endTime - startTime

    def generateInstances(self):
        instanceSet, duration = self.__generateInstances()

        print(f"Generating instances took: {(duration)}s")
    
        for i in range(0, len(instanceSet)):
            outputFileName = f"instance_p1_{self.p1:.2f}_p2_{self.p2:.2f}_n_{self.instSize}_{i:02d}.lp"
            outputFilePath = os.path.join(self.instFilePath, outputFileName)
            with open(outputFilePath, "w") as instanceFile:
                instanceFile.write(instanceSet[i])
                
        print(f"({len(instanceSet)}) instances are written!")


            
            