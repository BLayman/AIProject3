
from __future__ import print_function
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign


def notify(x):
    print("%s should be avoided" % tuple(x))


def main():
    notify.arity = 1
    prolog = Prolog()
    registerForeign(notify)
    prolog.consult("test.pl")
    list(prolog.query("avoid(wumpus)"))
    list(prolog.query("avoid(dinosaurs)"))


if __name__ == "__main__":
    main()
