from pyswip.prolog import Prolog
from pyswip.easy import registerForeign

import mapGen

def notify(x):
    print("%s should be avoided" % x)

def killWumpus(prolog):
    prolog.assertz("dead(wumpus)")

def notifyWumpus(x,y):
    print("wumpus deduced to be at %d %d " %(x,y))

def notifyPit(x,y):
    print("pit deduced to be at %d %d " %(x,y))

def notifySafe(x,y):
    print("%d %d is safe" % (x,y))

def notifyNotSafe(x,y):
    print("%d %d is not safe" % (x,y))

def main():
    prolog = Prolog()
    notify.arity = 1
    registerForeign(notify)
    notifyWumpus.arity = 2
    notifyPit.arity = 2
    notifyNotSafe.arity = 2
    notifySafe.arity = 2
    registerForeign(notifySafe)
    registerForeign(notifyNotSafe)
    registerForeign(notifyWumpus)
    registerForeign(notifyPit)


    prolog.consult("test.pl")

    # Generate a new world instance
    #world = mapGen.generateWorld(5, 5, 0, 0)
    world = mapGen.genWorldFromTxt('map.txt')
    # Put that world into our prolog instance
    mapGen.assumeWorld(prolog, world)
    mapGen.printWorld(world)
    position = (0,0)
    list(prolog.query("move(0,0)"))
    list(prolog.query("testSafe(0,0)"))
    list(prolog.query("testSafe(1,0)"))
    print("Wumpus: \n" + str(list(prolog.query("hasWumpus(X,Y)"))))


if __name__ == "__main__":
    main()