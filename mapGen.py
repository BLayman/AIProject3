import random
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign

# Creates a world instance, which is just a 2D matrix of dictionaries that have pairs:
# - wumpus, for whether a wumpus exists at the coordinate (boolean)
# - gold, for whether a gold exists at the coordinate (boolean)
# - pit, for whether a pit exists at the coordinate (boolean)
def generateWorld(width, height, startX, startY):
    genWorld = [[{'wumpus':False, 'gold':False, 'pit':False} for x in range(width)] for y in range(height)]
    
    # generate wumpus coordinates...
    wumpusX = random.randint(0, width - 1)
    wumpusY = random.randint(0, height - 1)
    # don't allow the wumpus to be at the start position...
    while wumpusX == startX and wumpusY == startY:
        wumpusX = random.randint(0, width - 1)
        wumpusY = random.randint(0, height - 1)

    # generate gold coordinates...
    goldX = random.randint(0, width-1)
    goldY = random.randint(0, height-1)
    # don't allow the gold to be at the start position...
    while goldX == startX and goldY == startY:
        goldX = random.randint(0, width-1)
        goldY = random.randint(0, height-1)

    # set the pit positions with the predefined likelihood:
    pitRate = .2
    for x in range(0, width):
        for y in range(0, height):
            # assign information to each position...
            genWorld[y][x]['wumpus'] = wumpusX == x and wumpusY == y
            genWorld[y][x]['gold'] = goldX == x and goldY == y
            genWorld[y][x]['pit'] = random.uniform(0, 1) < pitRate and not (x==startX and y==startY)

    return genWorld

def genWorldFromTxt(fileName):
    theMap = []
    with open(fileName, 'r') as txtMap:
        for line in txtMap:
            temp = []
            line = line.replace("\n", '')
            line = line.split(',')
            for string in line:
                cell = {'pit': False, 'gold': False, 'wumpus': False}
                if 'P' in string:
                    cell['pit'] = True
                elif 'G' in string:
                    cell['gold'] = True
                elif 'W' in string:
                    cell['wumpus'] = True
                temp.append(cell)
            theMap.append(temp)
    returnMap = []
    while len(theMap) > 0:
        returnMap.append(theMap.pop())
    return returnMap


# Given a world and a prolog instance, this will assign the entities from the world into prolog.
def assumeWorld(prolog, world):
    height = len(world)
    width = len(world[0])

    for x in range(0, width):
        for y in range(0, height):
            cell = world[y][x]
            
            if(cell['wumpus']):
                prolog.assertz("hasWumpus(%s,%s)" % (x+1,y+1))
            if(cell['gold']):
                prolog.assertz("hasGold(%s,%s)" % (x+1,y+1))
            if(cell['pit']):
                prolog.assertz("hasPit(%s,%s)" % (x+1,y+1))
  
# Utility function for displaying a given world (2D matrix of dicts) in standard out.                
def printWorld(world):
    width = len(world)
    height = len(world[0])
    
    for y in range(0, height):
        print("+----"*width+"+")        
        line = ""        
        for x in range(0, width):
            tile = "|"            
            cell = world[-(y + 1)][x]
            
            if cell['wumpus']:
                tile += "W"
            if cell['gold']:
                tile += "G"
            if cell['pit']:
                tile += "P"
            tile = tile.ljust(5)

            line += tile
        print(line+"|")            
    print("+----"*width+"+") 

# Main method for testing the map
if __name__ == '__main__':
    # Create a new blank prolog instance (don't need to consult file for testing this)    
    prolog = Prolog()    
    
    # Generate a new world instance
    world = generateWorld(10, 10, 0, 0)
    # Put that world into our prolog instance
    assumeWorld(prolog, world)

    # Now we can check how the world looks
    
    # First, print the world on standard out...
    printWorld(world)
    
    # Now, print the prolog-queried locations for different percepts and items...
    # pits 
    print("Pits: \n" + str(list(prolog.query("hasPit(X,Y)"))))
    # gold   
    print("Gold: \n" + str(list(prolog.query("hasGold(X,Y)"))))
    # wumpus
    print("Wumpus: \n" + str(list(prolog.query("hasWumpus(X,Y)"))))
    # breezes
    print("Breeze: \n" + str(list(prolog.query("hasBreeze(X,Y)"))))
    # glitters
    print("Glitter: \n" + str(list(prolog.query("hasGlitter(X,Y)"))))
    # stenches
    print("Stench: \n" + str(list(prolog.query("hasStench(X,Y)"))))
    
