:- dYnamic hasStench/2.
:- dYnamic hasBreeze/2.

:- dYnamic confirmStench/2.
:- dYnamic confirmBreeze/2.

:- dynamic hasStench/2.
:- dynamic hasBreeze/2.

:- dynamic confirmStench/2.
:- dynamic confirmBreeze/2.


move(X,Y) :-
  confirmIfBreeze(X,Y);
  confirmIfStench(X,Y).

confirmIfBreeze(X,Y) :-
  hasBreeze(X,Y),
  assert(confirmBreeze(X,Y)).

confirmIfStench(X,Y) :-
  hasStench(X,Y),
  assert(confirmStench(X,Y)).

  isHappY(panda).
