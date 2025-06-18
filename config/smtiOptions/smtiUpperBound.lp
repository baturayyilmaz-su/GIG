% Upper bound for preference list size
:- #count{W : mrank(M,W,_)} > m, M=1..n. % there at most m women in man's preference list.
:- #count{M : wrank(W,M,_)} > m, W=1..n. % there at most m men in woman's preference list.