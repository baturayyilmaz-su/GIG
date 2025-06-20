% The following constants are set in config directory.
% #const n -> number of men (and women)
% #const m -> upper limit for preference lists
% #const k -> % min. number of solutions of instance.

1{mrank(M,W,R) : W=1..n, R=1..n}n :- M=1..n.
1{wrank(W,M,R) : M=1..n, R=1..n}n :- W=1..n.

% man(woman) cannot prefer two women(men) in different ranks
:- mrank(M,W1,R1), mrank(M,W2,R2), W1=W2, R1!=R2.
:- wrank(W,M1,R1), wrank(W,M2,R2), M1=M2, R1!=R2.

%% ranks starts from 1 and be incremental.
:- not mrank(M,_,R-1), mrank(M,_,R), R=2..n.
:- not wrank(W,_,R-1), wrank(W,_,R), R=2..n.

% Define helpers based on input
acceptable(M,W) :- mrank(M,W,_), wrank(W,M,_).
mPrefers(M,W1,W2) :- mrank(M,W1,R1), mrank(M,W2,R2), R1<R2.
wPrefers(W,M1,M2) :- wrank(W,M1,R1), wrank(W,M2,R2), R1<R2.

% Generate k matching
0{matched(M,W,I) : acceptable(M,W)}1 :- M=1..n, I=1..k. % try to generate a match for every acceptable pairs where M is a man
mSingle(M,I) :- not matched(M,_,I), M=1..n, I=1..k.
wSingle(W,I) :- not matched(_,W,I), W=1..n, I=1..k.

% Constraints:
% every woman and man can be matched at most once at each instant
:- matched(M,W1,I), matched(M,W2,I), W1!=W2.
:- matched(M1,W,I), matched(M2,W,I), M1!=M2.

% Defining blocking pairs
% m and w is blocking if m is unmatched and w is unmatched
blockingPair(M,W,I) :- mSingle(M,I), wSingle(W,I), acceptable(M,W).
% m and w is blocking if m is unmatched and w preferes him more than her current match
blockingPair(M,W,I) :- mSingle(M,I), matched(Mi,W,I), wPrefers(W, M, Mi), acceptable(M,W).
% m and w is blocking if w is unmatched and m prefers her more than his current match
blockingPair(M,W,I) :- wSingle(W,I), matched(M, Wj,I), mPrefers(M, W, Wj), acceptable(M,W).
% m and w is blocking if both of them are matched but they prefer each other more than their current match
blockingPair(M,W,I) :- matched(M,Wj,I), matched(Mi, W,I), mPrefers(M,W,Wj), wPrefers(W,M,Mi).

% Matching should not have a blocking pair.
:- blockingPair(M,W,I), M=1..n, W=1..n.

% instances should be different
hasDifferentPairs(I1,I2) :- matched(M,W1,I1), matched(M,W2,I2), I1<I2, W1!=W2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- matched(M,_,I1), mSingle(M,I2), I1<I2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- mSingle(M,I1), matched(M,_,I2), I1<I2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- matched(M1,W,I1), matched(M2,W,I2), I1<I2, M1!=M2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- matched(_,W,I1), wSingle(W,I2), I1<I2, I1=1..k, I2=1..k.
hasDifferentPairs(I1,I2) :- wSingle(W,I1), matched(_,W,I2), I1<I2, I1=1..k, I2=1..k.

:- not hasDifferentPairs(I1,I2), I1<I2, I1=1..k, I2=1..k.


#show matched/3.
#show mSingle/2.
#show wSingle/2.
#show mrank/3.
#show wrank/3.