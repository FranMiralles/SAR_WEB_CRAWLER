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
                for filename in files:
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
        #if self.stemming:
        #    make_stemming(self)
        #if self.permuterm:
        #    make_permuterm(self)
        
        
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
                
    
    def index_file(self, filename: str):
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

        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                j = self.parse_article(line)  # Parsear el artículo
                if self.already_in_index(j):  # Verificar si el artículo ya está indexado
                    continue

                # Tokenizar el contenido del artículo
                content = j['all']
                tokens = self.tokenize(content)

                #print(f"Indexing {j['title']} with {len(tokens)} tokens")

                # Asignar ID único para el artículo
                articleId = len(self.articles)
                self.articles[articleId] = {'doc_id': docId, 'position': len(self.articles)}

                # Indexar los tokens
                if self.positional:
                        
                    if self.multifield:
                        for field, tokenize in self.fields:
                                if field not in self.index:
                                    self.index[field] = {}
                                    
                                content = j[field]
                                tokens = self.tokenize(content)

                                for i, token in tokens:
                                    if token not in self.index[field]:
                                        self.index[field][token] = set()
                                    self.index[field][token].add((articleId, i))
                     
                    else:   
                        for i, token in enumerate(tokens):
                            if token not in self.index['all']:
                                self.index['all'][token] = set()
                            self.index['all'][token].add((articleId, i))
                else:
                    if self.multifield:
                        for field, tokenize in self.fields:
                                if field not in self.index:
                                    self.index[field] = {}
                                    
                                content = j[field] 
                                tokens = self.tokenize(content)

                                for token in tokens:
                                    if token not in self.index[field]:
                                        self.index[field][token] = set()
                                    self.index[field][token].add(articleId)

                    else:
                        for token in tokens:
                            if token not in self.index['all']:
                                self.index['all'][token] = set()
                            self.index['all'][token].add(articleId)

                self.urls.add(j['url'])  # Añadir la URL al conjunto de URLs

        print(f"Indexed {filename} with {len(self.articles)} articles and {sum(len(postings) for postings in self.index['all'].values())} total tokens.")

            # 
            # En la version basica solo se debe indexar el contenido "all"
            #
        #
        #
        #################
        ### COMPLETAR ###
        #################



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
        for term in self.index:
            stemmed_term = self.stemmer.stem(term)
            if stemmed_term not in self.sindex:
                self.sindex[stemmed_term] = set()
            self.sindex[stemmed_term].update(self.index[term])


    
    def make_permuterm(self): #CARLOS
        """
        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE PERMUTERM
        """

        self.ptindex = {}
        for term in self.index:
            # Generate all possible rotations of the term
            rotations = [term[i:] + term[:i] for i in range(len(term))]
            # Add the rotations to the permuterm index
            for rotation in rotations:
                if rotation not in self.ptindex:
                    self.ptindex[rotation] = set()
                self.ptindex[rotation].add(term)




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
            for field, tokenize in self.fields:
                    tokens = len(self.index[field])
                    print(f"\t# of tokens in '{field}': {tokens}")
        else:
            tokens = len(self.index['all'])
            print(f"\t# of tokens in 'all': {tokens}")
        print("----------------------------------------")
        print("Positional queries are NOT allowed.")
        print("========================================")

        
        #Let's print the inverted index
        #print("Inverted index:")
        #for term, posting in self.index['all'].items():
            #print(f"{term}: {posting}")



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
        elements = self.normalize_query(query)
        for element in elements:
            if element not in ['AND', 'OR', 'NOT', '(', ')']:
                tokens.append(self.get_posting(element))
            else:
                tokens.append(element)

        # Pilas para operadores y operandos
        operator_stack = []
        operand_stack = []

        # Iterar sobre los tokens
        for i, token in tokens:
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
                operand_stack.append(self.get_posting(token))

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
        

    def evaluate(self, operator:str, operand1:List, operand2:List) -> List:
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
                return self.and_posting(self.index.get(operand1, []), self.index.get(operand2, []))
            elif operator == 'OR':
                return self.or_posting(self.index.get(operand1, []), self.index.get(operand2, []))
            else:
                raise ValueError(f"Operador inválido: {operator}")
        
    def normalize_query(self, query:str) -> List[str]:
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
        pass



    def get_positionals(self, terms:str, index): # FRAN
        """

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        pass
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
        
        stem = self.stemmer.stem(term)

        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

    def get_permuterm(self, term:str, field:Optional[str]=None): # ROBERTO
        """

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################
        pass



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
        res = list(self.docs.keys())
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
        p1.sort()
        p1 = list(set(p1))
        p2.sort()
        p2 = list(set(p2))
        p3:list = []
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
        p1.sort()
        p1 = list(set(p1))
        p2.sort()
        p2 = list(set(p2))
        p3:list = []
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


    def minus_posting(self, p1, p2): # FRAN
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
        p1.sort()
        p1 = list(set(p1))
        p2.sort()
        p2 = list(set(p2))
        p3:list = []
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
        
        ################
        ## COMPLETAR  ##
        ################
        







        

