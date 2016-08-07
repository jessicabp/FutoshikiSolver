# Utility to read Futoshiki puzzles from text files, and display Futoshiki puzzles to a screen.

import Snapshot
import pygame
import Solver



# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
red      = (255,    0,   0)

# This sets the width and height of each grid location
width=60
height=60
 
# This sets the margin between each cell
margin=30

def loadPuzzle(puzzlefile):
    file = open(puzzlefile)
    content = file.readlines()
    newsnapshot = Snapshot.snapshot()
    rownumber = 0

    cells = []
    for row in range(5):
        # Add an empty array that will hold each cell in this row
        cells.append([])
        for column in range(5):
            cells[row].append(0)  # Append a cell

    for rownumber in range(5):
        newrow = [int(x) for x in content[rownumber].split()]
        for columnnumber in range(5):
            newsnapshot.setCellVal(rownumber, columnnumber, newrow[columnnumber])

            cells[rownumber][columnnumber] = newrow[columnnumber]

    constraints = content[5:]
    for c in constraints:
        newconstraint = [int(x) for x in c.split()] 
        newsnapshot.setConstraint(newconstraint)
    file.close()

    # set initial possibilities for all cells
    for row in range(5):
        for col in range(5):
            newsnapshot.setPossibilities(row, col, Solver.getPossibleCellValues(newsnapshot, row, col))

    return newsnapshot
        
def displayPuzzle(snapshot, screen):
    # Set the screen background
    screen.fill(black)
 
    # Draw the grid squares
    color = white
    myfont = pygame.font.SysFont("Comic Sans MS", 30)
    for row in range(5):
        for column in range(5):       
           pygame.draw.rect(screen,color,[(margin+width)*column+margin,(margin+height)*row+margin,width,height])
           printVal = snapshot.getCellVal(row, column)
           if printVal == 0:
               label = myfont.render(".", 1, black)
           else:
               label = myfont.render(str(printVal), 1, black)
           screen.blit(label, ((margin+width)*column+margin+25,(margin+height)*row+margin+10))
    myfont = pygame.font.SysFont("Comic Sans MS", 50)
    for c in snapshot.getConstraints():
        r1 = c[0][0]
        c1 = c[0][1]
        r2 = c[1][0]
        c2 = c[1][1]
        if (c1 < c2):
            label = myfont.render("<", 1, red)
            screen.blit(label, ((margin+width)*(c1+1)+10,(margin+height)*r2+20))
        elif (c2 < c1):
            label = myfont.render(">", 1, red)
            screen.blit(label, ((margin+width)*(c2+1)+10,(margin+height)*r2+20))
        elif (r1 < r2):
            label = myfont.render("^", 1, red)
            screen.blit(label, ((margin+width)*c1+margin+15,(margin+height)*(r1+1)-5))
        else:
             label = myfont.render("v", 1, red)
             screen.blit(label, ((margin+width)*c1+margin+15,(margin+height)*(r2+1)-25))
        
        
        
