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
:- dynamic confirmWumpus/2.
:- dynamic confirmPit/2.

:- dynamic playerPoints/1.
:- dynamic playerHasGold/1.

:- dynamic hasWumpus/2.
:- dynamic confirmSafe/2.
:- dynamic testSafe/2.

% initial conditions
playerPoints(0).
playerHasGold(no).
playerAlive(yes).

% test conditions (comment out when using map to create environment)

% wumpus at 1,1
%hasWumpus(1,1).
%hasStench(0,1).
%hasStench(1,0).
%hasStench(1,2).
%hasStench(2,1).

%glitter at 2,2
%hasGlitter(2,2).

% pit at 3,3
%hasPit(3,3).
%hasBreeze(2,3).
%hasBreeze(3,2).
%hasBreeze(4,3).
%hasBreeze(3,4).


% dummy notifyWumpus for when python is not connected (comment out if using python)
%notifyWumpus(X,Y) :-
%  format('Wumpus discovered on ~w ~w', [X,Y]),
%  nl.

% dummy notifyPit for when python is not connected (comment out if using python)
%notifyPit(X,Y) :-
%  format('Pit discovered on ~w ~w', [X,Y]),
%  nl.

% check to see if you can deduce that Wumpus is at X, Y
testWumpus(X,Y) :-
  wumpusTestOne(X,Y);
  wumpusTestTwo(X,Y).

% at least three adjacent squares have a stench
wumpusTestOne(X,Y) :-
  confirmStench(A ,B),
  confirmStench(C, D),
  confirmStench(E, F),
  (A =\= C ; B =\= D),
  (A =\= E ; B =\= F),
  (C =\= E ; D =\= F),
  isAdjacent(X,Y,A,B),
  isAdjacent(X,Y,C,D),
  format("Wumpus adjacent to ~w ~w, ~w ~w, and ~w ~w. ", [A,B,C,D,E,F]),
  nl,
  assert(confirmWumpus(X,Y)),
  notifyWumpus(X,Y),
  !.

% two squares have stench and one safe square is adjacent to both of the stenchy squares
wumpusTestTwo(X,Y) :-
  confirmStench(A ,B),
  confirmStench(C, D),
  confirmSafe(E, F),
  (A =\= C ; B =\= D),
  (A =\= E ; B =\= F),
  (C =\= E ; D =\= F),
  isAdjacent(A,B,E,F),
  isAdjacent(C,D,E,F),
  isAdjacent(X,Y,A,B),
  isAdjacent(X,Y,C,D),
  format("Wumpus adjacent to ~w ~w, ~w ~w, and ~w ~w. ", [A,B,C,D,E,F]),
  nl,
  assert(confirmWumpus(X,Y)),
  notifyWumpus(X,Y),
  !.

testSafe(X,Y) :-
    confirmSafe(X,Y) ->
    notifySafe(X,Y);
    notifyNotSafe(X,Y).

% check to see if you can deduce that Pit is at X, Y
testPit(X,Y) :-
  pitTestOne(X,Y);
  pitTestTwo(X,Y).

pitTestOne(X,Y) :-
  confirmBreeze(A ,B),
  confirmBreeze(C, D),
  confirmBreeze(E, F),
  (A =\= C ; B =\= D),
  (A =\= E ; B =\= F),
  (C =\= E ; D =\= F),
  format("Pit adjacent to ~w ~w, and ~w ~w. ", [A,B,C,D]),
  assert(confirmPit(X,Y)),
  notifyPit(X,Y),
  !.

pitTestTwo(X,Y) :-
  confirmBreeze(A ,B),
  confirmBreeze(C, D),
  confirmSafe(E, F),
  (A =\= C ; B =\= D),
  (A =\= E ; B =\= F),
  (C =\= E ; D =\= F),
  isAdjacent(A,B,E,F),
  isAdjacent(C,D,E,F),
  isAdjacent(X,Y,A,B),
  isAdjacent(X,Y,C,D),
  format("Pit adjacent to ~w ~w, ~w ~w, and ~w ~w. ", [A,B,C,D,E,F]),
  nl,
  assert(confirmPit(X,Y)),
  notifyPit(X,Y),
  !.

% not currently being used, but could come in handy when tying to confirm wumpus and pit locations each turn
allAdjacentTo(X,Y, [Head|Tail], NumColumns) :-
  Row is div(Head, NumColumns),
  Col is mod(Head, NumColumns),
  isAdjacent(X,Y,Row,Col),
  fail();
  allAdjacentTo(X,Y,Tail, NumColumns).

% is x1, y1 adjacent to x2, y2
isAdjacent(X1,Y1,X2,Y2) :-
  (X1 =:= X2, (Y1 =:= Y2 - 1; Y1 =:= Y2 + 1)),
  format('~w ~w , ~w ~w', [X1,Y1,X2,Y2] ), nl;
  (Y1 =:= Y2, (X1 =:= X2 - 1; X1 =:= X2 + 1)),
  format('~w ~w , ~w ~w', [X1,Y1,X2,Y2] ),
  nl.


% confirm percepts when entering a space
move(X,Y) :-
  deathFromWumpus(X,Y);
  deathFromPit(X,Y);
  confirmIfBreeze(X,Y);
  confirmIfStench(X,Y);
  confirmIfGlitter(X,Y);
  assert(confirmSafe(X,Y)),
  true().


deathFromWumpus(X,Y) :-
  hasWumpus(X,Y),
  write('Chomp! Chomp! You have been killed by the wumpus!'),
  assert(playerAlive(no)),
  retract(playerAlive(yes)),
  !.

deathFromPit(X,Y) :-
  hasPit(X,Y),
  write('Ahhh! You have fallen in a pit!'),
  assert(playerAlive(no)),
  retract(playerAlive(yes)),
  !.

confirmIfBreeze(X,Y) :-
  hasBreeze(X,Y),
  assert(confirmBreeze(X,Y)),
  format('confirmed breeze on ~w ~w', [X,Y]),
  nl,
  fail().

confirmIfStench(X,Y) :-
  hasStench(X,Y),
  assert(confirmStench(X,Y)),
  format('confirmed stench on ~w ~w', [X,Y]),
  nl,
  fail().

% if has glitter, confirm and pick up gold
confirmIfGlitter(X,Y) :-
  hasGlitter(X,Y),
  assert(confirmGlitter(X,Y)),
  format('confirmed glitter on ~w ~w', [X,Y]),
  nl,
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
