
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign


def notify(x):
    print("%s should be avoided" % x)

def killWumpus(prolog):
    prolog.assertz("dead(wumpus)")


def notifyWumpus(x,y):
    print("wumpus deduced to be at %d %d " %(x,y))

def notifyPit(x,y):
    print("pit deduced to be at %d %d " %(x,y))


def main():
    prolog = Prolog()
    notify.arity = 1
    registerForeign(notify)
    notifyWumpus.arity = 2
    notifyPit.arity = 2
    registerForeign(notifyWumpus)
    registerForeign(notifyPit)

    prolog.consult("test.pl")

    list(prolog.query("move(0,1)"))
    list(prolog.query("move(1,0)"))
    list(prolog.query("testWumpus(1,1)"))


if __name__ == "__main__":
    main()
