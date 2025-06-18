from util.CommandExecutor import CommandExecutor
import os
from abc import ABC, abstractmethod
from util.Enums import ProblemType, SymmetryOption
from util.Seed import SAT_SRTI_Seed, UNSAT_SRTI_Seed, SMTI_Seed


class SeedGenerator(CommandExecutor):
    def __init__(self, seedSize, option_ub=-1, option_sym=SymmetryOption.NON_SYMMETRIC, option_incompProb=0.5, option_tieProb=0.5):
        super().__init__()
        self.previousInstancesFilePath = os.path.join("config", "previousInstances.lp")
        self.instanceSizeFilePath = os.path.join("config", "instanceSize.lp")
        self.option_upperBound = option_ub
        self.option_symmetry = option_sym
        self.option_incompPorb = option_incompProb
        self.option_tieProb = option_tieProb
        self.seedSize = seedSize

        self.__writeSeedSizeParameter()
        self.__writeUpperBoundParameter()
        self.__deletePreviousInstances()

    @abstractmethod
    def _getProblemType(self):
        pass

    @abstractmethod
    def _getConfigurationStr(self):
        pass

    @abstractmethod
    def _generateSeedFromProgramOutput(self, atoms):
        pass

    def __deletePreviousInstances(self):
        with open(self.previousInstancesFilePath, "w") as file:
            file.write("")

    def _addPreviousInstance(self, instanceString):
        test = None
        if self._getProblemType() == ProblemType.BIPARTITE:  # then it is SMTI instance
            def test(atom): return "wrank" in atom or "mrank" in atom
        else:
            def test(atom): return "arank" in atom

        with open(self.previousInstancesFilePath, "a") as file:
            temp = instanceString.split(" ")
            temp = [atom for atom in temp if test(atom)]
            constraintStr = ""
            for atom in temp:
                constraintStr += f"{atom}, "
            constraintStr = constraintStr[0:constraintStr.rindex(", ")] + "."
            file.write(f":- {constraintStr}\n")

    def __writeSeedSizeParameter(self):
        with open(self.instanceSizeFilePath, "w") as file:
            file.write(f"#const n = {self.seedSize}.\n")  # n = instance size

    def __writeUpperBoundParameter(self):
        if self.option_upperBound > 0:
            upperBoundValueFilePath = os.path.join("config", "upperBoundValue.lp")
            with open(upperBoundValueFilePath, "w") as file:
                file.write(f"#const m = {self.option_upperBound}.\n") # m = pref. list upperbound

    def __getOptionsString(self, optionKey):
        optionsString = " "
        if self.option_symmetry == SymmetryOption.SYMMETRIC:
            optionsString += os.path.join("config", f"{optionKey}Options", f"{optionKey}Symmetry.lp") + " "

        if self.option_upperBound > 0:
            optionsString += os.path.join("config", "upperBoundValue.lp") + " "
            optionsString += os.path.join("config", f"{optionKey}Options", f"{optionKey}UpperBound.lp") + " "

        if self.option_incompPorb <= 0:
            optionsString += os.path.join("config", f"{optionKey}Options", f"{optionKey}Complete.lp") + " "

        if self.option_tieProb <= 0:
            optionsString += os.path.join("config", f"{optionKey}Options", f"{optionKey}NoTie.lp") + " "
        elif self.option_tieProb >= 1:
            optionsString += os.path.join("config", f"{optionKey}Options", f"{optionKey}AllTie.lp") + " "

        return optionsString

    def _getOptionsString(self):
        if self._getProblemType() == ProblemType.BIPARTITE:  # Then it is SMTI seed
            return self.__getOptionsString("smti")

        else:  # Then it is SRTI seed
            return self.__getOptionsString("srti")
    
    def setSeedSize(self, seedSize):
        self.seedSize = seedSize
        self.__writeSeedSizeParameter()

    def generateSeed(self):
        output = self.runCommand()

        if output is None:
            print(f"Command could not be executed in {self.TIMEOUT_VALUE}.")
            return None
        if "UNSATISFIABLE" in output:
            print(f"Cannot generate (more) seed with this configuration: {self._getConfigurationStr()}!")
            return None
    
        lines = output.split("\n")
        answerLineIndex = next((i - 1 for i in range(0, len(lines)) if "SATISFIABLE" in lines[i]), -1)

        assert answerLineIndex != -1, "The .lp program of seed generator did not work properly!"

        answer = lines[answerLineIndex]
        atoms = answer.strip().split(" ")
        return self._generateSeedFromProgramOutput(atoms)


class SAT_SMTI_SeedGenerator(SeedGenerator):

    def __init__(self, seedSize, option_ub=-1, option_sym=SymmetryOption.NON_SYMMETRIC, option_incompProb=0.5, option_tieProb=0.5, solutionsInSeed=3):
        super().__init__(seedSize, option_ub, option_sym, option_incompProb, option_tieProb)
        self.generatorScript = os.path.join("SeedGenerationScripts", "SAT_SMTI_Seed_Generator.lp")

        self.seedSolutionsCount = solutionsInSeed
        self.seedSolutionFile = os.path.join("config", "minSeedSolutions.lp")
        self.__writeSeedSolutionParameter()

    def __writeSeedSolutionParameter(self):
        with open(self.seedSolutionFile, "w") as file:
            file.write(f"#const k = {self.seedSolutionsCount}.\n")  # k = min number of solutions in seed

    def _getConfigurationStr(self):
        return f"SAT SMTI Seed Generator: seedSize: {self.seedSize}, solutionsInSeed: {self.seedSolutionsCount}"
    
    def _getProblemType(self):
        return ProblemType.BIPARTITE

    def _getCommandString(self):
        return f"clingo {self.generatorScript} {self.instanceSizeFilePath} {self.seedSolutionFile} {self.previousInstancesFilePath} {self._getOptionsString()}"

    def _generateSeedFromProgramOutput(self, atoms):
        instanceString = ""
        solutionString = ""

        for atom in atoms:
            if "man" in atom or "wrank" in atom or "mrank" in atom:
                instanceString += atom.strip() + " "
            elif "matched" in atom or "mSingle" in atom or "wSingle" in atom:
                solutionString += atom.strip() + " "

        self._addPreviousInstance(instanceString)
        return SMTI_Seed(seedInstanceString=instanceString.strip(),
                         seedSolutionString=solutionString.strip())

    def setSolutionCountInSeed(self, seedSolutionCount):
        self.seedSolutionsCount = seedSolutionCount
        self.__writeSeedSolutionParameter()

class SAT_SRTI_SeedGenerator(SeedGenerator):

    def __init__(self, seedSize, option_ub=-1, option_sym=SymmetryOption.NON_SYMMETRIC, option_incompProb=0.5, option_tieProb=0.5, solutionsInSeed=3):
        super().__init__(seedSize, option_ub, option_sym, option_incompProb, option_tieProb)
        self.generatorScript = os.path.join("SeedGenerationScripts", "SAT_SRTI_Seed_Generator.lp")

        self.seedSolutionsCount = solutionsInSeed
        self.seedSolutionFile = os.path.join("config", "minSeedSolutions.lp")
        self.__writeSeedSolutionParameter()

    def __writeSeedSolutionParameter(self):
        with open(self.seedSolutionFile, "w") as file:
            file.write(f"#const k = {self.seedSolutionsCount}.\n")  # k = min number of solutions in seed

    def _getConfigurationStr(self):
        return f"SAT SRTI Seed Generator: seedSize: {self.seedSize}, solutionsInSeed: {self.seedSolutionsCount}"
    
    def _getProblemType(self):
        return ProblemType.NON_BIPARTITE

    def _getCommandString(self):
        return f"clingo {self.generatorScript} {self.instanceSizeFilePath} {self.seedSolutionFile} {self.previousInstancesFilePath} {self._getOptionsString()}"

    def _generateSeedFromProgramOutput(self, atoms):
        instanceString = ""
        solutionString = ""

        for atom in atoms:
            if "agent" in atom or "arank" in atom:
                instanceString += atom.strip() + " "
            elif "matched" in atom or "aSingle" in atom:
                solutionString += atom.strip() + " "

        self._addPreviousInstance(instanceString)
        return SAT_SRTI_Seed(agentData=instanceString.strip(),
                             matchingData=solutionString.strip())
    
    def setSolutionCountInSeed(self, seedSolutionCount):
        self.seedSolutionsCount = seedSolutionCount
        self.__writeSeedSolutionParameter()


class UNSAT_SRTI_SeedGenerator(SeedGenerator):

    def __init__(self, seedSize, option_ub=-1, option_sym=SymmetryOption.NON_SYMMETRIC, option_incompProb=0.5, option_tieProb=0.5, cycleSize=3, cycleCount=1, rankDistance=1):
        super().__init__(seedSize, option_ub, option_sym, option_incompProb, option_tieProb)
        self.generatorScript = os.path.join("SeedGenerationScripts", "UNSAT_SRTI_Seed_Generator.lp")

        self.cycleSizeFile = os.path.join("config", "cycleParameters", "cyceSize.lp")
        self.cycleCountFile = os.path.join("config", "cycleParameters", "cyceCount.lp")
        self.rankDistanceFile = os.path.join("config", "cycleParameters", "rankDistance.lp")

        self.cycleSize = cycleSize
        self.cycleCount = cycleCount
        self.rankDistance = rankDistance
        self.__writeCycleSize()
        self.__writeCycleCount()
        self.__writeRankDistance()

    def __writeCycleSize(self):
        with open(self.cycleSizeFile, "w") as file:
            file.write(f"#const c = {self.cycleSize}.\n")  # c = cycle size
    
    def __writeCycleCount(self):
        with open(self.cycleCountFile, "w") as file:
            file.write(f"#const a = {self.cycleCount}.\n")  # a = cycle count
    
    def __writeRankDistance(self):
        with open(self.rankDistanceFile, "w") as file:
            file.write(f"#const k = {self.rankDistance}.\n")  # k = rank distance (sticky degree)

    def _getConfigurationStr(self):
        return f"UNSAT SRTI Seed Generator: seedSize: {self.seedSize}, cycleSize: {self.cycleSize}, cycleCount: {self.cycleCount}, rankDistance: {self.rankDistance}"
    
    def _getProblemType(self):
        return ProblemType.NON_BIPARTITE

    def _getCommandString(self):
        return f"clingo {self.generatorScript} {self.instanceSizeFilePath} {self.previousInstancesFilePath} {self._getOptionsString()} {self.cycleCountFile} {self.cycleSizeFile} {self.rankDistanceFile}"

    def _generateSeedFromProgramOutput(self, atoms):
        instanceString = ""
        cycleString = ""

        for atom in atoms:
            if "agent" in atom or "arank" in atom:
                instanceString += atom.strip() + " "
            elif "cycle" in atom:
                cycleString += atom.strip() + " "

        self._addPreviousInstance(instanceString)
        return UNSAT_SRTI_Seed(seedInstanceString=instanceString.strip(),
                               seedCycleString=cycleString.strip())
    
    def setCycleSize(self, cycleSize):
        self.cycleSize = cycleSize
        self.__writeCycleSize()

    def setCycleCount(self, cycleCount):
        self.cycleCount = cycleCount
        self.__writeCycleCount()

    def setRankDistance(self, rankDistance):
        self.rankDistance = rankDistance
        self.__writeRankDistance()
