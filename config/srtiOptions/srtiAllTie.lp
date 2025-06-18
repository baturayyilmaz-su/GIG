% Ensuring everyone in the preference list is in the same rank (If p2 = 1)
:- arank(A,A1,R1), arank(A,A2,R2), A1!=A2, R1!=R2.