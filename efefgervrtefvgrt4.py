import re

# Texto de ejemplo
text = "Mi número de teléfono es 123-456-7890."

# Patrón de expresión regular con grupos de captura
pattern = re.compile(r"(\d{3})-(\d{3})-(\d{4})")

# Buscar coincidencia
match = pattern.search(text)

if match:
    # group() devuelve la cadena completa que coincide con el patrón
    print("Coincidencia completa:", match.group())  # Output: "123-456-7890"
    
    # group(1) devuelve el primer grupo de captura
    print("Primer grupo:", match.group(1))  # Output: "123"
    
    # group(2) devuelve el segundo grupo de captura
    print("Segundo grupo:", match.group(2))  # Output: "456"
    
    # group(3) devuelve el tercer grupo de captura
    print("Tercer grupo:", match.group(3))  # Output: "7890"
    
    # group(1, 2, 3) devuelve una tupla con los tres grupos de captura
    print("Todos los grupos:", match.group(1, 2, 3))  # Output: ("123", "456", "7890")
