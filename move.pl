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

% initial conditions
playerPoints(0).
playerHasGold(no).

% test conditions
hasStench(1,1).
hasBreeze(1,1).
hasGlitter(2,2).

% confirm percepts when entering a space
move(X,Y) :-
  confirmIfBreeze(X,Y);
  confirmIfStench(X,Y);
  confirmIfGlitter(X,Y);
  true().

confirmIfBreeze(X,Y) :-
  hasBreeze(X,Y),
  assert(confirmBreeze(X,Y)),
  fail().

confirmIfStench(X,Y) :-
  hasStench(X,Y),
  assert(confirmStench(X,Y)),
  fail().

confirmIfGlitter(X,Y) :-
  hasGlitter(X,Y),
  assert(confirmGlitter(X,Y)),
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
