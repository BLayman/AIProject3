
dangerous(wumpus).

dangerous(dinosaurs).
dead(dinosaurs).

avoid(X) :-
dangerous(X),
\+ dead(X),
notify(X).

wumpusOn(-1,-1).
notifyWumpus(-1,-1).

stench(0,1).
stench(1,0).

% note: this is not complete!
hasWumpus(X,Y) :-
  isAdjacent(X,Y,A,B),
  isAdjacent(X,Y,C,D),
  stench(A ,B),
  stench(C, D),
  assert(wumpus(X,Y)),
  wumpusOn(X,Y).

wumpus(X,Y) :-
    notifyWumpus(X,Y).

allAdjacentTo(X,Y, []).

allAdjacentTo(X,Y, [Head|Tail], NumColumns) :-
  Row is div(Head, NumColumns),
  Col is mod(Head, NumColumns),
  isAdjacent(X,Y,Row,Col),
  fail();
  allAdjacentTo(X,Y,Tail, NumColumns).


isAdjacent(X1,Y1,X2,Y2) :-
  (X1 =:= X2, (Y1 =:= Y2 - 1; Y1 =:= Y2 + 1)),
  format('~w ~w , ~w ~w', [X1,Y1,X2,Y2] ), nl;
  (Y1 =:= Y2, (X1 =:= X2 - 1; X1 =:= X2 + 1)),
  format('~w ~w , ~w ~w', [X1,Y1,X2,Y2] ), nl.
