from util.Agent import *
from abc import ABC, abstractmethod

class Cycle:
    def __init__(self) -> None:
        self.cycle = [] # list of Agent IDs
    
    def __init__(self, listOfAgentIDs) -> None:
        self.cycle = listOfAgentIDs # list of Agent IDs
    
    def addAgentToCycle(self, agentID):
        self.cycle.append(agentID)

    def getCycle(self):
        return self.cycle
    
    def isAgentInCycle(self, agentID):
        return agentID in self.cycle
    
    def renameCycle(self, incrementAmount):
        for i in range(len(self.cycle)):
            self.cycle[i] += incrementAmount
    
    def getWorstRankedPartner(self, agent : Agent):
        worstRank = -1
        worstRankedPartnerID = -2

        for cycleAgentID in self.cycle:
            if agent.isPreferAgent(cycleAgentID): # then agent preferes an agent(cycleAgentID) from cycle
                rankOfCycleAgent = agent.getRankOfPreferredAgent(cycleAgentID)
                if rankOfCycleAgent > worstRank:
                    worstRank = rankOfCycleAgent
                    worstRankedPartnerID = cycleAgentID

        return worstRank, worstRankedPartnerID

    def __str__(self) -> str:
        return f"Cycle: {self.cycle}"
    
    def __repr__(self) -> str:
        return self.__str__()


class Matching(ABC):
    def __init__(self):
        self.matching = []

    def addPair(self, agentID1=None, agentID2=None):  # if agent is None, then the other agent is single
        self.matching.append((agentID1, agentID2))

    def getMatching(self):
        return self.matching

    def isPairExist(self, pair):
        return pair in self.matching
    
    @abstractmethod
    def _getMatchedPartnerID(self, agent : Agent, pair : tuple):
        pass

    @abstractmethod
    def _checkIfAgentInPair(self, agent : Agent, pair : tuple) -> bool:
        pass
    
    def getWorstRankedPartner(self, agent : Agent):
        worstRank = -1
        worstRankedPartnerID = None

        for pair in self.matching:
            if self._checkIfAgentInPair(agent, pair):
                matchedAgentID = self._getMatchedPartnerID(agent, pair)

                if matchedAgentID is None: # then agentID is single in one matching
                    return float('inf'), -1
                
                rankOfMatchedAgent = agent.getRankOfPreferredAgent(matchedAgentID) # 0-based rank
                if rankOfMatchedAgent > worstRank:
                    worstRank = rankOfMatchedAgent
                    worstRankedPartnerID = matchedAgentID

        return worstRank, worstRankedPartnerID

    def __str__(self):
        return f"Matching: {self.matching}"
    def __repr__(self):
         return self.__str__()
    

class Marriage(Matching):
    def __init__(self):
        super().__init__()
    
    def _getMatchedPartnerID(self, agent : Agent, pair : tuple):
        return pair[int(isinstance(agent,Man))] # pair is a tuple of (Man, Woman)
    
    def _checkIfAgentInPair(self, agent : Agent, pair : tuple):
        if isinstance(agent,Man): 
            return pair[0] == agent.ID
        elif isinstance(agent, Woman):
            return pair[1] == agent.ID
        else:
            raise RuntimeError("There is an agent in marriage that is neither a man nor a woman!")

    
    def toRoommates(self,seedSize): # seed size is simply the size of men. It will be used to rename the IDs of women in the matching. This parameter will be passed from the seed class. 
        roommateMatching = Roommates()
        for pair in self.matching: # pair is a tuple of (Man, Woman)
            if pair[1] is None: # then man (pair[0]) is single 
                roommateMatching.addPair(pair[0], None)
            elif pair[0] is None: # then woman (pair[1]) is single
                roommateMatching.addPair(pair[1] + seedSize, None)
            else: # then none of them is single
                roommateMatching.addPair(pair[0], pair[1] + seedSize)
        return roommateMatching


    
class Roommates(Matching):
    def __init__(self):
        super().__init__()
    
    def _getMatchedPartnerID(self, agent : Agent, pair : tuple):
        return pair[1-pair.index(agent.ID)] # pair is a tuple of (Agent, Agent)

    def _checkIfAgentInPair(self, agent : Agent, pair : tuple):
        return  agent.ID in pair # # pair is a tuple of (Agent, Agent) and an agent cannot be matched with itself