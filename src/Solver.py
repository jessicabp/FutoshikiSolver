# Template for the algorithm to solve a Futoshiki. Builds a recursive backtracking solution
# that branches on possible values that could be placed in the next empty cell. 
# Initial pruning of the recursion tree - 
#       we don't continue on any branch that has already produced an inconsistent solution
#       we stop and return a complete solution once one has been found

import pygame, Snapshot, Cell, Futoshiki_IO


def solve(snapshot, screen):
    # display current snapshot
    pygame.time.delay(200)
    Futoshiki_IO.displayPuzzle(snapshot, screen)
    pygame.display.flip()

    # if current snapshot is complete return True
    if isComplete(snapshot):
        return True

    # update the possible values for unsolved cells - if any cell now has no possible values, return False as the solution is not solvable
    for cell in snapshot.unsolvedCells():
        row = cell.getRow()
        col = cell.getCol()
        if not snapshot.setPossibilities(row, col, getPossibleCellValues(snapshot, row, col)):
            return False

    # if current snapshot not complete ...
    # get next empty cell(s) - returns list of cells with only one possibility, or list of cell with fewest possible values
    emptycelldata = getNextCell(snapshot)

    # if each cell only has one possible value, complete them all at once
    # the possibilities for each of these cells will not need updating as it is already a single value
    # if placing the single possible value in these cells creates an inconsistent solution, return False
    if emptycelldata[0][0] == 1:
        newsnapshot = snapshot.clone()
        for cell in emptycelldata:
            cellrow = cell[1]
            cellcol = cell[2]
            value = cell[3][0]
            newsnapshot.setCellVal(cellrow, cellcol, value)
        # if new snapshot is consistent perform recursive call to solve, return True if solved
        if checkConsistency(newsnapshot):
            if solve(newsnapshot, screen):
                return True
        else:
            return False

    else:
        cellrow = emptycelldata[0][1]
        cellcol = emptycelldata[0][2]
        possiblevalues = emptycelldata[0][3]
        # for possible values for the cell clone current snapshot and update the cell with the value
        for value in possiblevalues:
            newsnapshot = snapshot.clone()
            newsnapshot.setCellVal(cellrow, cellcol, value)
            newsnapshot.setPossibilities(cellrow, cellcol, [value])
            # if new snapshot is consistent perform recursive call to solve, return True if solved
            if checkConsistency(newsnapshot):
                if solve(newsnapshot, screen):
                    return True

    # if we get to here there is no way to solve from current snapshot
    return False


# Check whether a snapshot is consistent, i.e. all cell values comply
# with the Futoshiki rules (each number occurs only once in each row and column,
# no "<" constraints violated).

def checkConsistency(snapshot):
    # check numbers (except 0) only occur once in each row and column
    for rowOrCol in range(5):
        rowCells = snapshot.cellsByRow(rowOrCol)
        rowValues = []
        for cell in rowCells:
            rowValues.append(cell.getVal())
        colCells = snapshot.cellsByCol(rowOrCol)
        colValues = []
        for cell in colCells:
            colValues.append(cell.getVal())
        for value in range(1, 6):
            if rowValues.count(value) > 1 or colValues.count(value) > 1:
                return False

    # check all constraints are met
    constraints = snapshot.getConstraints()
    for coord in constraints:
        smaller = snapshot.getCellVal(coord[0][0], coord[0][1])
        larger = snapshot.getCellVal(coord[1][0], coord[1][1])
        if smaller != 0 and larger != 0 and smaller >= larger:
            return False
    return True


# Check whether a puzzle is solved.
# return true if the Futoshiki is solved, false otherwise

def isComplete(snapshot):
    if len(snapshot.unsolvedCells()) != 0:
        return False
    return checkConsistency(snapshot)


# Get the next empty cell to find a value for

def getNextCell(snapshot):
    nextcells = snapshot.getLeastPossibilitiesCell()
    if nextcells[0][0] == 1:
        return nextcells
    else:
        nextcellsdata = []
        for cell in nextcells:
            nextcellsdata.append([cell[0], cell[1], cell[2], snapshot.getPossibilities(cell[1], cell[2])])
        return nextcellsdata


# Get a list of valid values for the empty cell

def getPossibleCellValues(snapshot, row, col):
    # if there is already a value in the cell, that is returned as the only possibility
    if snapshot.getCellVal(row, col) != 0:
        return [snapshot.getCellVal(row, col)]

    possiblevalues = snapshot.getPossibilities(row, col)

    # eliminate values already in the cell's row and column
    for cell in snapshot.cellsByRow(row):
        value = cell.getVal()
        if value in possiblevalues:
            possiblevalues.remove(value)
    for cell in snapshot.cellsByCol(col):
        value = cell.getVal()
        if value in possiblevalues:
            possiblevalues.remove(value)

    # find the min/max value the cell can hold based on the constraints, and remove all values below/above that from the possible values
    # this will force the value if there is a chain of one type the same length as the board
    constraints = snapshot.getConstraints()
    for value in range(getMaxValidValue(snapshot, constraints, row, col, 6), 6):
        if value in possiblevalues:
            possiblevalues.remove(value)
    for value in range(1, getMinValidValue(snapshot, constraints, row, col, 1)):
        if value in possiblevalues:
            possiblevalues.remove(value)

    return possiblevalues


# Find the cell's maximum value according to the constraints
# highestPossibleValue is actually one higher than the highest valid value, so it can be used as the upper range limit

def getMaxValidValue(snapshot, constraints, row, col, highestPossibleValue):
    valueToReturn = highestPossibleValue
    for constraint in constraints:
        if constraint[0][0] == row and constraint[0][1] == col:
            newHighValue = snapshot.getCellVal(constraint[1][0], constraint[1][1])
            # if the higher value cell has not been given a value yet
            if newHighValue == 0:
                # recursively call the function to see if there is a run on string of constraints
                newHighValue = getMaxValidValue(snapshot, constraints, constraint[1][0], constraint[1][1], highestPossibleValue - 1)
                # get the highest possible value for the given cell to use if it is higher than the current high value
                potentialHighValue = max(snapshot.getPossibilities(constraint[1][0], constraint[1][1]))
                if potentialHighValue > newHighValue:
                    newHighValue = potentialHighValue
            if newHighValue < valueToReturn:
                valueToReturn = newHighValue
    return valueToReturn


# Find the cell's minimum value according to the constraints

def getMinValidValue(snapshot, constraints, row, col, smallestPossibleValue):
    valueToReturn = smallestPossibleValue
    for constraint in constraints:
        if constraint[1][0] == row and constraint[1][1] == col:
            newLowValue = snapshot.getCellVal(constraint[0][0], constraint[0][1])
            # if the smaller value cell has not been given a value yet
            if newLowValue == 0:
                # recursively call the function to see if there is a run on string of constraints
                newLowValue = getMinValidValue(snapshot, constraints, constraint[0][0], constraint[0][1], smallestPossibleValue + 1)
                # get the lowest possible value for the given cell to use if it is lower than the current low value
                potentialLowValue = min(snapshot.getPossibilities(constraint[1][0], constraint[1][1]))
                if potentialLowValue > newLowValue:
                    newLowValue = potentialLowValue
            if newLowValue > valueToReturn:
                valueToReturn = newLowValue
    return valueToReturn


def getConstrainingCells(snapshot, row, col):
    constraints = snapshot.getConstraints()
    constrainingCells = []
    for constraint in constraints:
        if constraint[0][0] == row and constraint[0][1] == col:
            constrainingCells.append([constraint[1][0], constraint[1][1]])
        elif constraint[1][0] == row and constraint[1][1] == col:
            constrainingCells.append([constraint[0][0], constraint[0][1]])
    return constrainingCells
