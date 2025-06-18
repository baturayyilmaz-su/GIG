% Ensuring symmetric preference lists
:- mrank(M,W,_), not wrank(W,M,_).
:- wrank(W,M,_), not mrank(M,W,_).