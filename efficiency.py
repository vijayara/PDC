import math

tons = 3
n_line = 3 #number of lines
n_column = 4 #number of  columns
possible_combinations = tons**(3*n_line*n_column)
bits = math.floor(math.log(possible_combinations, 2))
combinations = 2**bits
ratio = combinations/possible_combinations*100
print("Number of bits:\t\t\t", bits)
print("Number of possible combinations:", possible_combinations)
print("Number of combinations:\t\t", combinations)
print("Ratio efficiency:\t\t", ratio)
