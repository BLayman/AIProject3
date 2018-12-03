from pyswip.prolog import Prolog
from pyswip.easy import registerForeign
import worldBuilder
import random
import math
import sys
from collections import Counter


def startGame(prolog):

    points = 0
    deathReason = 'Win'

    startPosition = (1,1)

    position = startPosition
    direction = 1 # up=0, right=1, down=2, left=3
    list(prolog.query("visit(%s,%s,%s)" % (position[0],position[1],direction)))

    path = []

    while(True):

        deadFromPit = list(prolog.query("hasPit(%s,%s)" % position))
        deadFromWumpus = list(prolog.query("hasWumpus(%s,%s)" % position))

        if(len(deadFromPit) != 0):
            print("Died from pit!")
            deathReason = 'Pit'
            points += -1000
            return (points, len(list(prolog.query("visited(X,Y)"))), deathReason)
        if(len(deadFromWumpus) != 0):
            print("Died from wumpus!")
            deathReason = "Wumpus"
            points += -1000
            return (points, len(list(prolog.query("visited(X,Y)"))), deathReason)

        # check for gold
        gold = len(list(prolog.query("foundGlitter(X,Y)"))) > 0

        if gold:
            print("Found gold!")

            points += 1000

            pathBackToStart = shortestPath(position, startPosition, visitedCells)
            print("Goal: " + str(startPosition))
            print("Path to start: " + str(pathBackToStart))
            traversalResult = traversePath(prolog,position, direction, pathBackToStart)

            position = traversalResult[0]
            direction = traversalResult[2]
            points += traversalResult[3]

            print("Cost to get back to start: " + str(traversalResult[3]))
            print("FINAL POINTS: " + str(points))

            return (points, len(list(prolog.query("visited(X,Y)"))), deathReason)

        unvisitedCellsDict = list(prolog.query("isUnvisitedSafe(X,Y)"))
        unvisitedCells = toTupleList(unvisitedCellsDict)

        visitedCellsDict = list(prolog.query("visitedInBounds(X,Y)"))
        visitedCells = toTupleList(visitedCellsDict)

        if len(unvisitedCells) == 0:
            print("Could not find any more safe cells, attempting to kill wumpus...")

            # Kill the wumpus, if we can...

            #
            # FIND THE WUMPUS IF WE CAN
            #
            wumpusList = toTupleList(list(prolog.query("foundWumpus(X,Y)")))
            wumpusKilled = list(prolog.query("scream()"))

            if len(wumpusList) == 0 or len(wumpusKilled) != 0:
                print("Wumpus could not be found!")
                pos = getBestMove(prolog)
                print("Guessing best move is to %d %d" % (pos[0], pos[1]))

                print("Goal: " + str(pos))
                projectedPath = shortestPath(position, pos, visitedCells)

                print("Projected path: " + str(projectedPath))

                traversalResult = traversePath(prolog,position, direction, projectedPath)

                position = traversalResult[0]
                direction = traversalResult[2]
                points += traversalResult[3]

                print("Points so far: " + str(points))

                print("-----------")


                continue

            wumpus = wumpusList[0]

            print("Wumpus at: " + str(wumpus))

            #
            # FIND CELLS THAT WE CAN SHOOT THE WUMPUS FROM
            #
            cellsInRange = []
            for cell in visitedCells:
                if len(list(prolog.query("inBounds(%s,%s)" % (cell[0], cell[1])))) == 0:
                    continue
                if cell[0] == wumpus[0] or cell[1] == wumpus[1]:
                    cellsInRange.append(cell)

            print("Cells in range: " + str(cellsInRange))


            #
            # FIND CLOSEST POSITION WE CAN SHOOT FROM
            #

            shootFrom = closestUnvisited(position, cellsInRange)
            print("Closest cell to shoot from: " + str(shootFrom))
            pathToShootPosition = shortestPath(position, shootFrom, visitedCells)

            #
            # TRAVERSE TO NEAREST POSITION TO SHOOT FROM
            #

            traversalResult = traversePath(prolog,position, direction, pathToShootPosition)

            position = traversalResult[0]
            direction = traversalResult[2]
            points += traversalResult[3]
            print("Cost to get to cell: " + str(traversalResult[3]))

            #
            # TURN DIRECTION TO FACE WUMPUS
            #

            cost = 0
            needToFace = directionToFaceNext(position, wumpus)
            print("Cost to turn to cell: " + str(cost))

            #
            # KILL THE WUMPUS
            #

            list(prolog.query("killWumpus()"))
            print("Cost to shoot arrow: " + str(-10))
            points += -10

            print("-----------")
            continue


        print("Position: " + str(position))
        currentGoal = closestUnvisited(position, unvisitedCells)
        print("Goal: " + str(currentGoal))
        projectedPath = shortestPath(position, currentGoal, visitedCells)

        print("Projected path: " + str(projectedPath))



        traversalResult = traversePath(prolog,position, direction, projectedPath)

        position = traversalResult[0]
        previousPosition = traversalResult[1]
        direction = traversalResult[2]
        points += traversalResult[3]

        print("Points for: " + str(points))

        print("-----------")

        print(position)

    print(list(prolog.query("visited(X,Y)")))
    return(points, len(list(prolog.query("visited(X,Y)"))), deathReason)

def getBestMove(prolog):
    l = list(prolog.query("dangerBreeze(X,Y, NX, NY)"))
    #Set of positions for breezes
    theSet = set()
    for thing in l:
        unkownPos = (thing["X"], thing["Y"])
        dangerZone = (thing["NX"], thing["NY"])
        theSet.add((unkownPos, dangerZone))
    l = list(prolog.query("dangerStench(X,Y,NX,NY)"))
    #Set of positions for unvisited spots with neighbors that have stenches
    theOtherSet = set()
    for thing in l:
        unkownPos = (thing["X"], thing["Y"])
        dangerZone = (thing["NX"], thing["NY"])
        theOtherSet.add((unkownPos, dangerZone))
    #Combine the sets as lists to account for wumpus and breeze at certain locations
    total = list(theSet) + list(theOtherSet)
    #Remove the breeze or stench location, just need the unvisited spot location
    total = [thing[0] for thing in total]
    total = Counter(total)
    min = -1
    pos = (0,0)
    for key in total.keys():
        if min == -1:
            min = total[key]
            pos = key
        elif total[key] < min:
            pos = key
            min = total[key]
    #Return the position with the minimum danger neighbors
    return pos

def traversePath(prolog,position, direction, projectedPath):
    cost = 0
    previousPosition = position
    for cell in projectedPath:
        needToFace = directionToFaceNext(position, cell)

        direction = needToFace

        # cost of moving...
        cost += -1

        # update position
        previousPosition = position
        position = cell

    # visit
    list(prolog.query("visit(%s,%s,%s)" % (position[0],position[1],direction)))

    # revert to 2nd to last position if we bump
    bump = len(list(prolog.query("bump(%s,%s,%s)" % (position[0],position[1],direction)))) > 0

    # if bumped, just move back. Cost of bump already taken into account.
    if bump:
        position = previousPosition
        cost += 1
    return (position, previousPosition, direction, cost)

def directionToFaceNext(origin, next):
    if(origin[0] == next[0]):
        if(origin[1] < next[1]):
            return 0
        else:
            return 2
    else:
        if(origin[0] < next[0]):
            return 1
        else:
            return 3

def findNecessaryDirection(currPos, wumpPos):
    #If same x's
    if currPos[0] == wumpPos[0]:
        #If current position is below Wumpus, point up
        if currPos[1] < wumpPos[1]:
            return 0
        #Else position is above wumpus, turn down
        else:
            return 2
    #Same y's
    else:
        #If we are to the right of wumpus turn East
        if currPos[0] < currPos[0]:
            return 1
        # We are to the left
        else:
            return 3
    #Shouldn't return false
    return False

def closestUnvisited(start, safeUnvisited):
    minDist = math.inf
    min = (None, None)

    for cell in safeUnvisited:
        dist = abs(start[0]-cell[0]) + abs(start[1]-cell[1])

        if dist < minDist:
            minDist = dist
            min = cell

    return min

def shortestPath(start, end, visited):
    marked = [start]
    frontier = [start]
    parents = {}

    while len(frontier) != 0:
        cell = frontier[0]
        del frontier[0]


        if isNeighbor(end, cell):
            parents[end] = cell
            path = []

            iterator = end
            while(iterator != start):
                path.append(iterator)
                iterator = parents[iterator]
            path.reverse()
            return path


        for neighbor in neighbors(cell, visited):
            if neighbor in marked:
                continue
            marked.append(neighbor)
            frontier.append(neighbor)
            parents[neighbor] = cell


def neighbors(cell, cellList):
    neighbors = []
    for c in cellList:
        if isNeighbor(cell, c):
            neighbors.append(c)
    return neighbors

def isNeighbor(cellA, cellB):
    vertical = cellA[0] == cellB[0] and abs(cellA[1]-cellB[1]) == 1
    horizontal = cellA[1] == cellB[1] and abs(cellA[0]-cellB[0]) == 1
    return vertical or horizontal

def toTupleList(cellDict):
    tlist = []
    for cell in cellDict:
        x = cell['X']
        y = cell['Y']
        tlist.append((x,y))
    return list(set(tlist))



def nextMove(position, safeCells):
    adjacentCells = []
    for cell in safeCells:
        vertical = cell[0] == position[0] and abs(cell[1]-position[1]) == 1
        horizontal = cell[1] == position[1] and abs(cell[0]-position[0]) == 1
        if vertical or horizontal:
            adjacentCells.append(cell)

    nextCell = random.choice(adjacentCells)
    return nextCell

def runABunch(n, size):
    for i in range(0,n):
        prolog = Prolog()
        prolog.consult("wumpusWorld.pl")

        list(prolog.query("initPredicates()"))

        world = worldBuilder.generateWorld(size, size, 0, 0)
        worldBuilder.printWorld(world)
        worldBuilder.assumeWorld(prolog, world)
        prolog.assertz("cell(1,1)")
        prolog.assertz("width(%d)" % size)
        prolog.assertz("height(%d)" % size)

        result = startGame(prolog)

        print(str(result))

        del prolog


if __name__ == '__main__':
    size = int(sys.argv[1])
    runABunch(10, size)

    #
    # size = int(sys.argv[1])
    # fileName = sys.argv[2]
    # prolog = Prolog()
    # prolog.consult("wumpus-world.pl")
    # if fileName == 'random':
    #     world = worldBuilder.generateWorld(size, size, 0, 0)
    # else:
    #     world = worldBuilder.genWorldFromTxt(fileName)
    # worldBuilder.printWorld(world)
    # worldBuilder.assumeWorld(prolog, world)
    # prolog.assertz("cell(1,1)")
    # prolog.assertz("width(%d)" % size)
    # prolog.assertz("height(%d)" % size)
    #
    #
    # startGame(prolog)
    #
    # print(shortestPath((1,1), (4,4), [(1,1),(2,1),(3,1),(4,1),(4,2),(2,2),(2,3),(2,4),(3,4),(4,4),(4,3)]))
