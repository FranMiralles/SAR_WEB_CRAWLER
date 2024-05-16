import re



def normalize_query(query:str) -> list[str]:
        """
        Normaliza la consulta

        Args:
            query (str): consulta

        Returns:
            List[str]: lista de tokens
        """
        element = ''
        result = []
        missing = False

        for character in query:
            if character == '"' and not missing:
                missing = True
            elif character == '"' and missing:
                missing = False
                if element:  
                    result.append(element)
                element = ''
            elif character == ' ' and missing:
                element += character
            elif character == ' ' and not missing:
                if element:  
                    result.append(element)
                element = ''
            elif character == '(' or character == ')':
                if element: 
                    result.append(element)
                result.append(character)
                element = ''
            else:
                element += character

        if element:
            result.append(element)

        return result
string = 'fo*o bar:"baz baz" grault garply:"waldo" (fred plugh:xyzzy) "buenos dias'

print(normalize_query(string))