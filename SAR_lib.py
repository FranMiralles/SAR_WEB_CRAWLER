import json
from nltk.stem.snowball import SnowballStemmer
import os
import re
import sys
import math
from pathlib import Path
from typing import Optional, List, Union, Dict
import pickle
import re

from SAR_Crawler_lib import SAR_Wiki_Crawler

class SAR_Indexer:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de artículos de Wikipedia
        
        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [
        ("all", True), ("title", True), ("summary", True), ("section-name", True), ('url', False),
    ]
    def_field = 'all'
    PAR_MARK = '%'
    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10

    all_atribs = ['urls', 'index', 'sindex', 'ptindex', 'docs', 'weight', 'articles',
                  'tokenizer', 'stemmer', 'show_all', 'use_stemming']

    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas 

        """
        self.urls = set() # hash para las urls procesadas,
        self.index = {} # hash para el indice invertido de terminos --> clave: termino, valor: posting list
        self.sindex = {} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        self.ptindex = {} # hash para el indice permuterm.
        self.docs = {} # diccionario de terminos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados.
        self.articles = {} # hash de articulos --> clave entero (artid), valor: la info necesaria para diferencia los artículos dentro de su fichero
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################


    def set_showall(self, v:bool):
        """

        Cambia el modo de mostrar los resultados.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v:bool):
        """

        Cambia el modo de mostrar snippet.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v



    #############################################
    ###                                       ###
    ###      CARGA Y GUARDADO DEL INDICE      ###
    ###                                       ###
    #############################################


    def save_info(self, filename:str):
        """
        Guarda la información del índice en un fichero en formato binario
        
        """
        info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'wb') as fh:
            pickle.dump(info, fh)

    def load_info(self, filename:str):
        """
        Carga la información del índice desde un fichero en formato binario
        
        """
        #info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'rb') as fh:
            info = pickle.load(fh)
        atrs = info[0]
        for name, val in zip(atrs, info[1:]):
            setattr(self, name, val)

    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################

    def already_in_index(self, article:Dict) -> bool:
        """

        Args:
            article (Dict): diccionario con la información de un artículo

        Returns:
            bool: True si el artículo ya está indexado, False en caso contrario
        """
        return article['url'] in self.urls


    def index_dir(self, root:str, **args): # alguien
        """
        
        Recorre recursivamente el directorio o fichero "root" 
        NECESARIO PARA TODAS LAS VERSIONES
        
        Recorre recursivamente el directorio "root"  y indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """
        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        file_or_dir = Path(root)
        
        if file_or_dir.is_file():
            # is a file
            self.index_file(root)
        elif file_or_dir.is_dir():
            # is a directory
            for d, _, files in os.walk(root):
                for filename in sorted(files):
                    if filename.endswith('.json'):
                        fullname = os.path.join(d, filename)
                        self.index_file(fullname)
        else:
            print(f"ERROR:{root} is not a file nor directory!", file=sys.stderr)
            sys.exit(-1)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################

        #
        if self.stemming:
            self.make_stemming()
        if self.permuterm:
            self.make_permuterm()
        
        
    def parse_article(self, raw_line:str) -> Dict[str, str]:
        """
        Crea un diccionario a partir de una linea que representa un artículo del crawler

        Args:
            raw_line: una linea del fichero generado por el crawler

        Returns:
            Dict[str, str]: claves: 'url', 'title', 'summary', 'all', 'section-name'
        """
        
        article = json.loads(raw_line)
        sec_names = []
        txt_secs = ''
        for sec in article['sections']:
            txt_secs += sec['name'] + '\n' + sec['text'] + '\n'
            txt_secs += '\n'.join(subsec['name'] + '\n' + subsec['text'] + '\n' for subsec in sec['subsections']) + '\n\n'
            sec_names.append(sec['name'])
            sec_names.extend(subsec['name'] for subsec in sec['subsections'])
        article.pop('sections') # no la necesitamos 
        article['all'] = article['title'] + '\n\n' + article['summary'] + '\n\n' + txt_secs
        article['section-name'] = '\n'.join(sec_names)

        return article
                
    
    def index_file(self, filename: str): # CARLOS
        """
        Indexa el contenido de un fichero.
        
        input: "filename" es el nombre de un fichero generado por el Crawler cada línea es un objeto json
            con la información de un artículo de la Wikipedia

        NECESARIO PARA TODAS LAS VERSIONES

        dependiendo del valor de self.multifield y self.positional se debe ampliar el indexado,
        en el caso de positional se debe indexar la posición de las palabras, en el caso de multifield
        se deben indexar todos los campos.
        """

        # Asignar ID único para el documento
        docId = len(self.docs)
        self.docs[docId] = filename
        if 'all' not in self.index:
            self.index['all'] = {}

        print(f"Indexing {filename}")

        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                j = self.parse_article(line)  # Parsear el artículo

                if self.already_in_index(j):  # Verificar si el artículo ya está indexado
                    print(f"Article {j['url']} already indexed")
                    continue

                # Tokenizar el contenido del artículo
                content = j['all']
                #print(f"Indexing {j['title']} with {len(tokens)} tokens")

                # Asignar ID único para el artículo
                articleId = len(self.articles)
                self.articles[articleId] = {'doc_id': docId, 'url': j['url']}

                # Indexar los tokens
                if self.positional:
                        
                    if self.multifield:
                        for field, tokenize in self.fields:
                                    if field not in self.index:
                                        self.index[field] = {}
                                        
                                    content = j[field]
                                    if tokenize:
                                        tokens = self.tokenize(content)
                                        for i, token in enumerate(tokens):
                                            if token not in self.index[field]: #Nueva entrada en el índice
                                                self.index[field][token] = [(articleId, [i])]
                                           #Ya existe la entrada en el índice
                                            else: 
                                                # Mirar si seguimos con el mismo artId para añadir la posición o si es un nuevo artId para añadir una nueva tupla
                                                if self.index[field][token][-1][0] != articleId:
                                                    self.index[field][token].append((articleId, [i]))
                                                else:
                                                    self.index[field][token][-1][1].append(i)
                                    else:
                                        url = content #Es el caso de url, se indexa como una palabra
                                        if url not in self.index[field]:
                                            self.index[field][url] = [(articleId, [0])]
                                        else: self.index[field][url].append((articleId, 0))

                    else:   
                        tokens = self.tokenize(content)
                        for i, token in enumerate(tokens):
                            if token not in self.index['all']: #Nueva entrada en el índice
                                self.index['all'][token] = [(articleId, [i])]
                            #Ya existe la entrada en el índice
                            else: 
                                # Mirar si seguimos con el mismo artId para añadir la posición o si es un nuevo artId para añadir una nueva tupla
                                if self.index['all'][token][-1][0] != articleId:
                                    self.index['all'][token].append((articleId, [i]))
                                else:
                                    self.index['all'][token][-1][1].append(i)
                else:
                    if self.multifield:
                        for field, tokenize in self.fields:
                                    if field not in self.index:
                                        self.index[field] = {}
                                        
                                    content = j[field] 
                                    if tokenize:
                                        tokens = self.tokenize(content)
                                        for token in tokens:
                                            if token not in self.index[field]:
                                                self.index[field][token] = [articleId]
                                            # MIRAR SI YA ESTA EN LA LISTA, comprobar si la última tupla es la misma que la actual
                                            else:
                                                if not self.index[field][token] or self.index[field][token][-1] != articleId:
                                                    self.index[field][token].append(articleId)

                                    else :
                                        url = content
                                        if url not in self.index[field]:
                                            self.index[field][url] = [articleId]
                                        else: self.index[field][url].append(articleId)
                    else:
                        tokens = self.tokenize(content)
                        for token in tokens:
                            if token not in self.index['all']:
                                self.index['all'][token] = [articleId]
                            else:
                                if not self.index['all'][token] or self.index['all'][token][-1] != articleId:
                                    self.index['all'][token].append(articleId)

                self.urls.add(j['url'])  # Añadir la URL al conjunto de URLs

                print(f"Indexing article {articleId}:", len(tokens), j['title'])
                

    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def tokenize(self, text:str):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()


    def make_stemming(self): #CARLOS
        """

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE STEMMING.

        "self.stemmer.stem(token) devuelve el stem del token"


        """
        self.sindex = {}

        #For multifield
        if self.multifield:
            for field, tokenize in self.fields: #Iterar por 'all', 'title', 'summary', 'section-name', 'url'
                    if field not in self.sindex: #Crear la entrada en el diccionario si no existe
                        self.sindex[field] = {}
                    for term in self.index[field]: #Para cada termino en el indice actual
                        stem = self.stemmer.stem(term) #Sacamos el stem del termino
                        if stem not in self.sindex[field]: #Si el stem no esta en el indice de stems, lo añadimos
                            self.sindex[field][stem] = []
                        self.sindex[field][stem].append(term)
        else: 
            self.sindex['all'] = {}
            for term in self.index['all']: #Para cada termino en el indice actual
                stem = self.stemmer.stem(term)
                if stem not in self.sindex['all']: #Si el stem no esta en el indice de stems, lo añadimos
                    self.sindex['all'][stem] = []
                self.sindex['all'][stem].append(term)

    
    def make_permuterm(self): #CARLOS
        """
        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE PERMUTERM
        """

        self.ptindex = {}

        # For multifield
        if self.multifield:
            for field, tokenize in self.fields:
                    if field not in self.ptindex:
                        self.ptindex[field] = {}
                    for term in self.index[field]:
                        permuted_terms = self.generate_permuterms(term)
                        for perm in permuted_terms:
                            if perm not in self.ptindex[field]:
                                self.ptindex[field][perm] = term
        else:
            if 'all' not in self.ptindex:
                self.ptindex['all'] = {}
            for term in self.index['all']:
                permuted_terms = self.generate_permuterms(term)
                for perm in permuted_terms:
                    if perm not in self.ptindex['all']:
                        self.ptindex['all'][perm] = term

    def generate_permuterms(self, term): #Carlos, método auxiliar
        """
        Genera la lista de permuterms para un término dado.

        Args:
            term (str): El término para el que se generarán los permuterms.

        Returns:
            List[str]: Lista de permuterms generados para el término.
        """
        permuterms = []
        augmented_term = term + '$'
        for i in range(len(augmented_term)):
            permuterm = augmented_term[i:] + augmented_term[:i]
            permuterms.append(permuterm)
        return permuterms


    def show_stats(self): #CARLOS
        """
        Muestra estadisticas de los indices.
        """
        print("========================================")
        print(f"Number of indexed files: {len(self.docs)}")
        print("----------------------------------------")
        print(f"Number of indexed articles: {len(self.articles)}")
        print("----------------------------------------")
        print("TOKENS:")
        if self.multifield:
            for field in self.index:
                tokens = len(self.index[field])
                print(f"\t# of tokens in '{field}': {tokens}")
        else:
            tokens = len(self.index['all'])
            print(f"\t# of tokens in 'all': {tokens}")
        print("----------------------------------------")
        if self.permuterm:
            print("PERMUTERMS:")
            for field in self.ptindex:
                tokens = len(self.ptindex[field])
                print(f"\t# of permuterms in '{field}': {tokens}")
            print("----------------------------------------")
        
        if self.stemming:
            print("STEMS:")
            for field in self.sindex:
                tokens = len(self.sindex[field])
                print(f"\t# of stems in '{field}': {tokens}")
            print("----------------------------------------")

        if(self.positional):
            print("Positional queries are allowed")
        else:
            print("Positional queries are NOT allowed")

        print("========================================")

        print(self.index['all']['fin'])
        
        #for article in self.articles:
        #    print(self.articles[article])

        #Printear las posting lists
        #   print("fin")
        #   print(self.index['all']['fin'])
        #   print("semana")
        #   print(self.index['all']['semana'])
        #for term in self.index['all']:
        #print(list(self.ptindex.keys()))

        #print article 392
        


    #################################
    ###                           ###
    ###   PARTE 2: RECUPERACION   ###
    ###                           ###
    #################################

    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################



    def solve_query(self, query:str): #David
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
            "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """

        if query is None or len(query) == 0:
            return []
        
        tokens = []

        # Normalizar la consulta
        elements = self.normalize_query(query)

        # Obtener las posting lists de los términos
        for element in elements:
            if element not in ['AND', 'OR', 'NOT', '(', ')']:
                if ':' in element:
                    field, term = element.split(':')
                    tokens.append(self.get_posting(term.lower(), field.lower()))
                else:
                    tokens.append(self.get_posting(element.lower()))
                
            else:
                tokens.append(element)
        # Pilas para operadores y operandos
        operator_stack = []
        operand_stack = []

        i = 0
        # Iterar sobre los tokens
        for token in tokens:
            if token == '(':
                operator_stack.append(token)
            elif token == ')':
                # Procesar los tokens hasta encontrar el '('
                while operator_stack and operator_stack[-1] != '(':
                    operator = operator_stack.pop()
                    operand2 = operand_stack.pop()
                    operand1 = operand_stack.pop()
                    result = self.evaluate(operator, operand1, operand2)
                    operand_stack.append(result)
                # Eliminar el '(' de la pila de operadores al haber resuelto la subexpresión
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
            elif token in ['AND', 'OR']:
                # Procesar los tokens con mayor prioridad
                while operator_stack and operator_stack[-1] != '(':
                    operator = operator_stack.pop()
                    operand2 = operand_stack.pop()
                    operand1 = operand_stack.pop()
                    result = self.evaluate(operator, operand1, operand2)
                    operand_stack.append(result)
                # Añade el operador a la pila de operadores
                operator_stack.append(token)
            elif token == 'NOT':
                # NOT seguido de una subexpresión
                if tokens[i+1] == '(':  
                    operator_stack.append('NOT')
                else:
                    operand = tokens.pop(i+1)
                    result = self.reverse_posting(operand)
                    operand_stack.append(result)
            else:
                # Añade el término a la pila de operandos
                operand_stack.append(token)
            i += 1    

        # Procesar el resto de tokens
        while operator_stack:
            operator = operator_stack.pop()
            if operator == 'NOT':
                operand = operand_stack.pop()
                result = self.reverse_posting(operand)
                operand_stack.append(result)
            else:
                operand2 = operand_stack.pop()
                operand1 = operand_stack.pop()
                result = self.evaluate(operator, operand1, operand2)
                operand_stack.append(result)

        # Devolver el resultado
        return operand_stack[-1] if operand_stack else []
    

        

    def evaluate(self, operator:str, operand1:List, operand2:List) -> List: #David
            """
            Evalúa el operador dado en los dos operandos y devuelve el resultado.

            Parámetros:
            operator (str): El operador a aplicar. Los valores válidos son 'AND' y 'OR'.
            operand1 (List): El primer operando.
            operand2 (List): El segundo operando.

            Devuelve:
            List: El resultado de aplicar el operador en los operandos.

            Lanza:
            ValueError: Si el operador no es 'AND' ni 'OR'.
            """
            if operator == 'AND':
                return self.and_posting(operand1, operand2)
            elif operator == 'OR':
                return self.or_posting(operand1, operand2)
            else:
                raise ValueError(f"Operador inválido: {operator}")
            
        
    def normalize_query(self, query:str) -> List[str]: #David
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
        operators = {"OR", "AND", "NOT", "(", ")"}  # Conjunto de operadores lógicos y paréntesis

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
                    current_word = ''
                result.append(character)
            else:
                # Agregar el carácter actual a la palabra actual
                current_word += character
        
        # Agregar la última palabra
        if current_word:
            result.append(current_word)
        
        # Insertar 'AND' donde sea necesario
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
        
        return final_result



    def get_posting(self, term:str, field:Optional[str]=None): # FRAN
        """

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list
        
        NECESARIO PARA TODAS LAS VERSIONES

        """
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        res = []
        

        # En caso de que el campo sea None, buscar en all
        if field == None:
            field = "all"

        # Caso de usar permuterm
        if ("*" in term or "?" in term):
            res = self.get_permuterm(term,field)

        # Caso de usar positionals
        elif (" " in term or ":" in term):
            res = self.get_positionals(term, field)

        # Caso de usar permuterm
        elif("*" in term or "?" in term):
            res = self.get_permuterm(term,field)

        # Caso de usar stemming
        elif (self.use_stemming):
            res = self.get_stemming(term, field)

        # Caso base
        elif term in self.index[field]:
            res = self.index[field][term]

        # Quitar las posiciones para los ands or y minus...
        resAux = res
        res = []
        for element in resAux:
            if isinstance(element, tuple):
                res.append(element[0])
            else:
                res.append(element)
        return res



    def get_positionals(self, terms:str, field:Optional[str]=None): # FRAN
        """

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        res = []
        separedTerms = terms.split(" ")

        # Obtener para cada termino sus articlesID en una lista, luego hacer AND para obtener solo los articlesID que aparecen en todos los terminos, esto lo hago para agilizar la computación posterior de comprobar para cada posición si los siguientes términos tienen una posición seguida
        sharedArticlesIDList = []
        for term in separedTerms:
            aux = []
            postingPositional = self.get_posting(term, field)
            for tupla in postingPositional:
                # Añado solo los articleID
                aux.append(tupla[0])
            aux.sort()
            sharedArticlesIDList.append(aux)
        # Hacer el AND entre todos los articleID de cada término
        sharedArticlesID = sharedArticlesIDList.pop()
        while(len(sharedArticlesIDList) != 0):
            sharedArticlesID = self.and_posting(sharedArticlesID, sharedArticlesIDList.pop())

        # Ahora en sharedArticlesID tengo una lista con todos los ID que se repiten en todos los términos, para buscar a partir de estos

        # Obtengo el primer término y su posting por el que se hará el recorrido del algoritmo
        firstTerm = separedTerms.pop(0)
        firstPosting = self.get_posting(firstTerm, field)
        for firstTupla in firstPosting:
            # Si el articleID se encuentra en la lista de articlesID comunes
            if(firstTupla[0] in sharedArticlesID):
                # Recorrido por cada posición
                for i in range(len(firstTupla[1])):
                    pos = firstTupla[1][i]
                    # Esta variable permitirá controlar si se ha llegado al final con todos los términos, encontrando posiciones secuenciales
                    inAllTerms = True
                    # Buscar el siguiente en cada midTerm
                    for midTerm in separedTerms:
                        # Para cada término, aumentamos la posición
                        pos += 1
                        # Si algún término no tiene la posición terminamos el bucle
                        if not(inAllTerms):
                            break
                        # Obtenemos la posting de los términos posteriores al primero y recorremos sus tuplas para encontrar aquella con articleID igual al que buscamos
                        midPosting = self.get_posting(midTerm, field)
                        for midTupla in midPosting:
                            if firstTupla[0] == midTupla[0]:
                                # Buscamos una ocurrencia de la posición, si no se encuentra salta una excepción y ponemos la variable inAllTerms a False, indicando que no se ha encontrado en todos los términos
                                try:
                                    midTupla[1].index(pos)
                                except ValueError:
                                    inAllTerms = False
                    # Si se ha encontrado para todos los términos, se añade al resultado el articleID y la posición del primer término del sintagma en el artículo
                    if inAllTerms:
                        res.append((firstTupla[0], firstTupla[1][i]))
        

        return res
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################


    def get_stemming(self, term:str, field: Optional[str]=None): # FRAN
        """

        Devuelve la posting list asociada al stem de un termino.
        NECESARIO PARA LA AMPLIACION DE STEMMING

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        # COMPLETADO
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

        # Devuelve el steam del término
        stem = self.stemmer.stem(term)
        res = []
        # Si se encuentra en el índice, devolver la posting list asociada
        if (stem in self.sindex[field]):
            res = self.sindex[field][stem]

        return res

    def get_permuterm(self, term: str, field: Optional[str] = None):  # ROBERTO
        """
        Devuelve la lista de postings asociada a un término utilizando el índice permuterm.
        NECESARIO PARA LA AMPLIACIÓN DE PERMUTERM

        param:  "term": término para recuperar la lista de postings, "term" incluye un comodín (* o ?).
                "field": campo sobre el que se debe recuperar la lista de postings, solo necesario si se hace la ampliación de múltiples índices.

        return: lista de postings
        """
        
        #####################
        #### COMPLETADO #####
        #####################

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################

        # Reemplaza los comodines con la representación interna
        # term = term.replace('*', '%').replace('?', '_')

        # Genera el permuterm con todas las rotaciones
        # permuterm = term + '$'
        #rotations = [permuterm[i:] + permuterm[:i] for i in range(len(permuterm))]
        print("GETPERMUTERM")
        res = []
        pterm = term + "$"
        while pterm[len(pterm)-1] != '*' and pterm[len(pterm)-1] != '?':
            pterm = pterm[1:] + pterm[0]

        keys = list(self.ptindex[field].keys())

        keysRelated = []
        if pterm[-1] == '*':
            pterm = pterm[:-1]
            for key in keys:
                if key.startswith(pterm):
                    keysRelated.append(key)
            pass
        elif pterm[-1] == '?':
            pterm = pterm[:-1]
            for key in keys:
                if key.startswith(pterm) and len(key) == len(key) + 1:
                    keysRelated.append(key)
            pass

        if len(keysRelated) == 0:
            return res
        
        postingsRelated = []
        while(len(keysRelated) != 0):
            key = self.ptindex[field][keysRelated.pop()]
            postingsRelated.append(self.get_posting(key, field))

        if len(postingsRelated) == 0:
            return res
        
        print("PostingsRelated")
        print(postingsRelated)

        res = postingsRelated.pop(0)
        while(len(postingsRelated) != 0):
            res = self.or_posting(res, postingsRelated.pop()) 


        # self.ptindex
        return res



    def reverse_posting(self, p:list): # FRAN
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los artid exceptos los contenidos en p

        """
        # COMPLETADO
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        res = list(self.articles.keys()).sort()
        return self.minus_posting(res, p)



    def and_posting(self, p1:list, p2:list):# FRAN
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los artid incluidos en p1 y p2

        """
        # COMPLETADO
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        p3:list = []
        p1 = list(set(p1))
        p2 = list(set(p2))
        p1.sort()
        p2.sort()
        while len(p1) != 0 and len(p2) != 0:
            if(p1[0] == p2[0]):
                p3.append(p1[0])
                p1.pop(0)
                p2.pop(0)
            else:
                if(p1[0] < p2[0]):
                    p1.pop(0)
                else:
                    p2.pop(0)

        return p3



    def or_posting(self, p1:list, p2:list): # FRAN
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los artid incluidos de p1 o p2

        """
        # COMPLETADO
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        p3:list = []
        p1 = list(set(p1))
        p2 = list(set(p2))
        p1.sort()
        p2.sort()
        while len(p1) != 0 and len(p2) != 0:
            if(p1[0] == p2[0]):
                p3.append(p1[0])
                p1.pop(0)
                p2.pop(0)
            else:
                if(p1[0] < p2[0]):
                    p3.append(p1[0])
                    p1.pop(0)
                else:
                    p3.append(p2[0])
                    p2.pop(0)
        while len(p1) != 0:
            p3.append(p1[0])
            p1.pop(0)
        while len(p2) != 0:
            p3.append(p2[0])
            p2.pop(0)

        return p3


    def minus_posting(self, p1:list, p2:list): # FRAN
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se incluye por si es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los artid incluidos de p1 y no en p2

        """
        # COMPLETADO
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################
        print("p2")
        print(p2)
        p3:list = []
        p2 = list(set(p2))
        p2.sort()   
        while len(p1) != 0 and len(p2) != 0:
            if(p1[0] < p2[0]):
                p3.append(p1[0])
                p1.pop(0)
            else:
                if(p1[0] > p2[0]):
                    p2.pop(0)
                else:
                    p1.pop(0)
                    p2.pop(0)
        while len(p1) != 0:
            p3.append(p1[0])
            p1.pop(0)

        return p3





    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################

    def solve_and_count(self, ql:List[str], verbose:bool=True) -> List:
        results = []
        for query in ql:
            if len(query) > 0 and query[0] != '#':
                r = self.solve_query(query)
                results.append(len(r))
                if verbose:
                    print(f'{query}\t{len(r)}')
            else:
                results.append(0)
                if verbose:
                    print(query)
        return results


    def solve_and_test(self, ql:List[str]) -> bool:
        errors = False
        for line in ql:
            if len(line) > 0 and line[0] != '#':
                query, ref = line.split('\t')
                reference = int(ref)
                result = len(self.solve_query(query))
                if reference == result:
                    print(f'{query}\t{result}')
                else:
                    print(f'>>>>{query}\t{reference} != {result}<<<<')
                    errors = True                    
            else:
                print(query)
        return not errors


    def solve_and_show(self, query:str): # ROBERTO
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados 

        param:  "query": query que se debe resolver.

        return: el numero de artículo recuperadas, para la opcion -T

        """
        solved = self.solve_query(query)
        print(solved)

        indexed_urls = []
        titles = []

        for art_id in solved:
            docID = self.articles[art_id]['doc_id']
            url = (self.articles[art_id]['url'])
            indexed_urls.append(url)
            filename = self.docs[docID]
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    j = self.parse_article(line) 
                    if j['url'] == url:

                        titles.append(j['title'])

        result = list(zip(indexed_urls, titles))

        print('========================================')
        i = 1
        for url, title in result:
            print(f"#{i:02d} ({'algo'}) {title}: {url}")
            if False:
                break
            i += 1
        print('========================================')
        print(f"Number of results: {len(result)}")






        

