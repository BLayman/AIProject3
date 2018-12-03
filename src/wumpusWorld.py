from pyswip.prolog import Prolog
from pyswip.easy import registerForeign
import worldBuilder
import random
import math
import sys
from collections import Counter

# Begins the game starting at positon (1,1) and finishing when we have either
# died or have found the gold and climbed out.
def startGame(prolog):
    points = 0      # keeps track of points
    outcome = 'Won' # used for returning result, default is 'Won'

    startPosition = (1,1)
    position = startPosition
    direction = 1 # up=0, right=1, down=2, left=3

    # Initiate prolog information by visiting our starting position
    list(prolog.query("visit(%s,%s,%s)" % (position[0],position[1],direction)))

    path = []

    while(True):
        print("Position: " + str(position))
        # to make useful inference, we first gather information stored in our
        # knowledge base (KB), in this case using logical predicates that we
        # defined and maintain in Prolog.
        unvisitedCellsDict = list(prolog.query("isUnvisitedSafe(X,Y)"))
        unvisitedCells = toTupleList(unvisitedCellsDict)

        visitedCellsDict = list(prolog.query("visitedInBounds(X,Y)"))
        visitedCells = toTupleList(visitedCellsDict)

        # (1) Check whether our current position causes us to meet our demise...
        deadFromPit = list(prolog.query("hasPit(%s,%s)" % position))
        deadFromWumpus = list(prolog.query("dieFromWumpus(%s,%s)" % position))

        # queries that return an item in the list evaluate to true
        if(len(deadFromPit) != 0):
            print("Died from pit!")
            outcome = 'Died in Pit'
            points += -1000
            return (points, len(list(prolog.query("visitedInBounds(X,Y)"))), outcome)
        if(len(deadFromWumpus) != 0):
            print("Died from wumpus!")
            outcome = "Died from Wumpus"
            points += -1000
            return (points, len(list(prolog.query("visitedInBounds(X,Y)"))), outcome)

        # (2) Check whether we are current lucky enough to be on the gold...
        gold = len(list(prolog.query("foundGlitter(X,Y)"))) > 0

        # if we are...
        if gold:
            print("Found gold!")

            # prematurely award our 1000 points. While we technically only get
            # the points for leaving the pit with the gold, we can award them
            # here because our algorithm guarantees we can make it back out
            # alive (kept track of safe cells since we started).
            points += 1000

            # now we need to find a path that takes us all the way back...
            pathBackToStart = shortestPath(position, startPosition, visitedCells)
            print("Goal: " + str(startPosition))
            print("Path to start: " + str(pathBackToStart))
            # traverse the path we generated...
            traversalResult = traversePath(prolog,position, direction, pathBackToStart)

            # take the results of our traversal and combine them to our
            # rolling metrics and states.
            position = traversalResult[0]
            direction = traversalResult[1]
            points += traversalResult[2]

            print("Cost to get back to start: " + str(traversalResult[2]))

            # we are now finished because we can climb out of the pit.
            return (points, len(list(prolog.query("visitedInBounds(X,Y)"))), outcome)


        # (3) Check if we have visited all of our safe cells...

        if len(unvisitedCells) == 0:
            # if so, we will first need to try to kill the wumpus in order to
            # create more safe cells.
            print("Could not find any more safe cells, attempting to kill wumpus...")

            # attempt to find the wumpus...
            wumpusList = toTupleList(list(prolog.query("foundWumpus(X,Y)")))
            wumpusKilled = list(prolog.query("scream()"))

            # two potential ways that we can't kill the wumpus to open up space:
            # 1. the wumpus has already been killed, or
            # 2. we haven't descovered enough (2) stenches.
            if len(wumpusList) == 0 or len(wumpusKilled) != 0:
                # if either are the case, just attempt the best move we can...
                nextBestMove = getBestMove(prolog)
                projectedPath = shortestPath(position, nextBestMove, visitedCells)
                traversalResult = traversePath(prolog,position, direction, projectedPath)

                position = traversalResult[0]
                direction = traversalResult[1]
                points += traversalResult[2]

                print("Wumpus could not be found!")
                print("Guessing best move is to %d %d" % nextBestMove)
                print("Goal: " + str(nextBestMove))
                print("Projected path: " + str(projectedPath))
                print("Points so far: " + str(points))
                print("-----------")

                continue

            # otherwise, we can kill the wumus and will
            wumpus = wumpusList[0]

            # to kill the wumpus, we need to find cells that we have visited
            # that will let us be lined up with the wumpus so we can shoot it.
            cellsInRange = []
            for cell in visitedCells:
                if len(list(prolog.query("inBounds(%s,%s)" % (cell[0], cell[1])))) == 0:
                    continue
                if cell[0] == wumpus[0] or cell[1] == wumpus[1]:
                    cellsInRange.append(cell)

            # out of all the cells that meet the criteria of being lined up with
            # the wumpus, we choose the one closest to our current position to
            # minimize travel cost.
            shootFrom = closestCell(position, cellsInRange)

            # we now compute the path to take to get to this cell that we plan
            # to shoot from
            pathToShootPosition = shortestPath(position, shootFrom, visitedCells)

            # now we traverse along the path
            traversalResult = traversePath(prolog,position, direction, pathToShootPosition)

            # we update state and metric information from the traversal
            position = traversalResult[0]
            direction = traversalResult[1]
            points += traversalResult[2]

            # lastly, we turn to face the wumpus
            direction = directionToFaceNext(position, wumpus)

            # now we kill the wumpus with our arrow, incurring the -10 cost.
            list(prolog.query("killWumpus()"))
            points += -10

            # print out information about our wumpus murder
            print("Wumpus at: " + str(wumpus))
            print("Cells in range: " + str(cellsInRange))
            print("Closest cell to shoot from: " + str(shootFrom))
            print("Cost to get to cell: " + str(traversalResult[2]))
            print("Cost to shoot arrow: " + str(-10))
            print("End at: " + str(position))
            print("-----------")
            continue

        # (4) If we have not visited all of our safe cells, we need to find
        # a nearby unvisited safe cell to visit.


        # get the closest unvisited, safe cell to our current position.
        currentGoal = closestCell(position, unvisitedCells)
        # compute the path we need to take to get to it.
        projectedPath = shortestPath(position, currentGoal, visitedCells)
        # traverse along the path, storing results of our traversal
        traversalResult = traversePath(prolog,position, direction, projectedPath)

        # update our state and metrics with traversal results
        position = traversalResult[0]
        direction = traversalResult[1]
        points += traversalResult[2]

        # print information about our movement
        print("Goal: " + str(currentGoal))
        print("Projected path: " + str(projectedPath))
        print("Points for: " + str(points))
        print("-----------")

    return(points, len(list(prolog.query("visitedInBounds(X,Y)"))), outcome)

def getBestMove(prolog):
    l = list(prolog.query("dangerBreeze(X,Y, NX, NY)"))
    #Set of positions for breezes
    breezeSet = set()
    for cellPair in l:
        unkownPos = (cellPair["X"], cellPair["Y"])
        dangerZone = (cellPair["NX"], cellPair["NY"])
        breezeSet.add((unkownPos, dangerZone))
    l = list(prolog.query("dangerStench(X,Y,NX,NY)"))
    #Set of positions for stenches
    stenchSet = set()
    for cellPair in l:
        unkownPos = (cellPair["X"], cellPair["Y"])
        dangerZone = (cellPair["NX"], cellPair["NY"])
        stenchSet.add((unkownPos, dangerZone))
    #Combine the sets as lists to account for wumpus and breeze at certain locations
    total = list(breezeSet) + list(stenchSet)
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

# Determines the result of traversing along the path, starting at 'position' and
# facing direction 'direction'. The result includes our end position, our end
# direction, and the cost incurred by the path.
def traversePath(prolog, position, direction, path):
    cost = 0 # keep a running total of costs while traversing path
    previousPosition = position
    for cell in path:
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

    # if bumped, just move back.
    if bump:
        position = previousPosition
        cost += 1   # need to negate the cost of the move, since bumps don't have costs.
    return (position, direction, cost)

# Determines the direction we should face if we are standing at the cell
# 'origin' and want to be looking in the direction of cell 'next'. Direction
# values follow the pattern: 0=up, 1=right, 2=down, 3=left.
def directionToFaceNext(origin, next):
    # x-axes are equal
    if(origin[0] == next[0]):
        if(origin[1] < next[1]):
            # we are below next
            return 0
        else:
            # we are above next
            return 2
    else:
        if(origin[0] < next[0]):
            # we are to the left of next
            return 1
        else:
            # we are to the right of next
            return 3

# Determines the closest cell to start in the cellList
def closestCell(start, cellList):
    # state information about the current lowest distance cell.
    minDist = math.inf
    min = (None, None)

    for cell in cellList:
        dist = abs(start[0]-cell[0]) + abs(start[1]-cell[1])

        # if the current cell has a smaller distance than the min found so far,
        # then it is the new minimum.
        if dist < minDist:
            minDist = dist
            min = cell

    # return the minimum found after traversing all cells in the list
    return min

# Determines the shortest path from cell 'start' to cell 'end' by only searching
# through 'visited' cells. Uses a breadth first search algorithm to guarantee
# shortest path. By going through visited cells, we will not run the risk of
# hitting an unsafe cell on our way to a safe one.
def shortestPath(start, end, visited):
    marked = [start]
    frontier = [start] # list treated as a queue.
    # a dictionary used for keeping track of what cell each cell was found from
    # in order to piece together a path once we found our 'end' cell.
    parents = {}

    while len(frontier) != 0:
        cell = frontier[0]
        del frontier[0]

        # here we check if the current cell pulled off the queue is the 'end'
        # goal cell, and if so we construct a path given our search results.
        if isNeighbor(end, cell):
            parents[end] = cell
            path = []

            iterator = end
            while(iterator != start):
                path.append(iterator)
                iterator = parents[iterator]
            path.reverse()
            return path

        # if the cell is not our goal cell, then we just add our neighbors to
        # the queue and proceed with typical BFS.
        for neighbor in neighbors(cell, visited):
            if neighbor in marked:
                continue
            marked.append(neighbor)
            frontier.append(neighbor)
            parents[neighbor] = cell

# Returns any cells found in cellList that are neighbors of cell.
def neighbors(cell, cellList):
    neighbors = []
    for c in cellList:
        if isNeighbor(cell, c):
            neighbors.append(c)
    return neighbors

# Returns true if the two cells are neighbors.
def isNeighbor(cellA, cellB):
    # cells are adjacent vertically if same x's and y's are one apart.
    vertical = cellA[0] == cellB[0] and abs(cellA[1]-cellB[1]) == 1
    # cells are adjacent horizontally if same y's and x's are one apart.
    horizontal = cellA[1] == cellB[1] and abs(cellA[0]-cellB[0]) == 1
    # neighbors if either type of adjacency is true
    return vertical or horizontal

# Prolog queries are returned as dictionaries, so this is a utility function
# that lets query results with the format {X=*, Y=*} be turned into tuples like
# (X,Y)
def toTupleList(cellDict):
    tlist = []
    for cell in cellDict:
        x = cell['X']
        y = cell['Y']
        tlist.append((x,y))
    return list(set(tlist))

# Prints our game result in a nicely formatted manner.
def printGameOutput(result):
    print("\n##################")
    print("GAME HAS FINISHED!")
    print("result:  " + str(result[2]))
    print("score:   " + str(result[0]))
    print("entered: " + str(result[1]))
    print("##################\n")

# Run n games with map of dimension 'size'x'size'.
def runMultipleGames(n, size):
    for i in range(0,n):
        # Create prolog, consult with our KB file.
        prolog = Prolog()
        prolog.consult("wumpusWorld.pl")

        # Clear any left-over predicates from previous run...
        list(prolog.query("initPredicates()"))

        # Create our random world
        world = worldBuilder.generateWorld(size, size, 0, 0)
        worldBuilder.printWorld(world)
        # Put facts about the world into our knowledge base stored in prolog.
        worldBuilder.assumeWorld(prolog, world)

        # Run the game, save the results.
        result = startGame(prolog)

        # Format the results...
        printGameOutput(result)

        del prolog


if __name__ == '__main__':
    size = int(sys.argv[1])
    fileName = sys.argv[2]

    if fileName == 'random':
        # User selected random games
        runMultipleGames(int(sys.argv[3]), size)
    else:
        # User selected a game from a file
        # Create prolog, consult with our KB file.
        prolog = Prolog()
        prolog.consult("wumpusWorld.pl")

        # Create our world from a textfile
        world = worldBuilder.genWorldFromTxt(fileName)
        worldBuilder.printWorld(world)
        # Put facts about the world into our knowledge base stored in prolog.
        worldBuilder.assumeWorld(prolog, world)

        result = startGame(prolog)

        # Format the results...
        printGameOutput(result)
