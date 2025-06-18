from util.Enums import Gender
from copy import deepcopy
from collections import deque
import random

class Agent:
    def __init__(self, ID):
        self.ID = ID
        self.set = Gender.NONE
        self.preferenceList = deque()
        self.worstRankedAgentID = None # should be the ID of the worst ranked agent.

    def __extendPreferenceList(self, rank):
        diff = rank - (len(self.preferenceList) - 1)
        if diff > 0:
            self.preferenceList.extend([[] for _ in range(0,diff)]) # adding diff many empty lists to preference list 

    def addPreferredAgent(self, agentID, rank): # rank is used as 0-based index
        self.__extendPreferenceList(rank)
        self.preferenceList[rank].append(agentID)
    
    def __notifyWorstRank(self, agentID, rankOfAgent):
        assert self.worstRankedAgentID is not None, "Unhandled worstRankedAgentID!!"
        if self.worstRankedAgentID == -2:
            self.worstRankedAgentID = agentID

        elif self.getRankOfPreferredAgent(self.worstRankedAgentID) < rankOfAgent: # then agentID is a worse than worstRank
            self.worstRankedAgentID = agentID

    def getRankOfWortRankedPartner(self):
        if self.worstRankedAgentID == -1 or self.worstRankedAgentID == -2:
            return self.worstRankedAgentID
        else:
            return self.getRankOfPreferredAgent(self.worstRankedAgentID)
        
    def getRandomRank(self, tie, rank=None):
        if rank == len(self.preferenceList) and tie: # this case is used for preserving cycles only! It is not used when generating satisfiable intances.
            return None
        elif rank == len(self.preferenceList) and not tie:
            return rank
        
        if rank is None and tie:
            return random.randint(0,len(self.preferenceList)-1)
        elif rank is None and not tie:
            return random.randint(0,len(self.preferenceList))
        elif rank is not None and tie:
            return random.randint(rank,len(self.preferenceList)-1)
        else:# rank is not None and not tie:
            return random.randint(rank+1,len(self.preferenceList))

    def addAgentToRandomRank(self, agentID, tie, randomRank=None, notifyWorstRank=False):
        if randomRank == None:
            return
        
        if not tie:
            self.preferenceList.insert(randomRank, [agentID])
            if notifyWorstRank: self.__notifyWorstRank(agentID, randomRank)
        else:
            self.preferenceList[randomRank].append(agentID)
            if notifyWorstRank: self.__notifyWorstRank(agentID, randomRank)

    def __getFlattenedPreferrenceList(self):
        return [item for sublist in self.preferenceList for item in sublist]

    def getNumberOfPreferredAgent(self):
        count = 0
        for rank in self.preferenceList:
            for agent in rank:
                count += 1
        return count

    def getRankOfPreferredAgent(self, preferredAgentID : int):
        for r in range(0, len(self.preferenceList)):
            if preferredAgentID in self.preferenceList[r]:
                return r
        return None  # indicating that prefferedAgentID is not preferred by this agent
    
    def isPreferAgent(self, agentID : int):
        fList = self.__getFlattenedPreferrenceList()
        return agentID in fList
    
    def renameAgent(self, incrementAmount):
        self.ID += incrementAmount
        for r in range(len(self.preferenceList)):
            for i in range(len(self.preferenceList[r])):
                self.preferenceList[r][i] += incrementAmount
        if self.worstRankedAgentID != -1 and self.worstRankedAgentID != -2: 
            self.worstRankedAgentID += incrementAmount


    def getAtomString(self, atomEndChar=".\n"):
        agentStr = ""
        prefList = self.preferenceList
        assert [] not in prefList, "There is an empty rank in the preference list of agent!"
        
        for r in range(0, len(prefList)):
            for agentID in prefList[r]:
                agentStr += f"arank({self.ID},{agentID},{r + 1}){atomEndChar}"

        return agentStr

    def __eq__(self, other):
        return self.ID == other.ID

    def __ne__(self, other):
        return self.ID != other.ID
    
    def __str__(self):
       return f"{self.set}_{self.ID} : {self.preferenceList} | worstRankedAgentID: {self.worstRankedAgentID}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Man(Agent):
    def __init__(self, ID):
        super().__init__(ID)
        self.set = Gender.MAN

    def toSRTIAgent(self, seedSize):
        agent = Agent(self.ID)
        agent.set = Gender.MAN # this information will be used when combining seeds for SMTI
        
        assert self.worstRankedAgentID is not None, "Worst ranked agent is not set before converting to SRTI agent!"
        if self.worstRankedAgentID != -1: # Note that Man and Woman objects cannot have worstRankedAgentID as -2, beacuse it is related with cycles only!
            agent.worstRankedAgentID = self.worstRankedAgentID + seedSize
        else:
            agent.worstRankedAgentID = -1

        for r in range(len(self.preferenceList)):
            for womanID in self.preferenceList[r]:
                agent.addPreferredAgent(womanID+seedSize, r)
        return agent

    def getAtomString(self, atomEndChar=".\n"):
        manStr = ""
        prefList = self.preferenceList
        assert [] not in prefList, "There is an empty rank in the preference list of man!"

        for r in range(0, len(prefList)):
            for womanID in prefList[r]:
                manStr += f"mrank({self.ID},{womanID},{r + 1}){atomEndChar}"
        
        return manStr


class Woman(Agent):
    def __init__(self, ID):
        super().__init__(ID)
        self.set = Gender.WOMAN

    def toSRTIAgent(self, seedSize):
        agent = Agent(self.ID+seedSize)
        agent.set = Gender.WOMAN # this information will be used when combining seeds for SMTI
        
        assert self.worstRankedAgentID is not None, "Worst ranked agent is not set before converting to SRTI agent!"
        agent.worstRankedAgentID = self.worstRankedAgentID # Note that Man and Woman objects cannot have worstRankedAgentID as -2, beacuse it is related with cycles only!

        for r in range(len(self.preferenceList)):
            for manID in self.preferenceList[r]:
                agent.addPreferredAgent(manID, r)
        return agent

    def getAtomString(self, atomEndChar=".\n"):
        womanStr = ""
        prefList = self.preferenceList
        assert [] not in prefList, "There is an empty rank in the preference list of man!"

        for r in range(0, len(prefList)):
            for manID in prefList[r]:
                womanStr += f"wrank({self.ID},{manID},{r + 1}){atomEndChar}"
        
        return womanStr