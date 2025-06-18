from util.Enums import ProblemType, SymmetryOption, Gender, Satisfiability
from util.Seed import *
from util.Agent import *
from util.Instance import Instance
import random

class SeedCombiningProcedure:
    def __init__(self, listOfSeeds : list[SRTI_Seed], bipartiteOpt, P1, P2, upperBound, symmetryOption, satisfiability) -> None:
        self.listOfSeeds = listOfSeeds
        self.bipartiteOpt = bipartiteOpt
        self.P1 = P1
        self.P2 = P2
        self.upperBound = upperBound
        self.symmetryOption = symmetryOption
        self.satisfiablitiy = satisfiability

        if self.bipartiteOpt == ProblemType.BIPARTITE:
            self.__castSeedsToSRTI()

    def __castSeedsToSRTI(self):
        result = []
        for seed in self.listOfSeeds:
            srtiSeed = seed.toSRTISeed()
            result.append(srtiSeed)
        self.listOfSeeds = result

    def __renameSeeds(self):
        for i in range(len(self.listOfSeeds)):
            if i!=0:
                totalSizeOfPrevSeeds = sum([int(s.size) for s in self.listOfSeeds[0:i]])
                seed = self.listOfSeeds[i]
                seed.renameAgents(totalSizeOfPrevSeeds)

    def __checkBipartiteOption(self, agent_i : Agent, agent_j : Agent):
        if self.bipartiteOpt == ProblemType.NON_BIPARTITE: 
            return True
        else:
            assert agent_i.set != Gender.NONE, "SMTI agent (man or woman) does not have gender after converted to SRTI agent!"
            assert agent_j.set != Gender.NONE, "SMTI agent (man or woman) does not have gender after converted to SRTI agent!"
            return agent_i.set != agent_j.set
        
    def __checkPrefList(self, agent_i : Agent, agent_j : Agent):
        return agent_j.getNumberOfPreferredAgent() < self.upperBound and not agent_j.isPreferAgent(agent_i.ID)
    
    def __chekSymmetricPrefList(self, agent_i : Agent):
        return self.symmetryOption == SymmetryOption.SYMMETRIC and agent_i.getNumberOfPreferredAgent() >= self.upperBound
    
    def __checkIfAgentRequiresNotification(self, agent : Agent):
        if self.satisfiablitiy != Satisfiability.UNSATISFIABLE:
            return False # notification is done for cycle agents only
        for seed in self.listOfSeeds:
            for cycle in seed.listOfCycles:
                if cycle.isAgentInCycle(agent.ID):
                    return True
        
        return False

    def __solutionPreservingAddition(self, agent_1 : Agent, agent_2 : Agent, toTie : bool, mutAdd : bool, preserveCycle : bool):
        r1 = agent_1.getRankOfWortRankedPartner() + int(preserveCycle) # they cannot be even in a tie with a cycle agent, so we add 1
        r2 = agent_2.getRankOfWortRankedPartner() + int(preserveCycle) # they cannot be even in a tie with a cycle agent, so we add 1

        if not preserveCycle: assert r1 != -2, "Cycle is involved in stable matching!"
        if not preserveCycle: assert r2 != -2, "Cycle is involved in stable matching!"
        if preserveCycle: assert r1 != 0, "Stable matching is involved in cycle!" # if agent does not have a cycle agent in its list, it is denoted with -2, and in this case it should not have -1 as its worstRankedPartnerID
        if preserveCycle: assert r2 != 0, "Stable matching is involved in cycle!" # if agent does not have a cycle agent in its list, it is denoted with -2, and in this case it should not have -1 as its worstRankedPartnerID

        rank_1 = -1 # random rank in agent_2's list (for agent_1)
        rank_2 = -1 # random rank in agent_1's list (for agent_2)

        if (r1 == -1 and r2 == -1) or (r2 == -1 and agent_1.getRankOfPreferredAgent(agent_2.ID) < r1): 
            if preserveCycle: # then none of the agents contains a cycle agent, addition can be done randomly
                rank_1 = agent_2.getRandomRank(tie=toTie, rank=None)
                if mutAdd: rank_2 = agent_1.getRandomRank(tie=toTie, rank=None)
            else: # then both of agents are single in a matching, they cannot be acceptable
                return
            
        elif r1 != -1 and r2 == -1:
            rank_1 = agent_2.getRandomRank(tie=toTie, rank=None)
            if mutAdd: rank_2 = agent_1.getRandomRank(tie=toTie, rank=r1)
        
        elif r1 == -1 and r2 != -1:
            rank_1 = agent_2.getRandomRank(tie=toTie, rank=r2)
            if mutAdd: rank_2 = agent_1.getRandomRank(tie=toTie, rank=None)
        else:
            rank_1 = agent_2.getRandomRank(tie=toTie, rank=r2)
            if mutAdd: rank_2 = agent_1.getRandomRank(tie=toTie, rank=r1)
        
        assert rank_1 != -1, "There is a problem when choosing random ranks"
        if mutAdd: assert rank_2 != -1, "There is a problem when choosing random ranks"

        if mutAdd and rank_1 is not None and rank_2 is not None:
            agent_1.addAgentToRandomRank(agentID=agent_2.ID, tie=toTie, randomRank=rank_2, notifyWorstRank=self.__checkIfAgentRequiresNotification(agent_2))
            agent_2.addAgentToRandomRank(agentID=agent_1.ID, tie=toTie, randomRank=rank_1, notifyWorstRank=self.__checkIfAgentRequiresNotification(agent_1))
        elif not preserveCycle and not mutAdd and rank_1 is not None and ((r2 == -1 and agent_1.getRankOfPreferredAgent(agent_2.ID) >= r1)):
            # if mutAdd is false, then agent_2 is already in the preference list of agent_1, then we need to gurantee the followings (when we are trying to preserve matchings):
            # * agent_1 (res. agent_2) will not be interested in agent_2 (res. agent_1) even if they become acceptable
            agent_2.addAgentToRandomRank(agentID=agent_1.ID, tie=toTie, randomRank=rank_1, notifyWorstRank=self.__checkIfAgentRequiresNotification(agent_1))
        elif preserveCycle and not mutAdd and rank_1 is not None and ((r1 == -1 or agent_1.getRankOfPreferredAgent(agent_2.ID) > r1) and (r2 == -1 or rank_1 > r2)):
            # if mutAdd is true, then agent_2 is already in the preference list of agent_1, then we need to gurantee the followings (when we are trying to preserve cycles):
            # * (agent_1,agent_2) argument should not attack the cycle. So, both of them should precede a cycle agent in each others preference list (if there is a cycle agent in that list).
            agent_2.addAgentToRandomRank(agentID=agent_1.ID, tie=toTie, randomRank=rank_1, notifyWorstRank=self.__checkIfAgentRequiresNotification(agent_1))

    def combineSeeds(self) -> Instance:
        self.__renameSeeds()

        for i in range(len(self.listOfSeeds)):
            for j in range(len(self.listOfSeeds)):
                if i != j:
                    seed_i = self.listOfSeeds[i]
                    seed_j = self.listOfSeeds[j]

                    for agent_i in seed_i.setOfAgents:
                        for agent_j in seed_j.setOfAgents:
                            if self.__checkBipartiteOption(agent_i, agent_j) and self.__checkPrefList(agent_i,agent_j):
                                
                                if self.__chekSymmetricPrefList(agent_i):
                                    continue

                                r1 = random.uniform(0,1)
                                r2 = random.uniform(0,1)

                                if r1 > self.P1:
                                    if not agent_i.isPreferAgent(agent_j.ID):
                                        if self.symmetryOption == SymmetryOption.NON_SYMMETRIC:
                                            rank = agent_j.getRandomRank(tie=(r2<self.P2))
                                            agent_j.addAgentToRandomRank(agent_i.ID, tie=(r2<self.P2), randomRank=rank, notifyWorstRank=self.__checkIfAgentRequiresNotification(agent_i))
                                        else:
                                            self.__solutionPreservingAddition(agent_i, agent_j, (r2<self.P2), True, self.satisfiablitiy==Satisfiability.UNSATISFIABLE)
                                    else:
                                        self.__solutionPreservingAddition(agent_i, agent_j, (r2<self.P2), False, self.satisfiablitiy==Satisfiability.UNSATISFIABLE)
        
        return Instance(self.listOfSeeds)
