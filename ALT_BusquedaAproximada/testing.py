from distancias import *

print(levenshtein_matriz("algoritmo", "algortimo"))
print(levenshtein_reduccion("algoritmo", "algortimo"))
print(levenshtein("algoritmo", "algortimo", 3))
print(levenshtein_matriz("gato", "gaot"))

print(damerau_intermediate_matriz("algoritmo", "algortimo"))
print(damerau_intermediate_matriz("gato", "gaot"))
