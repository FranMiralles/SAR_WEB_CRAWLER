import re



def normalize_query(query:str) -> list[str]:
    """
    Normaliza la consulta

    Args:
        query (str): consulta

    Returns:
        List[str]: lista de tokens
    """
    current_word = ''  # Variable para almacenar la palabra actual
    result = []  # Lista para almacenar los resultados
    opened_quotes = False  # Bandera para indicar si estamos dentro de comillas

    for character in query:
        if character == '"' and not opened_quotes:
            # Si encontramos una comilla de apertura
            opened_quotes = True
        elif character == '"' and opened_quotes:
            # Si encontramos una comilla de cierre
            opened_quotes = False
            if current_word:  # Agregar la palabra actual si no está vacía
                result.append(current_word)
            current_word = ''
        elif character == ' ' and opened_quotes:
            # Agregar espacios dentro de comillas a la palabra actual
            current_word += character
        elif character == ' ' and not opened_quotes:
            # Agregar la palabra actual si no estamos dentro de comillas
            if current_word:  # Agregar la palabra actual si no está vacía
                result.append(current_word)
            current_word = ''
        elif character == '(' or character == ')':
            # Si encontramos un paréntesis, agregar la palabra actual y el paréntesis
            if current_word:  # Agregar la palabra actual si no está vacía
                result.append(current_word)
            result.append(character)
            current_word = ''
        else:
            # Agregar el carácter actual a la palabra actual
            current_word += character

    # Agregar la última palabra si no está vacía
    if current_word:
        result.append(current_word)

    return result

string = 'fo*o url:"baz baz" grault garply:"waldo" (fred plugh:xyzzy) "buenos dias'

print(normalize_query(string))