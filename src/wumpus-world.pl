:- dynamic width/1.
:- dynamic height/1.
:- dynamic hasPit/2.
:- dynamic cell/2.
:- dynamic foundBreeze/2.
:- dynamic foundStench/2.
:- dynamic foundGlitter/2.
:- dynamic visited/2.
:- dynamic bump/3.
:- dynamic scream/0.
:- dynamic visitedInBounds/2.


initPredicates() :-
  retractall(width(_)),
  retractall(height(_)),
  retractall(hasGold(_,_)),
  retractall(hasPit(_,_)),
  retractall(hasWumpus(_,_)),
  retractall(scream()),
  retractall(cell(_,_)),
  retractall(foundBreeze(_,_)),
  retractall(foundGlitter(_,_)),
  retractall(foundStench(_,_)),
  retractall(visitedInBounds(_,_)),
  retractall(visited(_,_)).

dieFromWumpus(X,Y) :-
  hasWumpus(X,Y),
  not(scream()).

isDead(X,Y) :-
  hasPit(X,Y);
  hasWumpus(X,Y).

outOfFoundBounds(X,Y) :-
  bump(BX,BY,BD),
  (BD == 0 -> Y >= BY; true),
  (BD == 2 -> Y =< BY; true),
  (BD == 1 -> X >= BX; true),
  (BD == 3 -> X =< BX; true).


% hidden information

neighbor(X1, Y1, X2, Y2) :-
  cell(X1, Y1),
  cell(X2, Y2),
  (above(X1, Y1, X2, Y2);
  below(X1, Y1, X2, Y2);
  right(X1, Y1, X2, Y2);
  left(X1, Y1, X2, Y2)).


above(X1, Y1, X2, Y2) :-
  X2 =:= X1,
  Y2 =:= Y1+1.

below(X1, Y1, X2, Y2) :-
  X2 =:= X1,
  Y2 =:= Y1-1.

right(X1, Y1, X2, Y2) :-
  Y2 =:= Y1,
  X2 =:= X1+1.

left(X1, Y1, X2, Y2) :-
  Y2 =:= Y1,
  X2 =:= X1-1.

% predicates for determining percept assignments.

hasStench(X, Y) :-
  neighbor(X, Y, NX, NY),
  hasWumpus(NX, NY).

hasBreeze(X, Y) :-
  neighbor(X, Y, NX, NY),
  hasPit(NX, NY).

hasGlitter(X, Y) :-
  hasGold(X, Y).

% predicates for deducing whether entities exist given perception.

noPit(X, Y) :-
  neighbor(X, Y, NX, NY),
  visited(NX, NY),
  inBounds(NX, NY),
  not(foundBreeze(NX, NY)).

noWumpus(X, Y) :-
  scream();
  (neighbor(X, Y, NX, NY),
  visited(NX, NY),
  inBounds(NX, NY),
  not(foundStench(NX, NY))).

neighborVisited(X, Y) :-
  neighbor(X, Y, NX, NY),
  visited(NX, NY).

isSafe(X, Y) :-
  visited(X,Y);
  (noWumpus(X, Y),
  noPit(X, Y)).

isUnvisitedSafe(X, Y) :-
  cell(X,Y),
  not(visited(X,Y)),
  isSafe(X,Y),
  not(outOfFoundBounds(X,Y)).

% for discovering new percepts at a visited cell.

inBounds(X, Y) :-
  cell(X,Y),
  width(W),
  height(H),
  X >= 1,
  X =< W,
  Y >= 1,
  Y =< H.

visit(X, Y, D) :-
  (visited(X,Y) -> false; true),
  assertz(visited(X,Y)),
  (inBounds(X,Y) -> assertz(visitedInBounds(X,Y)) ; assertz(bump(X,Y,D)), false),
  XP is X+1,
  XM is X-1,
  YP is Y+1,
  YM is Y-1,
  assertz(cell(X,YM)),
  assertz(cell(X,YP)),
  assertz(cell(XM,Y)),
  assertz(cell(XP,Y)),
  gatherPercepts(X, Y).

gatherPercepts(X, Y) :-
  inBounds(X,Y),
  (hasBreeze(X, Y) -> assertz(foundBreeze(X, Y)); true),
  (hasStench(X, Y) -> assertz(foundStench(X, Y)); true),
  (hasGlitter(X, Y) -> assertz(foundGlitter(X, Y)); true).

foundWumpus(X,Y) :-
  neighbor(X,Y,AX,AY),
  neighbor(X,Y,BX,BY),
  not((AX == BX, AY == BY)),
  hasStench(AX, AY),
  hasStench(BX, BY),
  not(isSafe(X,Y)),
  !.

% kill the wumpus
killWumpus() :-
  assertz(scream()).

dangerBreeze(X,Y, DX, DY) :-
  cell(X,Y),
  cell(DX,DY),
  not(visited(X,Y)),
  neighbor(X,Y,DX,DY),
  (foundBreeze(DX,DY)).

dangerStench(X,Y,DX,DY) :-
  cell(X,Y),
  cell(DX,DY),
  not(visited(X,Y)),
  neighbor(X,Y,DX,DY),
  (foundStench(DX,DY)).
