import distancias

print(distancias.levenshtein_edicion("ejemplo", "campos"))
print(distancias.levenshtein_edicion("amorcito", "aviador"))
print(distancias.levenshtein_reduccion("amorcito", "aviador"))
print(distancias.levenshtein_cota_optimista("casa", "abad", 5))

print("-------------------------------------------")
print(distancias.levenshtein_matriz("zapato", "patos"))
print(distancias.levenshtein_edicion("zapato", "patos"))
print(distancias.levenshtein_reduccion("zapato", "patos"))
print(distancias.levenshtein("zapato", "patos", 4))
print(distancias.levenshtein_cota_optimista("zapato", "patos", 4))