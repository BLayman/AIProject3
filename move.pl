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

playerPoints(0).

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
  pickUpGlitter(),
  fail().


% if glitter is percieved, pick it up, and increase player points
pickUpGlitter() :-
  increaseCreaturePoints(1000).

increaseCreaturePoints(X) :-
  playerPoints(Z),
  Y is X + Z,
  retract(playerPoints(Z)),
  assert(playerPoints(Y)).
