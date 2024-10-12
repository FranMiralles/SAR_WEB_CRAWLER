import numpy as np

def levenshtein_matriz(x, y, threshold=None):
    # esta versión no utiliza threshold, se pone porque se puede
    # invocar con él, en cuyo caso se ignora
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    return D[lenX, lenY]

def levenshtein_edicion(x, y, threshold=None):
    # Obtener la matriz de levenshtein:
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    
    # Hacer el back-tracking
    i = lenX
    j = lenY
    path = []
    while i > 0 and j > 0:
        # DIAGONAL
        if(D[i][j] == D[i-1][j-1] or D[i][j] == D[i-1][j-1] + 1):
            i -= 1
            j -= 1
            path.append((x[i], y[j]))
        # INSERCIÓN
        elif(D[i][j] == D[i][j-1] + 1):
            j -= 1
            path.append(('', y[j]))
        # BORRADO
        elif(D[i][j] == D[i-1][j] + 1):
            i -= 1
            path.append((x[i], ''))
    # Si queda algo en x, son borrados
    while i > 0:
        i -= 1
        path.append((x[i], ''))
    # Si queda algo en y, son inserciones
    while j > 0:
        j -= 1
        path.append(('', y[j]))

    path.reverse()
    return D[lenX, lenY],path

def levenshtein_reduccion(x, y, threshold=None):
    lenX = len(x)
    lenY = len(y)
    filaActual = list(range(lenY + 1))

    # Bucle sobre la palabra x (a transformar)
    for i in range(1, lenX + 1):
        filaAnterior = filaActual[:]
        filaActual[0] = i
        # Bucle sobre la palabra y (objetivo)
        for j in range(1, lenY + 1):
            filaActual[j] = min(
                filaAnterior[j] + 1,
                filaActual[j - 1] + 1,
                filaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
            )
    
    return filaActual[-1]

# La estrategia del threshold que utilizamos es que si todos los valores de la fila actual calculada son mayores al threshold, paramos la ejecución ya que o se queda igual o empeora
def levenshtein(x, y, threshold):
    lenX = len(x)
    lenY = len(y)
    filaActual = list(range(lenY + 1))
    
    # Bucle sobre la palabra x (a transformar)
    for i in range(1, lenX + 1):
        filaAnterior = filaActual[:]
        filaActual[0] = i
        minimoEnFila = filaActual[0]
        # Bucle sobre la palabra y (objetivo)
        for j in range(1, lenY + 1):
            filaActual[j] = min(
                filaAnterior[j] + 1,
                filaActual[j - 1] + 1,
                filaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
            )
            minimoEnFila = min(minimoEnFila, filaActual[j])
            if(minimoEnFila > threshold):
                return threshold+1

    return filaActual[-1]

def levenshtein_cota_optimista(x, y, threshold):
    # Crear el diccionario
    cota = {}
    for caracter in x:
        if cota.get(caracter, None) == None:
            cota[caracter] = 1
        else:
            cota[caracter] += 1
    for caracter in y:
        if cota.get(caracter, None) == None:
            cota[caracter] = -1
        else:
            cota[caracter] -= 1
    valores = cota.values()
    positivos = 0
    negativos = 0
    for valor in valores:
        if valor > 0:
            positivos += valor
        else:
            negativos += valor
    if(max(positivos, negativos * -1) > threshold):
        return threshold + 1
    return levenshtein(x, y, threshold)

def damerau_restricted_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein restringida con matriz
    lenX, lenY = len(x), len(y)
    # COMPLETAR
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                D[i - 2][j - 2] + 1,
            )
    return D[lenX, lenY]


    return 0 # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_edicion(x, y, threshold=None):
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE
    
def damerau_intermediate(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

opcionesSpell = {
    'levenshtein_m': levenshtein_matriz,
    'levenshtein_r': levenshtein_reduccion,
    'levenshtein':   levenshtein,
    'levenshtein_o': levenshtein_cota_optimista,
    'damerau_rm':    damerau_restricted_matriz,
    'damerau_r':     damerau_restricted,
    'damerau_im':    damerau_intermediate_matriz,
    'damerau_i':     damerau_intermediate
}

opcionesEdicion = {
    'levenshtein': levenshtein_edicion,
    'damerau_r':   damerau_restricted_edicion,
    'damerau_i':   damerau_intermediate_edicion
}

