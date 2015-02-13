# TODO: should calculate variances beforehand
def Calc_Vars(M, n):
    
    rows,cols = M.shape
    var = np.zeros((rows, cols))
    
    for i in range(rows):
        
        p_i = sum(M[i])
        
        for j in range(cols):
            
            if i == j:
                
                var[i][j] = n * ( -2 * p_i**2 + 8 * p_i**3 - 6 * p_i**4) +\
                            n**3 * (4 * p_i**3 - 4 * p_i**4) +\
                            n**2 * (2 * p_i**2 - 12 * p_i**3 + 10 * p_i**4)
            else:
                
                p_j = sum(M[j])
                var[i][j] = n**3 * (p_i**2 * p_j + p_i * p_j**2 - 4 * p_i**2 * p_j**2) +\
                            n**2 * (p_i * p_j + 10 * p_i**2 * p_j**2 - 3 * ( p_i**2 * p_j + p_i * p_j**2)) +\
                            n * (-p_i * p_j - 6 * p_i**2 * p_j**2 + 2 * (p_i**2 * p_j + p_i * p_j**2))
    
    return var