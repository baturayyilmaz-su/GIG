% The following constants are set in config directory.
% #const n -> number of agents
% #const m -> upper limit for preference lists
% #const k -> % min. number of solutions of instance.

1{arank(A1,A2,R) : A2=1..n, R=1..n, A1!=A2}n :- A1=1..n.
:- arank(A1,A2,R1), arank(A1,A2,R2), R1!=R2. % same agent cannot be preferred in different ranks
:- not arank(A,_,R-1), arank(A,_,R), R=2..n. % for ranks to start from 1 and increase one by one. = no empty ranks


% SRTI Solver --------------
% Helpers based on input
acceptable(A1,A2) :- arank(A1,A2,_), arank(A2,A1,_). % if a A1 and A2, then A1 != A2 is a consequence of this rule because agents dont rank themselves.
aPrefers(A,A1,A2) :- arank(A,A1,R1), arank(A,A2,R2), R1<R2. % Every agent ranks other agents once in the input

% Generate a matching
0{matched(A1,A2,I) : acceptable(A1,A2)}1 :- A2=1..n, I=1..k. % I, added for representing every instance. Agent cannot be matched with itself. Because it is not acceptable to itself
:- matched(A1,A2,I), not matched(A2,A1,I). % If A1 is matched with A2, A2 is matched with A1.
aSingle(A,I) :- not matched(A,_,I), A=1..n, I=1..k.
:- matched(A,A1,I), matched(A,A2,I), A1!=A2. % Every agent can be matched at most once

blockingPair(A1,A2,I) :- aSingle(A1,I), aSingle(A2,I), acceptable(A1,A2).
blockingPair(A1,A2,I) :- aSingle(A2,I), matched(A1,X,I), aPrefers(A1,A2,X), acceptable(A1,A2).
blockingPair(A1,A2,I) :- aSingle(A1,I), matched(A2,X,I), aPrefers(A2,A1,X), acceptable(A1,A2).
blockingPair(A1,A2,I) :- matched(A1,X,I), matched(A2,Y,I), aPrefers(A1,A2,X), aPrefers(A2,A1,Y).

:- blockingPair(A1,A2,I), A1=1..n, A2=1..n.
% --------------------------
% Instances should be different
hasDifferentPairs(I1,I2) :- matched(X,Y1,I1), matched(X,Y2,I2), I1<I2, Y1!=Y2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- matched(X,Y1,I1), aSingle(X,I2), I1<I2, I1=1..k, I2=1..k.
:- not hasDifferentPairs(I1,I2), I1<I2, I1=1..k, I2=1..k.


#show matched/3.
#show arank/3.
#show aSingle/2.