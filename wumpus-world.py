from pyswip.prolog import Prolog
from pyswip.easy import registerForeign
import mapGen
import random
import math


def startGame(prolog):

    points = 0

    startPosition = (1,1)

    position = startPosition
    list(prolog.query("visit(%s,%s)" % position))
    direction = 1 # up=0, right=1, down=2, left=3


    path = []

    while(True):

        # check for gold
        gold = len(list(prolog.query("foundGlitter(X,Y)"))) > 0

        if gold:
            print("Found gold!")

            points += 1000

            pathBackToStart = shortestPath(position, startPosition, visitedCells)
            print("Goal: " + str(startPosition))
            print("Path to start: " + str(pathBackToStart))
            traversalResult = traversePath(position, direction, pathBackToStart)

            position = traversalResult[0]
            direction = traversalResult[2]
            points += traversalResult[3]

            print("FINAL POINTS: " + str(points))

            return

        unvisitedCellsDict = list(prolog.query("isUnvisitedSafe(X,Y)"))
        unvisitedCells = toTupleList(unvisitedCellsDict)

        visitedCellsDict = list(prolog.query("visited(X,Y)"))
        visitedCells = toTupleList(visitedCellsDict)

        if len(unvisitedCells) == 0:
            print("Could not find any more safe cells, attempting to kill wumpus...")

            # Kill the wumpus, if we can...

            #
            # FIND THE WUMPUS IF WE CAN
            #
            wumpusList = toTupleList(list(prolog.query("foundWumpus(X,Y)")))

            if len(wumpusList) == 0:
                print("Wumpus could not be found!")
                return

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

            if len(cellsInRange) == 0:
                print("No cell we can shoot the wumpus from!")
                return
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

            traversalResult = traversePath(position, direction, pathToShootPosition)

            position = traversalResult[0]
            direction = traversalResult[2]
            points += traversalResult[3]

            print("Cost to get to cell: " + str(traversalResult[3]))

        print("Position: " + str(position))
        currentGoal = closestUnvisited(position, unvisitedCells)
        print("Goal: " + str(currentGoal))
        projectedPath = shortestPath(position, currentGoal, visitedCells)

        print("Projected path: " + str(projectedPath))



        traversalResult = traversePath(position, direction, projectedPath)

        position = traversalResult[0]
        previousPosition = traversalResult[1]
        direction = traversalResult[2]
        points += traversalResult[3]

        print("delta points: " + str(traversalResult[3]))

        print("-----------")

        list(prolog.query("visit(%s,%s)" % position))
        # revert to 2nd to last position if we bump
        bump = len(list(prolog.query("bump(%s,%s)" % (position[0],position[1])))) > 0

        # if bumped, just move back. Cost of bump already taken into account.
        if bump:
            position = previousPosition


        print(position)

    print(list(prolog.query("visited(X,Y)")))

def traversePath(position, direction, projectedPath):
    cost = 0
    previousPosition = position
    for cell in projectedPath:
        needToFace = directionToFaceNext(position, cell)

        # cost of turning...
        difference = abs(needToFace-direction)
        if difference == 3:
            cost += -1
        else:
            cost += -difference

        direction = needToFace

        # cost of moving...
        cost += -1

        # update position
        previousPosition = position
        position = cell

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




if __name__ == '__main__':
    prolog = Prolog()
    prolog.consult("wumpus-world.pl")
    world = mapGen.genWorldFromTxt('kill-wumpus-map.txt')
    mapGen.printWorld(world)
    mapGen.assumeWorld(prolog, world)
    prolog.assertz("cell(1,1)")

    startGame(prolog)

    #print(shortestPath((1,1), (4,4), [(1,1),(2,1),(3,1),(4,1),(4,2),(2,2),(2,3),(2,4),(3,4),(4,4),(4,3)]))
