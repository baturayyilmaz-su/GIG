from util.Agent import *
from util.SeedSolutions import *

class SMTI_Seed:
    def __init__(self, seedInstanceString : str, seedSolutionString : str):
        self.size = -1  # number of woman (or man)
        self.setOfMen = [] # list of Man objects 
        self.setOfWomen = [] # list of Woman objects
        self.listOfMatchings = [] # list Marriage objects

        self.__parseInstanceString(seedInstanceString=seedInstanceString)
        self.__parseSolutionString(seedSolutionString=seedSolutionString)
        self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled

    def __parseInstanceString(self, seedInstanceString : str):
        numberOfWoman = -1
        numberOfMan = -1

        atoms = seedInstanceString.strip().split(" ") # getting atoms list
        # getting size from the seed
        for atom in atoms:
            if "woman" in atom: # this must be checked before "man" since "man" is also included in "woman"
                W = int(atom.split("(")[1].strip().split(")")[0]) # gets W from "woman(W)"
                if W > numberOfWoman:
                    numberOfWoman = W
            elif "man" in atom:
                M = int(atom.split("(")[1].strip().split(")")[0]) # gets M from "man(M)"
                if M > numberOfMan:
                    numberOfMan = M

        assert numberOfWoman == numberOfWoman, "Number of men and women are not equal in the instance"
        self.size = numberOfWoman

        for atom in atoms:
            if "mrank" in atom:
                M = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets M from "mrank(M,W,R)"
                W = int(atom.strip().split(",")[1].strip()) # gets W from "mrank(M,W,R)"
                R = int(atom.strip().split(",")[2].strip().split(")")[0]) # gets R from "mrank(M,W,R)"
                
                man = self.__getManFromTheSet(manID=M) # retrieve the man object from the setOfMen
                if man is not None:
                    man.addPreferredAgent(W, R-1)
                else:
                    man = Man(M)
                    man.addPreferredAgent(W,R-1)
                    self.setOfMen.append(man)
                
            elif "wrank" in atom:
                W = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets W from "wrank(W,M,R)"
                M = int(atom.strip().split(",")[1].strip()) # gets M from "wrank(W,M,R)"
                R = int(atom.strip().split(",")[2].strip().split(")")[0]) # gets R from "wrank(W,M,R)"
                
                woman = self.__getWomanFromTheSet(womanID=W)
                if woman is not None:
                    woman.addPreferredAgent(M, R-1)
                else:
                    woman = Woman(W)
                    woman.addPreferredAgent(M,R-1)
                    self.setOfWomen.append(woman)

    def __parseSolutionString(self, seedSolutionString : str):
        atoms = seedSolutionString.strip().split(" ")

        for atom in atoms:
            if "matched" in atom: #   atoms
                M = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets M from "matched(M,W,I)"
                W = int(atom.strip().split(",")[1].strip()) # gets W from "matched(M,W,I)"
                I = int(atom.strip().split(",")[2].strip().split(")")[0]) # gets I from "matched(M,W,I)"

                if len(self.listOfMatchings) < I:
                    for _ in range(0, I - len(self.listOfMatchings)):
                        self.listOfMatchings.append(Marriage())
                self.listOfMatchings[I-1].addPair(M,W)

            elif "mSingle" in atom:
                M = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets M from "mSingle(M,I)"
                I = int(atom.strip().split(",")[1].strip().split(")")[0]) # gets I from "mSingle(M,I)"
                if len(self.listOfMatchings) < I:
                    for _ in range(0, I - len(self.listOfMatchings)):
                        self.listOfMatchings.append(Marriage())
                self.listOfMatchings[I-1].addPair(M, None)

            elif "wSingle" in atom:
                W = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets W from "wSingle(W,I)"
                I = int(atom.strip().split(",")[1].strip().split(")")[0]) # gets I from "wSingle(W,I)"
                if len(self.listOfMatchings) < I:
                    for _ in range(0, I - len(self.listOfMatchings)):
                        self.listOfMatchings.append(Marriage())
                self.listOfMatchings[I-1].addPair(None, W)

    def __getManFromTheSet(self, manID : int) -> Agent:
        # returns man with ID manID, None if manID does not exist in the setOfMen
        return next((man for man in self.setOfMen if man.ID == manID), None)
    
    def __getWomanFromTheSet(self, womanID : int) -> Agent:
        # returns woman with ID womanID, None if womanID does not exist in the setOfWomen
        return next((woman for woman in self.setOfWomen if woman.ID == womanID), None) 
    
    def __assignWorstRankedPartners(self, agent : Agent):
        results = []
        for marriage in self.listOfMatchings:
            worstRank, worstRankedPartnerID = marriage.getWorstRankedPartner(agent=agent)
            results.append((worstRank, worstRankedPartnerID))
        results.sort(reverse=True) # sorts tuples (by default) by using the first item in each tuple 
        worstRankedID = results[0][1]
        agent.worstRankedAgentID = worstRankedID

    def __handleWorstRanksOfAgents(self):
        for man in self.setOfMen:
            self.__assignWorstRankedPartners(man)
        for woman in self.setOfWomen:
            self.__assignWorstRankedPartners(woman)
            
    def toSRTISeed(self):
        setOfAgents = []
        listOfMatchings = []

        for man in self.setOfMen:
            setOfAgents.append(man.toSRTIAgent(self.size))
        for woman in self.setOfWomen:
            setOfAgents.append(woman.toSRTIAgent(self.size))

        for marriage in self.listOfMatchings:
            roommates = marriage.toRoommates(self.size)
            listOfMatchings.append(roommates)
        
        return SAT_SRTI_Seed(agentData=setOfAgents, matchingData=listOfMatchings)



class SRTI_Seed:
    def __init__(self, agentData) -> None:
        if isinstance(agentData,list):
            self.size = len(agentData)  # number of agents (number of man + number of women)
            self.setOfAgents = agentData

        elif isinstance(agentData, str):
            self.size = -1  # number of agents (number of man + number of women)
            self.setOfAgents = []
            self.__parseInstanceString(seedInstanceString=agentData)

    # def __init__(self, setOfAgents : list[Agent]) -> None:
    #     self.size = len(setOfAgents)  # number of agents (number of man + number of women)
    #     self.setOfAgents = setOfAgents

    # def __init__(self,seedInstanceString : str) -> None:
    #     self.size = -1  # number of agents (number of man + number of women)
    #     self.setOfAgents = []

    #     self.__parseInstanceString(seedInstanceString=seedInstanceString)

    def __parseInstanceString(self, seedInstanceString):
        n = -1

        atoms = seedInstanceString.strip().split(" ") # getting atoms list
        # getting n from the seed
        for atom in atoms:
            if "agent" in atom:
                A = int(atom.split("(")[1].strip().split(")")[0]) # gets A from "agent(A)"
                if A > n:
                    n = A

        assert n != -1, "There is no agent(A) atom in the seed string"
        self.size = n

        # filling setOfAgents
        for atom in atoms:
            if "arank" in atom: # it is a preference of an agent
                A1 = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets A1 from arank(A1 , A2 ,R)
                A2 = int(atom.strip().split(",")[1].strip()) # gets A2 from arank(A1,A2,R)
                R = int(atom.strip().split(",")[2].strip().split(")")[0]) # gets R from arank(A1,A2, R)

                agent = self.__getAgentFromTheSet(agentID=A1) # retrieve the agent object from the setOfAgents
                if agent is not None:
                    agent.addPreferredAgent(A2, R-1)
                else:
                    agent = Agent(A1)
                    agent.addPreferredAgent(A2, R-1)
                    self.setOfAgents.append(agent)

    def __getAgentFromTheSet(self, agentID : int) -> Agent:
        # returns agent with ID agentID, None if agentID does not exist in the setOfAgents
        return next((agent for agent in self.setOfAgents if agent.ID == agentID), None)

    def renameAgents(self, totalSizeOfPrevSeeds):
        for agent in self.setOfAgents:
            agent.renameAgent(totalSizeOfPrevSeeds)


class SAT_SRTI_Seed(SRTI_Seed):
    def __init__(self, agentData, matchingData) -> None:
        if isinstance(agentData, list) and isinstance(matchingData, list):
            super().__init__(agentData)
            self.listOfMatchings = matchingData # list of roommates
            # The function below is not necessary in here. Since this constructor is used only for casting from SMTI instance, where worstRanks are already assigned and updated
            # self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled
        elif isinstance(agentData, str) and isinstance(matchingData, str):
            super().__init__(agentData)
            self.listOfMatchings = []
            self.__parseSolutionString(seedSolutionString=matchingData)
            self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled
        else:
            raise RuntimeError(f"Unsupported data types for agentData ({type(agentData)}) and matchingData ({type(matchingData)})")

    # def __init__(self, setOfAgents, listOfMatchings) -> None:
    #     super().__init__(setOfAgents)
    #     self.listOfMatchings = listOfMatchings # list of roommates
    #     # The function below is not necessary in here. Since this constructor is used only for casting from SMTI instance, where worstRanks are already assigned and updated
    #     # self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled

    # def __init__(self, seedInstanceString, seedSolutionString) -> None:
    #     super().__init__(seedInstanceString)
    #     self.listOfMatchings = []
    #     self.__parseSolutionString(seedSolutionString=seedSolutionString)
    #     self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled

    def __parseSolutionString(self, seedSolutionString):
        atoms = seedSolutionString.strip().split(" ") # getting atoms list
        # filling listOfMatchings
        for atom in atoms:
            if "matched" in atom:
                A1 = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets A1 from matched(A1,A2,I)
                A2 = int(atom.strip().split(",")[1].strip()) # gets A2 from matched(A1,A2,I)
                I = int(atom.strip().split(",")[2].strip().split(")")[0]) # gets I from matched(A1,A2,I)
                
                matchedTuple = (A1,A2) if A1 < A2 else (A2,A1)
                if len(self.listOfMatchings) < I:
                    for _ in range(0, I - len(self.listOfMatchings)):
                        self.listOfMatchings.append(Roommates())
                self.listOfMatchings[I-1].addPair(matchedTuple[0], matchedTuple[1])

            elif "aSingle" in atom:
                A = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets A from aSingle(A,I)
                I = int(atom.strip().split(",")[1].strip().split(")")[0]) # gets I from aSingle(A, I)
                
                if len(self.listOfMatchings) < I:
                    for _ in range(0, I - len(self.listOfMatchings)):
                        self.listOfMatchings.append(Roommates())
                self.listOfMatchings[I-1].addPair(A, None)

    def __assignWorstRankedPartners(self, agent : Agent):
        results = []
        for rommates in self.listOfMatchings:
            worstRank, worstRankedPartnerID = rommates.getWorstRankedPartner(agent=agent)
            results.append((worstRank, worstRankedPartnerID))
        results.sort(reverse=True) # sorts tuples (by default) by using the first item in each tuple 
        worstRankedID = results[0][1]
        agent.worstRankedAgentID = worstRankedID

    def __handleWorstRanksOfAgents(self):
        for agent in self.setOfAgents:
            self.__assignWorstRankedPartners(agent)


class UNSAT_SRTI_Seed(SRTI_Seed):
    def __init__(self, seedInstanceString, seedCycleString) -> None:
        super().__init__(seedInstanceString)
        self.listOfCycles = []

        self.__parseCycleString(seedCycleString=seedCycleString)
        self.__handleWorstRanksOfAgents() # this function should be called after listOfMatchings is filled

    def __constructListOfCycles(self, cycleTuples : list[tuple]):
        RESULT = [[]]
        end = False
        i = 0
        counter = 0
        while not end:
            updateOccured = False
            cycle = RESULT[i]
            agentsThatPlacedInCycle = [item for sublist in RESULT[0:i] for item in sublist]

            for tupple in cycleTuples:
                agentID_1 = tupple[0]
                agentID_2 = tupple[1]

                if agentID_1 in agentsThatPlacedInCycle or agentID_2 in agentsThatPlacedInCycle:
                    continue

                if cycle == []:
                    cycle.append(agentID_1)
                    cycle.append(agentID_2)
                    updateOccured = True
                    counter = 0
                
                else:
                    if agentID_1 in cycle and agentID_2 not in cycle:
                        cycle.append(agentID_2)
                        updateOccured = True
                        counter = 0
                    elif agentID_1 not in cycle and agentID_2 in cycle:
                        cycle.append(agentID_1)
                        updateOccured = True
                        counter = 0
            
            if not updateOccured:
                RESULT.append([])
                i += 1 # no update occured, then we can start checking for a new cycle
                counter += 1

            if counter == 2: # if two consecutive non update occurs then it should end
                end=True

        RESULT = [cycle for cycle in RESULT if cycle != []]
        for cycle in RESULT:
            self.listOfCycles.append(Cycle(cycle))
        
    def __parseCycleString(self, seedCycleString):
        atoms = seedCycleString.strip().split(" ") # getting atoms list
        cycleTuples = []

        for atom in atoms:
            if "cycle" in atom:
                X = int(atom.strip().split(",")[0].strip().split("(")[1]) # gets X from cycle(X,Y)
                Y = int(atom.strip().split(",")[1].strip().split(")")[0]) # gets A from cycle(X,Y)
                cycleTuples.append((X,Y))

        self.__constructListOfCycles(cycleTuples)
    
    def __assignWorstRankedPartners(self, agent : Agent):
        results = []
        for cycle in self.listOfCycles:
            worstRank, worstRankedPartnerID = cycle.getWorstRankedPartner(agent=agent)
            results.append((worstRank, worstRankedPartnerID))
        results.sort(reverse=True) # sorts tuples (by default) by using the first item in each tuple in ascending
        worstRankedID = results[0][1] # first element of results is the max
        agent.worstRankedAgentID = worstRankedID

    def __handleWorstRanksOfAgents(self):
        for agent in self.setOfAgents:
            self.__assignWorstRankedPartners(agent)
    
    def renameAgents(self, totalSizeOfPrevSeeds):
        for agent in self.setOfAgents:
            agent.renameAgent(totalSizeOfPrevSeeds)
        
        for cycle in self.listOfCycles:
            cycle.renameCycle(totalSizeOfPrevSeeds)
