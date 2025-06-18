% #const n = 10. % number of agents
% #const m = 3. % upper limit for the preference lists

agent(1..n).
1{arank(A1,A2,R) : agent(A2), R=1..n, A1!=A2}n :- agent(A1). % arank(A1,A2,R) -> "rank, R, of A2 for A1"
:- arank(A1,A2,R1), arank(A1,A2,R2), R1!=R2. % same agent cannot be preferred in different ranks
:- not arank(A,_,R-1), arank(A,_,R), R=2..n. % for ranks to start from 1 and increase one by one. = no empty ranks

% generate the dependency graph of the instance (argumentation framework)
acceptable(A1,A2) :- arank(A1,A2,_), arank(A2,A1,_), A1<A2. % nodes are formed from acceptable pairs
preferAsLeastAs(A1,A2,A3) :- arank(A1,A2,R1), arank(A1,A3,R2), R2>=R1, A2!=A3. % ties attack each other in weakly-stable matchings

arc(A1, A2, A1, A3) :- acceptable(A1,A2), acceptable(A1,A3), A2 != A3, preferAsLeastAs(A1,A2,A4).
arc(A1, A2, A3, A1) :- acceptable(A1,A2), acceptable(A3,A1), A2 != A3, preferAsLeastAs(A1,A2,A3).
arc(A1, A2, A2, A3) :- acceptable(A1,A2), acceptable(A2,A3), A1 != A3, preferAsLeastAs(A2,A1,A4).
arc(A1, A2, A3, A2) :- acceptable(A1,A2), acceptable(A3,A2), A1 != A3, preferAsLeastAs(A2,A1,A3).

reachable(A1,A2,A3,A4) :- arc(A1,A2,A3,A4).
reachable(A1,A2,A3,A4) :- reachable(A1,A2,X,Y), reachable(X,Y,A3,A4).

% Generate a cycle. 
% #const c = 3. % cycle size
% #const a = 1. % cycle count
X{cycle(A1,A2) : acceptable(A1,A2)}X :- X=c*a.
:- cycle(A1,A2), not reachable(A1,A2,A1,A2).
% -- Cycle Constraints
attackedByCycle(A1,A2) :- cycle(A1,A2), cycle(A3,A4), arc(A3,A4,A1,A2). % node in a cycle must be attacked by cycle 
:- cycle(A1,A2), not attackedByCycle(A1,A2).
:- cycle(A1,A2), #count{X,Y : arc(X,Y,A1,A2)}>1. % 1 incoming edge to a cycle node.
:- cycle(A1,A2), #count{A3,A4 : cycle(A3,A4), reachable(A1,A2,A3,A4)}!=c. % there should be c many reachable nodes from a cycle node (A1,A2) including itself.


% #const k = 1. % stickyness degree
% cycleArc(A1,A2,A4) :- arc(A1,A2,A3,A4), cycle(A1,A2), cycle(A3,A4), A1=A3.
% cycleArc(A1,A2,A3) :- arc(A1,A2,A3,A4), cycle(A1,A2), cycle(A3,A4), A1=A4.
% cycleArc(A2,A1,A4) :- arc(A1,A2,A3,A4), cycle(A1,A2), cycle(A3,A4), A2=A3.
% cycleArc(A2,A1,A3) :- arc(A1,A2,A3,A4), cycle(A1,A2), cycle(A3,A4), A2=A4.
% :- cycleArc(X,A1,A2), arank(X,A1,R1), arank(X,A2,R2), |R1-R2| < k.

cycleArc(A1,A2,A4) :- arc(A1,A2,A1,A4), cycle(A1,A2), cycle(A1,A4).
cycleArc(A1,A2,A3) :- arc(A1,A2,A3,A1), cycle(A1,A2), cycle(A3,A1).
cycleArc(A2,A1,A4) :- arc(A1,A2,A2,A4), cycle(A1,A2), cycle(A2,A4).
cycleArc(A2,A1,A3) :- arc(A1,A2,A3,A2), cycle(A1,A2), cycle(A3,A2).
:- cycleArc(X,A1,A2), arank(X,A1,R1), arank(X,A2,R2), |R1-R2| < k.


#show agent/1.
#show arank/3.
#show cycle/2.
#show arc/4.