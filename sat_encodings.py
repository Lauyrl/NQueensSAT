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

#--- Binary
def at_most_one_binary(X, N, s_base):
    """ 
    For each variable set X, implement a logical bit string long enough to encode |X| values, 
    whose value will represent the index of the variable that is true.
    Each assignment of bits can represent at most one variable.
    """
    clauses = []

    K = (N-1).bit_length() # = ceil(log_2(N)): minimum bits needed to represent |X| values
    for i in range(N):
        # For each variable, build the clauses to enfore that, if that variable were true,
        # the utility variables representing the bit string should match the bits of that variable's index
        for k in range(K):
            bit = (i >> k) & 1  # get k-th bit of a variable's idex

            if (bit == 1):
                clauses.append([-X[i], s_base+k])
            else:
                clauses.append([-X[i], -(s_base+k)])

    return clauses, s_base+K

#--- Commander
GROUP_WIDTH = 3

def at_most_one_commander(X, N, s_base):
    """
    Split variables into small (!) groups, and provide a 'commander' variable for each group.
    A commander is True if any variable in its' group is True.
    Intra-group AMO can be trivially (!) enforced via pairwise clauses.
    Inter-group AMO is then enforced by enforcing AMO among their commanders.
        Commanders can be further split into groups, enabling resursive Commander encodings
    """
    clauses = []

    _, s_base = at_most_one_commander_recurse(X, s_base, clauses)

    return clauses, s_base

def exactly_one_commander(X, N, s_base):
    """
    Integrate ALO shortcut by enforcing it upon the top-level commanders and letting logic propagate downwards
    """
    clauses = []

    top_commanders, s_base = at_most_one_commander_recurse(X, s_base, clauses)
    top_level_alo = at_least_one_common(top_commanders, len(top_commanders))

    clauses.append(top_level_alo)

    return clauses, s_base

def at_most_one_commander_recurse(X, s_base, clauses):
    # When recursion begins with enough variables for only 1 group, no longer need recursive encodings,
    # because we no longer need to enforce inter-group AMO
    if (len(X) <= GROUP_WIDTH):
        clauses.extend(at_most_one_commander_group(X, None))
        return X, s_base

    commanders = []
    n_groups = math.ceil(len(X)/GROUP_WIDTH) # consider 1 or 2 left-over variables their own groups

    for g in range(n_groups):
        commander = s_base
        commanders.append(commander)

        s_base += 1   # increment base for next commanders

        group = X[g*GROUP_WIDTH : (g+1)*GROUP_WIDTH]
        clauses.extend(at_most_one_commander_group(list(group), commander))

    # Create encodings recursively for the commanders, let recursive call relay the updated base
    top_commanders, s_base = at_most_one_commander_recurse(commanders, s_base, clauses)

    # Important for tracking s_i after recursion
    return top_commanders, s_base

def at_most_one_commander_group(X, commander):
    pairwise_clauses = []

    if (len(X) == 1): 
        if (commander):
            # Enforce the defined properties of the commander variable
            pairwise_clauses.append([-X[0], commander])

            # Reverse relationship only useful for propagating ALO logic
            pairwise_clauses.append([-commander, X[0]])

    if (len(X) == 2):
        if (commander):
            # Enforce the defined properties of the commander variable
            pairwise_clauses.append([-X[0], commander])
            pairwise_clauses.append([-X[1], commander])

            # Reverse relationship only useful for propagating ALO logic
            pairwise_clauses.append([-commander, X[0], X[1]])

        # Pairwise AMO within the group
        pairwise_clauses.append([-X[0], -X[1]])
    
    if (len(X) == 3):
        if (commander):
            # Enforce the defined properties of the commander variable
            pairwise_clauses.append([-X[0], commander])
            pairwise_clauses.append([-X[1], commander])
            pairwise_clauses.append([-X[2], commander])

            # Reverse relationship only useful for propagating ALO logic
            pairwise_clauses.append([-commander, X[0], X[1], X[2]])

        # Pairwise AMO within the group
        pairwise_clauses.append([-X[0], -X[1]])
        pairwise_clauses.append([-X[1], -X[2]])
        pairwise_clauses.append([-X[2], -X[0]])

    return pairwise_clauses
