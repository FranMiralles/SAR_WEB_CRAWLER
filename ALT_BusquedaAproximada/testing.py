import distancias

print(distancias.levenshtein_edicion("ejemplo", "campos"))
print(distancias.levenshtein_edicion("amorcito", "aviador"))
print(distancias.levenshtein_reduccion("amorcito", "aviador"))
print(distancias.levenshtein_cota_optimista("casa", "abad", 5))