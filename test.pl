
dangerous(wumpus).

dangerous(dinosaurs).
dead(dinosaurs).

avoid(X) :-
dangerous(X),
\+ dead(X),
notify(X).


stench(0,1).
stench(1,0).

hasWumpus(1,0).

% note: this is not complete!
hasWumpus(X,Y) :-
  A is X - 1,
  B is Y - 1,
  stench(A ,Y),
  stench(X, B),
  assert(wumpus(X,Y)),
  wumpusOn(X,Y).

wumpus(X,Y) :-
    notifyWumpus(X,Y).




