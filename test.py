
from __future__ import print_function
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign


def notify(x):
    print("%s should be avoided" % x)

def killWumpus(prolog):
    prolog.assertz("dead(wumpus)")

def wumpusOn(x, y):
    print("hello")
    print("wumpus is on %d %d " %(x,y))


def main():
    prolog = Prolog()
    notify.arity = 1
    registerForeign(notify)
    wumpusOn.arity = 2
    registerForeign(wumpusOn)

    prolog.consult("test.pl")
    prolog.assertz("stench(1,2)")
    prolog.assertz("stench(2,1)")

    list(prolog.query("hasWumpus(2,2)"))
    #list(prolog.query("avoid(wumpus)"))
    #list(prolog.query("avoid(dinosaurs)"))


if __name__ == "__main__":
    main()
