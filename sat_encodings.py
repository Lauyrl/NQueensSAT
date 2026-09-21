import math

########## ALO ##########
def at_least_one_common(X, N):
    return list(X)

########## AMO ##########
#--- Sequenatial
def at_most_one_sequential(X, N, s_base):
    """
    Implement |X|-1 utility variables (s_i) that act as cummulative 'switches',
    where s_i must be True if any variable between [x_1, x_i] is True, this cummulative property is enforced via the clauses:
        (1): if any variable before x_i were True, s_i must be True
        (2): if x_i itself were True, s_i must be True
    s_i is then utilized to enforce AMO via the clause:
        (3): if x_i were True, every variable before it must be False
    """
    clauses = []

    # Special case i = 1: 
    #   s_(i-1) = s_0 is always False by convention, therefore (1) and (3) are always True, 
    #   exclude those clauses for simplicity
    clauses.append([-X[0], s_base])

    for i in range(1, N-1):
        clauses.append([-(s_base+i-1), s_base+i]) # (1)
        clauses.append([-X[i], s_base+i])         # (2)
        clauses.append([-X[i], -(s_base+i-1)])    # (3)

    # Special case i = N:
    #   As s_N would be the last switch, no other switch logically depends on it, and (3) is enough to 
    #   enforce AMO upon x_N, therefore, (1) and (2) are excluded for simplicity
    s_N = s_base+N-1 # shift by 1 as s_base is 0-indexed
    clauses.append([-X[N-1], -(s_N-1)])

    return clauses, s_N
