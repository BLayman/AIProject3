
dangerous(wumpus).

dangerous(dinosaurs).
dead(dinosaurs).

avoid(X) :-
dangerous(X),
\+ dead(X),
notify([X]).
