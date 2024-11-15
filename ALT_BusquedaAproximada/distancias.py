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
        if((D[i][j] == D[i-1][j-1] and x[i-1] == y[j-1]) or D[i][j] == D[i-1][j-1] + 1):
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
    columnaActual = list(range(lenY + 1))

    # Bucle sobre la palabra x (a transformar)
    for i in range(1, lenX + 1):
        columnaAnterior = columnaActual[:]
        columnaActual[0] = i
        # Bucle sobre la palabra y (objetivo)
        for j in range(1, lenY + 1):
            columnaActual[j] = min(
                columnaAnterior[j] + 1,
                columnaActual[j - 1] + 1,
                columnaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
            )
    
    return columnaActual[-1]

# La estrategia del threshold que utilizamos es que si todos los valores de la fila actual
# calculada son mayores al threshold, paramos la ejecución ya que o se queda igual o empeora
def levenshtein(x, y, threshold=None):
    lenX = len(x)
    lenY = len(y)
    columnaActual = list(range(lenY + 1))
    
    # Bucle sobre la palabra x (a transformar)
    for i in range(1, lenX + 1):
        columnaAnterior = columnaActual[:]
        columnaActual[0] = i
        minimoEnFila = columnaActual[0]
        # Bucle sobre la palabra y (objetivo)
        for j in range(1, lenY + 1):
            columnaActual[j] = min(
                columnaAnterior[j] + 1,
                columnaActual[j - 1] + 1,
                columnaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
            )
            minimoEnFila = min(minimoEnFila, columnaActual[j])
        if(minimoEnFila > threshold):
            return threshold+1
        

    return columnaActual[-1]

def levenshtein_cota_optimista(x, y, threshold=None):
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
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(
                    D[i - 1][j] + 1,
                    D[i][j - 1] + 1,
                    D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                    D[i - 2][j - 2] + 1,
            )
            else:
                D[i][j] = min(
                    D[i - 1][j] + 1,
                    D[i][j - 1] + 1,
                    D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                )
    return D[lenX, lenY]


def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(
                    D[i - 1][j] + 1,
                    D[i][j - 1] + 1,
                    D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                    D[i - 2][j - 2] + 1,
            )
            else:
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
        #TRASPONER
        if(x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2] and D[i][j]==D[i - 2][j - 2] + 1):
            i -= 2
            j -= 2
            path.append((x[i]+x[i+1], y[j]+y[j+1]))
        # DIAGONAL
        if((D[i][j] == D[i-1][j-1] and x[i-1] == y[j-1]) or D[i][j] == D[i-1][j-1] + 1):
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

def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    lenX = len(x)
    lenY = len(y)
    columnaActual = list(range(lenY + 1))
    columnaAnterior = columnaActual[:]
    columnaActual[0] = 1
    minimoEnFila = columnaActual[0]
    for h in range(1, lenY+1):
        columnaActual[h] = min(
                columnaAnterior[h] + 1,
                columnaActual[h - 1] + 1,
                columnaAnterior[h - 1] + (x[0] != y[h - 1]),
            )
        minimoEnFila = min(minimoEnFila, columnaActual[h])
    if(minimoEnFila > threshold):
            return threshold+1
    # Bucle sobre la palabra x (a transformar)
    for i in range(2, lenX + 1):
        columnaDosAnterior = columnaAnterior[:]
        columnaAnterior = columnaActual[:]
        columnaActual[0] = i
        minimoEnFila = columnaActual[0]
        # Bucle sobre la palabra y (objetivo)
        for j in range(1, lenY + 1):
            if x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                columnaActual[j] = min(
                    columnaAnterior[j] + 1,
                    columnaActual[j - 1] + 1,
                    columnaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
                    columnaDosAnterior[j - 2] + 1,
                )
            else:
                columnaActual[j] = min(
                    columnaAnterior[j] + 1,
                    columnaActual[j - 1] + 1,
                    columnaAnterior[j - 1] + (x[i - 1] != y[j - 1]),
                )
            minimoEnFila = min(minimoEnFila, columnaActual[j])
        if(minimoEnFila > threshold):
            return threshold+1
        

    return columnaActual[-1]

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    # Añadir la primera columna
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    # Añadir la primera fila
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        # Añadir el resto de la matriz
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,  # Borrado
                D[i][j - 1] + 1,  # Inserción
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),  # Sustitución o match
            )
            
             # Transposición de caracteres adyacentes: ab ↔ ba
            if i > 1 and j > 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
            
            # Transposición de tres caracteres: acb ↔ ba
            if i > 2 and j > 1 and x[i - 3] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(D[i][j], D[i - 3][j - 2] + 2)
            
            # Transposición con carácter adicional: ab ↔ bca
            if i > 1 and j > 2 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 3]:
                D[i][j] = min(D[i][j], D[i - 2][j - 3] + 2)
                
    return D[lenX, lenY]

def damerau_intermediate_edicion(x, y, threshold=None):
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    
    # Inicializar la primera columna y fila
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
    
    # Rellenar la matriz
    for i in range(1, lenX + 1):
        for j in range(1, lenY + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,  # Borrado
                D[i][j - 1] + 1,  # Inserción
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),  # Sustitución o match
            )
            
            # Transposición de caracteres adyacentes: ab ↔ ba
            if i > 1 and j > 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
            
            # Transposición de tres caracteres: acb ↔ ba
            if i > 2 and j > 1 and x[i - 3] == y[j - 1] and x[i - 1] == y[j - 2]:
                D[i][j] = min(D[i][j], D[i - 3][j - 2] + 2)
            
            # Transposición con carácter adicional: ab ↔ bca
            if i > 1 and j > 2 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 3]:
                D[i][j] = min(D[i][j], D[i - 2][j - 3] + 2)
    
    # Hacer el camino
    i, j = lenX, lenY
    path = []
    while i > 0 and j > 0:
        # Diagonal (sustitución o match)
        if (D[i][j] == D[i - 1][j - 1] and x[i - 1] == y[j - 1]) or (D[i][j] == D[i - 1][j - 1] + 1 and x[i - 1] != y[j - 1]):
            path.append((x[i - 1], y[j - 1]))
            i -= 1
            j -= 1
        # Inserción
        elif D[i][j] == D[i][j - 1] + 1:
            path.append(('', y[j - 1]))
            j -= 1
        # Borrado
        elif D[i][j] == D[i - 1][j] + 1:
            path.append((x[i - 1], ''))
            i -= 1
        # Transposición de caracteres adyacentes: ab ↔ ba
        elif i > 1 and j > 1 and D[i][j] == D[i - 2][j - 2] + 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
            path.append((x[i - 2] + x[i - 1], y[j - 2] + y[j - 1]))
            i -= 2
            j -= 2
        # Transposición de tres caracteres: acb ↔ ba
        elif i > 2 and j > 1 and D[i][j] == D[i - 3][j - 2] + 2 and x[i - 3] == y[j - 1] and x[i - 1] == y[j - 2]:
            path.append((x[i - 3] + x[i - 2] + x[i - 1], y[j - 2] + y[j - 1]))
            i -= 3
            j -= 2
        # Transposición con carácter adicional: ab ↔ bca
        elif i > 1 and j > 2 and D[i][j] == D[i - 2][j - 3] + 2 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 3]:
            path.append((x[i - 2] + x[i - 1], y[j - 3] + y[j - 2] + y[j - 1]))
            i -= 2
            j -= 3
    
    # Si quedan caracteres en x, son borrados
    while i > 0:
        i -= 1
        path.append((x[i], ''))
    # Si quedan caracteres en y, son insertados
    while j > 0:
        j -= 1
        path.append(('', y[j]))
    
    path.reverse()
    return D[lenX, lenY], path

def damerau_intermediate(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    # Obtenemos las longitudes de las cadenas de entrada
    lenX, lenY = len(x), len(y)
    difX = lenX - lenY
    
    # Inicializamos los vectores de trabajo:
    # vCurrent: vector actual donde calcularemos las distancias mínimas
    # vPrev: vector previo para almacenar el estado anterior en el cálculo
    # vPenult y vAntepenult: para guardar valores de estados anteriores necesarios para transposiciones
    vCurrent = np.zeros(lenX, dtype=int)
    vPrev = np.arange(1, lenX + 1, dtype=int)  # Inicialización incremental
    vPenult = np.full(lenX, np.inf, dtype=int) # Simula infinito en enteros para indicar valores no alcanzables
    vAntepenult = np.full(lenX, np.inf, dtype=int)

    # Iteramos sobre cada carácter de la cadena `y`
    for j in range(lenY):
        # Si la diferencia de longitud excede el umbral, detenemos la ejecución
        if difX + j > 0 and vPrev[difX + j - 1] > threshold:
            return threshold + 1
        
        # Calcular la distancia en el primer elemento
        # Mínimo entre el valor acumulado de inserción, borrado, y sustitución
        vCurrent[0] = min(
            j + (x[0] != y[j]),
            vPrev[0] + 1
        )
        
        # Para cada carácter de `y`, iteramos sobre cada carácter de `x`
        for i in range(1, lenX):
            # Para posiciones posteriores, consideramos también las operaciones básicas
            vCurrent[i] = min(
                vCurrent[i - 1] + 1,            # Inserción
                vPrev[i] + 1,                   # Borrado
                vPrev[i - 1] + (x[i] != y[j])   # Sustitución o coincidencia
            )

            # Evaluamos la transposición de caracteres adyacentes simples: `ab` ↔ `ba`
            if j > 0 and x[i - 1] == y[j] and x[i] == y[j - 1]:
                # Transposición en la posición inicial
                if i == 1:
                    vCurrent[i] = min(vCurrent[i], j)
                else:
                    vCurrent[i] = min(vCurrent[i], vPenult[i - 2] + 1)

            # Transposición de tres caracteres: `acb` ↔ `ba`
            if i > 1 and j > 0 and x[i - 2] == y[j] and x[i] == y[j - 1]:
                if i == 2:
                    vCurrent[i] = min(vCurrent[i], j + 1)
                else:
                    vCurrent[i] = min(vCurrent[i], vPenult[i - 3] + 2)

            # Transposición con un carácter adicional: `ab` ↔ `bca`
            if j > 1 and x[i - 1] == y[j] and x[i] == y[j - 2]:
                if i == 1:
                    vCurrent[i] = min(vCurrent[i], j)
                else:
                    vCurrent[i] = min(vCurrent[i], vAntepenult[i - 2] + 2)

        # Actualizamos los vectores para la siguiente iteración
        vAntepenult, vPenult = vPenult, vAntepenult
        vPenult, vPrev = vPrev, vPenult
        vPrev, vCurrent = vCurrent, vPrev

    # Devolvemos la distancia mínima encontrada en el último elemento de `vPrev`
    return vPrev[-1]

    
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

