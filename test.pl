:- dynamic hasStench/2.
:- dynamic hasBreeze/2.

:- dynamic confirmStench/2.
:- dynamic confirmBreeze/2.

:- dynamic hasStench/2.
:- dynamic hasBreeze/2.
:- dynamic hasGlitter/2.

:- dynamic confirmStench/2.
:- dynamic confirmBreeze/2.
:- dynamic confirmGlitter/2.

:- dynamic playerPoints/1.
:- dynamic playerHasGold/1.

:- dynamic hasWumpus/2.
:- dynamic notifyWumpus/2.

% initial conditions
playerPoints(0).
playerHasGold(no).

% test conditions
hasStench(0,1).
hasStench(1,0).
hasStench(1,2).
hasStench(2,1).
%confirmStench(0,1).
%confirmStench(1,0).
hasBreeze(1,1).
hasGlitter(2,2).

% dummy notifyWumpus for when python is not connected (comment out if using python)
notifyWumpus(X,Y) :-
  format('Wumpus discovered on ~w ~w', [X,Y]),
  nl.

% note: this is not complete!
testWumpus(X,Y) :-
  confirmStench(A ,B),
  confirmStench(C, D),
  (A =\= C ; B =\= D),
  isAdjacent(X,Y,A,B),
  isAdjacent(X,Y,C,D),
  format("Wumpus adjacent to ~w ~w, and ~w ~w.", [A,B,C,D]),
  assert(confirmWumpus(X,Y)),
  notifyWumpus(X,Y).


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


% confirm percepts when entering a space
move(X,Y) :-
  confirmIfBreeze(X,Y);
  confirmIfStench(X,Y);
  confirmIfGlitter(X,Y);
  true().

confirmIfBreeze(X,Y) :-
  hasBreeze(X,Y),
  assert(confirmBreeze(X,Y)),
  format('confirmed breeze on ~w ~w', [X,Y]),
  fail().

confirmIfStench(X,Y) :-
  hasStench(X,Y),
  assert(confirmStench(X,Y)),
  format('confirmed stench on ~w ~w', [X,Y]),
  fail().

confirmIfGlitter(X,Y) :-
  hasGlitter(X,Y),
  assert(confirmGlitter(X,Y)),
  format('confirmed glitter on ~w ~w', [X,Y]),
  retract(hasGlitter(X,Y)),
  pickUpGold(),
  fail().


% if glitter is percieved, pick it gold, and increase player points
pickUpGold() :-
  increasePlayerPoints(1000),
  assert(playerHasGold(yes)),
  retract(playerHasGold(no)).

increasePlayerPoints(X) :-
  playerPoints(Z),
  Y is X + Z,
  retract(playerPoints(Z)),
  assert(playerPoints(Y)).

% in case we need to decrease player points
decreasePlayerPoints(X) :-
  playerPoints(Z),
  Y is Z - X,
  retract(playerPoints(Z)),
  assert(playerPoints(Y)).
