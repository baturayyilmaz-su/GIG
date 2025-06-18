% Ensuring symmetric preference lists
:- arank(A1,A2,_), not arank(A2,A1,_).