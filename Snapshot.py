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
        for row in range(5):
            # Add an empty array that will hold each cell in this row
            self.cells.append([])
            for column in range(5):
                self.cells[row].append(Cell.cell(row, column, 0)) # Append a cell
        self.constraints =[]
        
    def setCellVal(self, i, j, val):
        self.cells[i][j].setVal(val)
        
    def getCellVal(self, i,j):
        return self.cells[i][j].getVal()
    
    def setConstraint(self, coords):
        self.constraints.append(coords)
    
    def getConstraints(self): 
        constraints = []  
        for c in self.constraints:
            coords1 = (c[0], c[1])
            coords2 = (c[2], c[3])
            constraints.append((coords1,coords2))
        return constraints
        
    def cellsByRow(self,row):
        return self.cells[row]
    
    def cellsByCol(self,col):
        column = []
        for row in range(5):
            column.append(self.cells[row][col])
        return column
    
    def unsolvedCells(self):
        unsolved = []
        for row in range(5):
            for col in range(5):
              if self.cells[row][col].getVal() == 0 :
                 unsolved.append(self.cells[row][col])
        return sorted(unsolved,key = lambda x: len(x.getPossibilities()))
        
    def clone(self):
        clone = snapshot()
        for row in range(5):
            for col in range(5):
              clone.setCellVal(row,col,self.getCellVal(row,col))
        for c in self.constraints:     
            clone.setConstraint(c)
        return clone
