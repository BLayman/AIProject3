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

% ###################### GAME STATE ######################

% removes all predicate assignments, used for resetting to a new game.
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

% Position (X,Y) will lead to death by wumpus
dieFromWumpus(X,Y) :-
  hasWumpus(X,Y),
  not(scream()).

% Cell (X,Y) is in bounds of the current 'width' and 'height'
inBounds(X, Y) :-
  cell(X,Y),
  width(W),
  height(H),
  X >= 1,
  X =< W,
  Y >= 1,
  Y =< H.

% (X1, Y1) and (X2,Y2) are adjacent to one another.
neighbor(X1, Y1, X2, Y2) :-
  cell(X1, Y1),
  cell(X2, Y2),
  (above(X1, Y1, X2, Y2);
  below(X1, Y1, X2, Y2);
  right(X1, Y1, X2, Y2);
  left(X1, Y1, X2, Y2)).

% (X2, Y2) is above (X1, Y1)
above(X1, Y1, X2, Y2) :-
  X2 =:= X1,
  Y2 =:= Y1+1.

% (X2, Y2) is below (X1, Y1)
below(X1, Y1, X2, Y2) :-
  X2 =:= X1,
  Y2 =:= Y1-1.

% (X2, Y2) is right (X1, Y1)
right(X1, Y1, X2, Y2) :-
  Y2 =:= Y1,
  X2 =:= X1+1.

% (X2, Y2) is left (X1, Y1)
left(X1, Y1, X2, Y2) :-
  Y2 =:= Y1,
  X2 =:= X1-1.

% ###################### PERCEPTS ######################

% Find all percepts available at (X,Y) by asserting their existence ('foundX')
gatherPercepts(X, Y) :-
  inBounds(X,Y),
  (hasBreeze(X, Y) -> assertz(foundBreeze(X, Y)); true),
  (hasStench(X, Y) -> assertz(foundStench(X, Y)); true),
  (hasGlitter(X, Y) -> assertz(foundGlitter(X, Y)); true).

% (X,Y) has a stench if it neighbors a wumpus (PLAYER CAN'T USE)
hasStench(X, Y) :-
  neighbor(X, Y, NX, NY),
  hasWumpus(NX, NY).

% (X,Y) has a breeze if it neighbors a pit (PLAYER CAN'T USE)
hasBreeze(X, Y) :-
  neighbor(X, Y, NX, NY),
  hasPit(NX, NY).

% (X,Y) has glitter if it has a gold on it (PLAYER CAN'T USE)
hasGlitter(X, Y) :-
  hasGold(X, Y).

% ###################### ACTIONS ######################

% Visit cell (X,Y) facing direction D
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

% Kill the wumpus
killWumpus() :-
  assertz(scream()).

% ###################### CAUTIOUS INFERENCE ######################

% Pit doesn't exist at X,Y if we have visited a neighbor of X,Y and it did not
% have a breeze percept.
noPit(X, Y) :-
  neighbor(X, Y, NX, NY),
  visited(NX, NY),
  inBounds(NX, NY),
  not(foundBreeze(NX, NY)).

% Wumpus doesn't exist at X,Y if we have visited a neighbor of X,Y and it did
% not have a stench percept.
noWumpus(X, Y) :-
  scream();
  (neighbor(X, Y, NX, NY),
  visited(NX, NY),
  inBounds(NX, NY),
  not(foundStench(NX, NY))).

% A cell X,Y is safe overall if (1) we have visited it, or (2) we have deduced
% that it has no pit and no wumpus.
isSafe(X, Y) :-
  visited(X,Y);
  (noWumpus(X, Y),
  noPit(X, Y)).

% A cell X,Y that satisfies both 'isSafe' and has not been visited yet.
isUnvisitedSafe(X, Y) :-
  cell(X,Y),
  not(visited(X,Y)),
  isSafe(X,Y),
  not(outOfFoundBounds(X,Y)).

% A cell X,Y is the location of the wumpus if we know two neighbors that we
% have discovered stenches at, and the cell is not confirmed as safe.
foundWumpus(X,Y) :-
  neighbor(X,Y,AX,AY),
  neighbor(X,Y,BX,BY),
  not((AX == BX, AY == BY)),
  foundStench(AX, AY),
  foundStench(BX, BY),
  not(isSafe(X,Y)),
  !.

% Player can infer that X,Y is out of bounds given the coordinats of when he
% bumped into a wall and the direction he was going.
outOfFoundBounds(X,Y) :-
  bump(BX,BY,BD),
  (BD == 0 -> Y >= BY; true),
  (BD == 2 -> Y =< BY; true),
  (BD == 1 -> X >= BX; true),
  (BD == 3 -> X =< BX; true).

% ###################### BEST MOVE INFERENCE ######################

% Unvisited cell (X,Y) is a danger because a neighbor (DX,DY) has a found breeze
% percept.
dangerBreeze(X,Y, DX, DY) :-
  cell(X,Y),
  cell(DX,DY),
  not(visited(X,Y)),
  neighbor(X,Y,DX,DY),
  (foundBreeze(DX,DY)).

% Unvisited cell (X,Y) is a danger because a neighbor (DX,DY) has a found stench
% percept.
dangerStench(X,Y,DX,DY) :-
  cell(X,Y),
  cell(DX,DY),
  not(visited(X,Y)),
  neighbor(X,Y,DX,DY),
  (foundStench(DX,DY)).
