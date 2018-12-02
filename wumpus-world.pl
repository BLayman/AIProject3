
:- dynamic foundBreeze/2.
:- dynamic foundStench/2.
:- dynamic foundGlitter/2.
:- dynamic visited/2.
:- dynamic bump/2.

width(4).
height(4).

% hidden information

cell(1,1).

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
  not(foundBreeze(NX, NY)).

noWumpus(X, Y) :-
  neighbor(X, Y, NX, NY),
  visited(NX, NY),
  not(foundStench(NX, NY)).

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
  isSafe(X,Y).

% for discovering new percepts at a visited cell.

inBounds(X, Y) :-
  cell(X,Y),
  width(W),
  height(H),
  X >= 1,
  X =< W,
  Y >= 1,
  Y =< H.

visit(X, Y) :-
  (visited(X,Y) -> false; true),
  assertz(visited(X,Y)),
  (inBounds(X,Y) -> true ; assertz(bump(X,Y)), false),
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
  (hasBreeze(X, Y) -> assertz(foundBreeze(X, Y)); true),
  (hasStench(X, Y) -> assertz(foundStench(X, Y)); true),
  (hasGlitter(X, Y) -> assertz(foundGlitter(X, Y)); true).

foundWumpus(X,Y) :-
  neighbor(X,Y,AX,AY),
  neighbor(X,Y,BX,BY),
  not((AX == BX, AY == BY)),
  hasStench(AX, AY),
  hasStench(BX, BY),
  not(isSafe(X,Y)).
