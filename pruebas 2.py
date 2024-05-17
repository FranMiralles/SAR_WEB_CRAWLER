def normalize_query(query: str) -> list[str]:
    """
    Normalizes the query

    Args:
        query (str): query

    Returns:
        List[str]: list of tokens
    """
    current_word = ''  # Variable to store the current word
    result = []  # List to store the results
    opened_quotes = False  # Flag to indicate if we are inside quotes
    operators = {"OR", "AND", "NOT", "(", ")"}
    
    for character in query:
        if character == '"' and not opened_quotes:
            # If we find an opening quote
            opened_quotes = True
        elif character == '"' and opened_quotes:
            # If we find a closing quote
            opened_quotes = False
            if current_word:  # Add the current word if it's not empty
                result.append(current_word)
            current_word = ''
        elif character == ' ' and opened_quotes:
            # Add spaces inside quotes to the current word
            current_word += character
        elif character == ' ' and not opened_quotes:
            # Add the current word if we are not inside quotes
            if current_word:  # Add the current word if it's not empty
                result.append(current_word)
                current_word = ''
        elif character == '(' or character == ')':
            # If we find a parenthesis, add the current word and the parenthesis
            if current_word:  # Add the current word if it's not empty
                result.append(current_word)
                current_word = ''
            result.append(character)
        else:
            # Add the current character to the current word
            current_word += character
    
    # Add the last word
    if current_word:
        result.append(current_word)
    
    # Insert 'AND' where necessary
    final_result = []
    for i in range(len(result)):
        final_result.append(result[i])
        if (
            i < len(result) - 1 and
            result[i] not in operators and 
            result[i + 1] not in operators and 
            result[i + 1] != '('
        ):
            final_result.append('AND')
        if (
            i < len(result) - 1 and 
            result[i] == ')' and 
            result[i + 1] not in operators and 
            result[i + 1] != ')'
        ):
            final_result.append('AND')
        if (
            i < len(result) - 1 and 
            result[i] not in operators and 
            result[i + 1] == '('
        ):
            final_result.append('AND')
    res = []   
    for element in final_result:
            if element not in ['AND', 'OR', 'NOT', '(', ')']:
                if ':' in element:
                    field, term = element.split(':')
                    res.append(term)
                    res.append(field)
    
    return res

# Example usage
query = 'hello world:bueno url:"find de semana" (this is AND NOT a test OR example) apc'
normalized_query = normalize_query(query)
print(normalized_query)
# Output should be: ['hello', 'AND', 'world', 'AND', '(', 'this', 'AND', 'is', 'AND', 'NOT', 'a', 'AND', 'test', 'OR', 'example', ')', 'AND', 'apc']
