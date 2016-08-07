# A snapshot is a point in the computation when 
# the values for some, but possibly not all, cells are known.
# This class has some methods that allow to clone a snapshot (this is useful to produce the 
# next snapshots in the recursion tree), to query the cells in various ways, and to set cells.
# It also has a method that returns a list encoding the inequality constraints that must be satisfied.

import Cell


class snapshot:
    def __init__(self):
        self.rows = 5
        self.columns = 5
        self.cells = []
        self.possibilities = []  # to store possible values for all cells
        for row in range(self.rows):
            # Add an empty array that will hold each cell in this row
            self.cells.append([])
            self.possibilities.append([])
            for column in range(self.columns):
                self.cells[row].append(Cell.cell(row, column, 0))  # Append a cell
                self.possibilities[row].append([1, 2, 3, 4, 5])
        self.constraints = []
        
    def setCellVal(self, i, j, val):
        self.cells[i][j].setVal(val)
        
    def getCellVal(self, i, j):
        return self.cells[i][j].getVal()
    
    def setConstraint(self, coords):
        self.constraints.append(coords)
    
    def getConstraints(self): 
        constraints = []  
        for c in self.constraints:
            coords1 = (c[0], c[1])
            coords2 = (c[2], c[3])
            constraints.append((coords1, coords2))
        return constraints
        
    def cellsByRow(self, row):
        return self.cells[row]
    
    def cellsByCol(self, col):
        column = []
        for row in range(self.rows):
            column.append(self.cells[row][col])
        return column
    
    def unsolvedCells(self):
        unsolved = []
        for row in range(self.rows):
            for col in range(self.columns):
                if self.cells[row][col].getVal() == 0:
                    unsolved.append(self.cells[row][col])
        return unsolved
        
    def clone(self):
        clone = snapshot()
        for row in range(self.rows):
            for col in range(self.columns):
                clone.setCellVal(row, col, self.getCellVal(row, col))
                clone.setPossibilities(row, col, self.getPossibilities(row, col))
        for c in self.constraints:     
            clone.setConstraint(c)
        return clone

    def getPossibilities(self, row, col):
        return list(self.possibilities[row][col])

    def setPossibilities(self, row, col, value):
        if len(value) == 0:
            return False
        self.possibilities[row][col] = value
        return True

    def removePossibility(self, row, col, value):
        if value in self.possibilities[row][col]:
            self.possibilities[row][col].remove(value)

    def getLeastPossibilitiesCell(self):
        cellsToCheck = []
        for cell in self.unsolvedCells():
            cellsToCheck.append([cell.getRow(), cell.getCol()])
        leastPossibilitiesCell = [6]
        singlePossibilitiesCells = []

        for cell in cellsToCheck:
            length = len(self.possibilities[cell[0]][cell[1]])
            if length == 1:
                singlePossibilitiesCells.append([1, cell[0], cell[1], self.possibilities[cell[0]][cell[1]]])
                leastPossibilitiesCell[0] = 1
                cellsToCheck.remove(cell)
            elif length < leastPossibilitiesCell[0]:
                leastPossibilitiesCell = [length, cell[0], cell[1]]

        # find forced values - cannot be done when updating possibilities as it depends on ALL possibilities being up to date
        singlePossibilitiesCells = self.getForcedValues(cellsToCheck, singlePossibilitiesCells)

        if len(singlePossibilitiesCells) > 0:
            return singlePossibilitiesCells
        else:
            return [leastPossibilitiesCell]

    def getForcedValues(self, cellsToCheck, forcedCells):
        for cell in cellsToCheck:
            row = cell[0]
            col = cell[1]

            # get list of possible values for the cell
            availableRowValues = self.getPossibilities(row, col)
            availableColValues = self.getPossibilities(row, col)
            for rowOrCol in range(5):
                # for every other cell in the row, remove that cell's possible values from the list of row values for the selected cell
                if (rowOrCol != col):
                    for value in self.getPossibilities(row, rowOrCol):
                        if value in availableRowValues:
                            availableRowValues.remove(value)

                # for every other cell in the column, remove that cell's possible values from the list of col values for the selected cell
                if (rowOrCol != row):
                    for value in self.getPossibilities(rowOrCol, col):
                        if value in availableColValues:
                            availableColValues.remove(value)

                # if there are no possible values remaining for the selected cell, move to the next cell
                if len(availableRowValues) == 0 and len(availableColValues) == 0:
                    break
            # if there is ony one option for the selected cell value, add it to the list of cells with one available value
            # also set the possibilities for that cell to that value
            if len(availableRowValues) == 1:
                forcedCells.append([1, row, col, availableRowValues])
                self.setPossibilities(row, col, availableRowValues)
            elif len(availableColValues) == 1:
                forcedCells.append([1, row, col, availableColValues])
                self.setPossibilities(row, col, availableColValues)
        return forcedCells