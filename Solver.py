# Template for the algorithm to solve a Futoshiki. Builds a recursive backtracking solution
# that branches on possible values that could be placed in the next empty cell. 
# Initial pruning of the recursion tree - 
#       we don't continue on any branch that has already produced an inconsistent solution
#       we stop and return a complete solution once one has been found

import pygame, Snapshot, Cell, Futoshiki_IO

def solve(snapshot, screen):
    # display current snapshot
    pygame.time.delay(100)
    Futoshiki_IO.displayPuzzle(snapshot, screen)
    pygame.display.flip()
    # if current snapshot is complete ... return a value

    if isComplete(snapshot) and checkConsistency(snapshot):
    	return True
    
    
    # if current snapshot not complete ...
    if not isComplete(snapshot):
        # get next empty cell with the least number of possibilities
        next_cell = snapshot.unsolvedCells()[0]
        # newsnapshot = ....clone current snapshot and update the cell with the value 
        new_snapshot = snapshot.clone()
        # update the set of possibilities for each empty cell in the new snapshot
        update_possibilities(new_snapshot)
        # for each value in the next cell's possibles list:
        for possibility in next_cell.possibles:
            # set next_cell's value to the first possibility in its list.
            new_snapshot.setCellVal(next_cell.row, next_cell.col, possibility)
            # update animation
            pygame.event.pump()
            pygame.display.flip()

            # if new snapshot is consistent, perform recursive call to solve
            if checkConsistency(new_snapshot):
                success = solve(new_snapshot, screen)
                if success: 
                    return True
    
    # if we get to here no way to solve from current snapshot
    return False

def update_possibilities(snapshot):
    """
    This function determines all possible values an unsolved cell could take. 
    1. It removes possible values that are already in the row or column of the cell.
    2. It removes possibilities that do not comply with inequality signs.
    3. It excludes max and min possible values if there is an inequality sign.
    4. It cross-references with other cells' possibilities ...
        by seeing if there is 1 possibility that remains that can go in the cell.
        (e.g. cell in consideration can be a 2, but not other cell in row can be a 2, thus
        the cell must be a 2 for the row to be valid.)
    
    """
    # iterate over all unsolved cells
    for cell in snapshot.unsolvedCells():
        # Check if any other values in row or column
        # (i.e. column and row exclusions)
        row = snapshot.cellsByRow(cell.row)
        col = snapshot.cellsByCol(cell.col)

        row_vals = []
        col_vals = []
        for j in range(snapshot.rows):
            row_vals.append(row[j].getVal())
            col_vals.append(col[j].getVal())

        new_possibilities = list(set(cell.getPossibilities()).difference(set([i for i in row_vals if i != 0])))
        cell.setPossibilities(new_possibilities)
        new_possibilities = list(set(cell.getPossibilities()).difference(set([i for i in col_vals if i != 0])))
        cell.setPossibilities(new_possibilities)

        ## Updating forced possibilities given the constraints...

        # if there is a condition involving that cell:
        constraints = snapshot.getConstraints()
        for c in constraints:
            new_possibilities = cell.getPossibilities()
            # if cell is the smaller-than cell:
            if c[0][0] == cell.row and c[0][1] == cell.col:
                bigger_cell = snapshot.cells[c[1][0]][c[1][1]]
                # if there is a value that it must be smaller than:
                if bigger_cell.getVal() != 0:
                    # can only put smaller than the constraint values in that cell
                    new_possibilities = [i for i in range(1,bigger_cell.getVal())]
                
                # exclusion of max values (if the cell must be smaller than another)
                elif snapshot.rows in new_possibilities:
                    # else no constraint value, remove max possible value from the possibilites.
                    new_possibilities.remove(snapshot.rows)
                # update possibilites
                cell.setPossibilities(new_possibilities)
            
            # if cell is the larger-than cell:
            if c[1][0] == cell.row and c[1][1] == cell.col:
                smaller_cell = snapshot.cells[c[0][0]][c[0][1]]
                # if there is a value that it must be greater than:
                if smaller_cell.getVal() != 0:
                    # can only put larger than the constraint values in that cell
                    new_possibilities = [i for i in range(smaller_cell.getVal() + 1,snapshot.rows + 1)]
                
                # exclusion of min values (if the cell must be greater than another)
                elif 1 in new_possibilities:
                    # else no constraint value, remove min possible value from the possibilites.   
                    new_possibilities.remove(1)
                # update possibilites 
                cell.setPossibilities(new_possibilities)

        # Check if there are any possibilities that are found in that one cell but none others in the row
        new_possibilities = cell.getPossibilities()
        # if there is more than one possibility in cell
        if len(new_possibilities) > 1:
            # look at all cell in row that are not current cell in consideration
            for row_cell in snapshot.cellsByRow(cell.row):
                # if row cell not the current cell
                if row_cell != cell:
                    # work out difference in possibilities.
                    # if there is only one cell in row that can be, say, 1, then it should only have that posibility.
                    new_possibilities = list(set(new_possibilities).difference(set(row_cell.getPossibilities())))
                # there is no exclusion on row
                if len(new_possibilities) == 0:
                    break
            # if there is an exclusion, make that its one and only posibility.       
            if len(new_possibilities) == 1:
                cell.setPossibilities(new_possibilities)

        # Check if there are any possibilities that are found in that one cell but none others in the column
        new_possibilities = cell.getPossibilities()
        # if there is more than one possibility in cell
        if len(new_possibilities) > 1:
            # look at all cell in row that are not current cell in consideration
            for col_cell in snapshot.cellsByCol(cell.col):
                # if row cell not the current cell
                if col_cell != cell:
                    # work out difference in possibilities.
                    # if there is only one cell in row that can be, say, 1, then it should only have that posibility.
                    new_possibilities = list(set(new_possibilities).difference(set(col_cell.getPossibilities())))
                # there is no exclusion on row
                if len(new_possibilities) == 0:
                    break
            # if there is an exclusion, make that its one and only posibility.       
            if len(new_possibilities) == 1:
                cell.setPossibilities(new_possibilities)

# Check whether a snapshot is consistent   
def checkConsistency(snapshot):
    """
    This function checks to see if the solution is consistent with the rules of the Futoshiki rules.
    With the Futoshiki rules each number occurs only once in each row and column, and
    no "<" constraints are violated.
    """

    for i in range(snapshot.rows):
        row = snapshot.cellsByRow(i)
        col = snapshot.cellsByCol(i)

        row_vals = []
        col_vals = []
        for j in range(snapshot.rows):
            row_vals.append(row[j].getVal())
            col_vals.append(col[j].getVal())
        
        if len(set([i for i in row_vals if i != 0])) != len([i for i in row_vals if i != 0]) or \
            len(set([i for i in col_vals if i != 0])) != len([i for i in col_vals if i != 0]):
            return False 

    for c in snapshot.constraints:
        cell_1 = snapshot.cells[c[0]][c[1]].getVal()
        cell_2 = snapshot.cells[c[2]][c[3]].getVal()
    
        if cell_1 > 0 and cell_2 > 0:
            if cell_1 >= cell_2:
                return False

    return True

# Check whether a puzzle is solved. 
# return true if the Futoshiki is solved, false otherwise
def isComplete(snapshot):
    """
    This function checks to see if the Futoshiki puzzle is complete. 
    Complete being if all cells are full (i.e. all the values of the cells 
    are > 0)
    """ 

    num_full_cell = 0

    for row in snapshot.cells:
        for cell in row:
            if cell.getVal() == 0:
                return False
        
    return True


