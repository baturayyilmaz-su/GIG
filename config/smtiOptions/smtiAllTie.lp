% Ensuring everyone in the preference list is in the same rank (If p2 = 1)
:- mrank(M,W1,R1), mrank(M,W2,R2), W1!=W2, R1!=R2.
:- wrank(W,M1,R1), wrank(W,M2,R2), M1!=M2, R1!=R2.