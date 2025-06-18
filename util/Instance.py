from util.Agent import *
from util.Seed import *

class Instance:
    def __init__(self, listOfSeeds : list[SRTI_Seed])->None:
        self.listOfSeeds = listOfSeeds
        self.instanceSize = sum([seed.size for seed in listOfSeeds])
        self.setOfIndividuals = []

    def __agentIDMapping(self, agentID : int, isWoman:bool):
        # takes agentID returns the ID of corresponding man or woman
        seedIndexOfAgent = None
        for i in range(len(self.listOfSeeds)):
            if agentID <= sum([int(s.size) for s in self.listOfSeeds[0:i+1]]):
                seedIndexOfAgent = i
                break
        assert seedIndexOfAgent is not None, "Could not find the seedIndexOfAgent!"
        seed = self.listOfSeeds[seedIndexOfAgent]
        totalNumberOfManUntilSeed = sum([int(s.size/2) for s in self.listOfSeeds[0:seedIndexOfAgent]])
        return agentID - ((int(isWoman))*int(seed.size/2)) - totalNumberOfManUntilSeed

    def __fillIndividualsAsSMTI(self):
        setOfMen = []
        setOfWomen = []

        for i in range(len(self.listOfSeeds)):
            seed = self.listOfSeeds[i]
            for j in range(seed.size):
                agent = seed.setOfAgents[j]
                assert agent.set != Gender.NONE, "SMTI agent does not have gender!"
                isWoman = agent.set==Gender.WOMAN 
                individual = Man(self.__agentIDMapping(agent.ID, isWoman)) if not isWoman else Woman(self.__agentIDMapping(agent.ID, isWoman))
                for r in range(len(agent.preferenceList)):
                    for prefferredAgentID in agent.preferenceList[r]:
                            ID = self.__agentIDMapping(prefferredAgentID, (not isWoman))
                            individual.addPreferredAgent(ID,r)
                if not isWoman: setOfMen.append(individual)
                else: setOfWomen.append(individual)

        for man in setOfMen:
            self.setOfIndividuals.append(man)
        for woman in setOfWomen:
            self.setOfIndividuals.append(woman)

    def __fillIndividualsAsSRTI(self):
        for seed in self.listOfSeeds:
            for agent in seed.setOfAgents:
                self.setOfIndividuals.append(agent)


    def getAsSMTI_Instance(self):
        self.__fillIndividualsAsSMTI() # this must be the first line of this function, so that setOfIndividuals is filled
        
        resultStr = f"man(1..{int(self.instanceSize/2)}).\n"
        resultStr += f"woman(1..{int(self.instanceSize/2)}).\n"
        for agent in self.setOfIndividuals:
            resultStr += agent.getAtomString()
        
        return resultStr

    def getAsSRTI_Instance(self):
        self.__fillIndividualsAsSRTI() # this must be the first line of this function, so that setOfIndividuals is filled
        
        resultStr = f"agent(1..{self.instanceSize}).\n"
        for agent in self.setOfIndividuals:
            resultStr += agent.getAtomString()
        return resultStr

    # def __init__(self, copies, seedSize):
    #     # self.instanceSize = len(copies) * len(copies[0])
    #     self.instanceSize = sum([len(seed.setOfAgents) for seed in copies])
    #     self.seedSize = seedSize
    #     self.setOfAgents = []

    #     self.__getSetOfAgentsFromCopies(copies)

    # # def __getSetOfAgentsFromCopies(self, copies):
    # #     for copy in copies:
    # #         for agent in copy:
    # #             self.setOfAgents.append(agent)
    
    # def __getSetOfAgentsFromCopies(self, copies):
    #     for seed in copies:
    #         for agent in seed.setOfAgents:
    #             self.setOfAgents.append(agent)

    # def __getAgentAsSMTIString(self, agent, atomEndChar=".\n"):
    #     s = self.seedSize # there are s amount of agents, s / 2 of them are women and s / 2 of them are men
    #     smtiStr = ""
    #     prefList = agent.getNonEmptyPreferenceList()

    #     if ((agent.ID - 1) % s) < (s / 2): # Then agent corresponds to a man!
    #         M = int(1 + (s / 2) * (int((agent.ID-1) / s)) + ((agent.ID-1) % s))
    #         # smtiStr += f"man({M}){atomEndChar}"
    #         for r in range(0, len(prefList)):
    #             for aID in prefList[r]:
    #                 W = int((s / 2) * (int((aID-1) / s)) - ((s / 2) - 1) + ((aID-1) % s))
    #                 smtiStr += f"mrank({M},{W},{r + 1}){atomEndChar}"
    #     else: # Then agent corresponds to a woman!
    #         W = int((s / 2) * (int((agent.ID-1) / s)) - ((s / 2) - 1) + ((agent.ID-1) % s))
    #         # smtiStr += f"woman({W}){atomEndChar}"
    #         for r in range(0, len(prefList)):
    #             for aID in prefList[r]:
    #                 M = int(1 + (s / 2) * (int((aID-1) / s)) + ((aID-1) % s))
    #                 smtiStr += f"wrank({W},{M},{r + 1}){atomEndChar}"
        
    #     return smtiStr
    
    # def getAsSMTI_Instance(self):
    #     resultStr = f"man(1..{int(self.instanceSize/2)}).\n"
    #     resultStr += f"woman(1..{int(self.instanceSize/2)}).\n"
    #     for agent in self.setOfAgents:
    #         resultStr += self.__getAgentAsSMTIString(agent=agent)
        
    #     return resultStr
        
    # def getAsSRTI_Instance(self):
    #     resultStr = f"agent(1..{self.instanceSize}).\n"
    #     for agent in self.setOfAgents:
    #         resultStr += agent.getAtomString()
    #     return resultStr