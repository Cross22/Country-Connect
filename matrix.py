# A simple matrix
# This matrix is a list of lists
# Column and row numbers start with 0
# Obtained from http://bytes.com/topic/python/answers/594203-please-how-create-matrix-python
 
class Matrix(object):
    def __init__(self, rows, cols):
        self.cols = cols
        self.rows = rows
        # initialize matrix and fill with zeroes
        self.matrix = []
        for i in range(rows):
            ea_row = []
            for j in range(cols):
                ea_row.append(0)
            self.matrix.append(ea_row)
        
        self.last_row = rows - 1
        self.last_col = cols - 1
 
    def setitem(self, row, col, v):
        self.matrix[row][col] = v
 
    def getitem(self, row, col):
        return self.matrix[row][col]
    
    def getindex(self, v):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.getitem(i,j) == v:
                    return (i,j)        
    
    def __iter__(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield (self.matrix, row, col)      
 
    def __repr__(self):
        outStr = ""
        for i in range(self.rows):
            outStr += 'Row %s = %s\n' % (i, self.matrix[i])
        return outStr
  
# this runs the main function if this script is called to run.
#  If it is imported as a module, we don't run the main function.  
if __name__ == "__main__":    
    a = Matrix(4,5)
    a.setitem(2,3,55.75)
    print a
    print a.getitem(2,-3)
    print a.cols
    #a.setitem(1,2,'19.1')
    #print a
    #print a.getindex(55.75)    
    
    #for i,r,c in a:
    #    print "r: " + str(r)
    #    print "c: " + str(c)
    #    print "value: " + str(i[r][c])