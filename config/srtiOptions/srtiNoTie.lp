% Ensuring there will be no ties in the seed. (If p2=0).
:- arank(A,A1,R1), arank(A,A2,R2), A1!=A2, R1=R2.