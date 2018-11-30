:- dynamic hasStench/2.
:- dynamic hasBreeze/2.

:- dynamic confirmStench/2.
:- dynamic confirmBreeze/2.

:- dynamic hasStench/2.
:- dynamic hasBreeze/2.

:- dynamic confirmStench/2.
:- dynamic confirmBreeze/2.

hasStench(1,1).
hasBreeze(1,1).

move(X,Y) :-
  confirmIfBreeze(X,Y);
  confirmIfStench(X,Y).

confirmIfBreeze(X,Y) :-
  hasBreeze(X,Y),
  assert(confirmBreeze(X,Y)),
  fail().

confirmIfStench(X,Y) :-
  hasStench(X,Y),
  assert(confirmStench(X,Y)).

  isHappy(panda).
