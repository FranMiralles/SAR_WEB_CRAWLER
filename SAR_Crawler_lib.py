#! -*- encoding: utf8 -*-
import heapq as hq

from typing import Tuple, List, Optional, Dict, Union

import requests
import bs4
import re
from urllib.parse import urljoin
import json
import math
import os

class SAR_Wiki_Crawler:

    def __init__(self):
        # Expresión regular para detectar si es un enlace de la Wikipedia
        self.wiki_re = re.compile(r"(http(s)?:\/\/(es)\.wikipedia\.org)?\/wiki\/[\w\/_\(\)\%]+")
        # Expresión regular para limpiar anclas de editar
        self.edit_re = re.compile(r"\[(editar)\]")
        # Formato para cada nivel de sección
        self.section_format = {
            "h1": "##{}##",
            "h2": "=={}==",
            "h3": "--{}--"
        }

        # Expresiones regulares útiles para el parseo del documento
        # Expresión regular para detectar si es un enlace de la Wikipedia
        self.title_sum_re = re.compile(r"##(?P<title>.+)##\n(?P<summary>((?!==.+==).+|\n)+)(?P<rest>(.+|\n)*)")
        # Expresión regular para detectar secciones
        self.sections_re = re.compile(r"==.+==\n")
        # Expresión regular para extraer una sección y su contenido
        self.section_re = re.compile(r"==(?P<name>.+)==\n(?P<text>((?!--.+--).+|\n)*)(?P<rest>(.+|\n)*)")
        # Expresión regular para detectar subsecciones
        self.subsections_re = re.compile(r"--.+--\n")
        # Expresión regular para extraer una subsección y su contenido
        self.subsection_re = re.compile(r"--(?P<name>.+)--\n(?P<text>(.+|\n)*)")

    def is_valid_url(self, url: str) -> bool:   # fullmatching cambiado por fullmatch
        """Verifica si es una dirección válida para indexar

        Args:
            url (str): Dirección a verificar

        Returns:
            bool: True si es valida, en caso contrario False
        """
        return self.wiki_re.fullmatch(url) is not None


    def get_wikipedia_entry_content(self, url: str) -> Optional[Tuple[str, List[str]]]:
        """Devuelve el texto en crudo y los enlaces de un artículo de la wikipedia

        Args:
            url (str): Enlace a un artículo de la Wikipedia

        Returns:
            Optional[Tuple[str, List[str]]]: Si es un enlace correcto a un artículo
                de la Wikipedia en inglés o castellano, devolverá el texto y los
                enlaces que contiene la página.

        Raises:
            ValueError: En caso de que no sea un enlace a un artículo de la Wikipedia
                en inglés o español
        """
        if not self.is_valid_url(url):
            raise ValueError((
                f"El enlace '{url}' no es un artículo de la Wikipedia en español"
            ))

        try:
            req = requests.get(url)
        except Exception as ex:
            print(f"ERROR: - {url} - {ex}")
            return None


        # Solo devolvemos el resultado si la petición ha sido correcta
        if req.status_code == 200:
            soup = bs4.BeautifulSoup(req.text, "lxml")
            urls = set()

            for ele in soup.select((
                'div#catlinks, div.printfooter, div.mw-authority-control'
            )):
                ele.decompose()

            # Recogemos todos los enlaces del contenido del artículo
            for a in soup.select("div#bodyContent a", href=True):
                href = a.get("href")
                if href is not None:
                    urls.add(href)

            # Contenido del artículo
            content = soup.select((
                "h1.firstHeading,"
                "div#mw-content-text h2,"
                "div#mw-content-text h3,"
                "div#mw-content-text h4,"
                "div#mw-content-text p,"
                "div#mw-content-text ul,"
                "div#mw-content-text li,"
                "div#mw-content-text span"
            ))

            dedup_content = []
            seen = set()

            for element in content:
                if element in seen:
                    continue

                dedup_content.append(element)

                # Añadimos a vistos, tanto el elemento como sus descendientes
                for desc in element.descendants:
                    seen.add(desc)

                seen.add(element)

            text = "\n".join(
                self.section_format.get(element.name, "{}").format(element.text)
                for element in dedup_content
            )

            # Eliminamos el texto de las anclas de editar
            text = self.edit_re.sub('', text)

            return text, sorted(list(urls))

        return None


    def parse_wikipedia_textual_content(self, text: str, url: str) -> Optional[Dict[str, Union[str,List]]]:
        """Returns an article-like structure from the raw text

        Args:
            text (str): Raw text of the Wikipedia article
            url (str): URL of the article, to add as a field

        Returns:
            Optional[Dict[str, Union[str,List[Dict[str,Union[str,List[str,str]]]]]]]:
            returns a dictionary with the keys 'url', 'title', 'summary', 'sections':
                The values associated with 'url', 'title', and 'summary' are strings,
                the value associated with 'sections' is a list of possible sections.
                    Each section is a dictionary with 'name', 'text', and 'subsections',
                        the values associated with 'name' and 'text' are strings and,
                        the value associated with 'subsections' is a list of possible subsections
                        in the form of a dictionary with 'name' and 'text'.

            in case of not finding a title or summary of the article, it will return None
        """
        def clean_text(txt):
            return '\n'.join(l for l in txt.split('\n') if len(l) > 0)

        document = {}

        match = self.title_sum_re.match(text)
        if match:
            title = match.group('title')
            summary = match.group('summary')
            rest = match.group('rest')
            document['url'] = url
            document['title'] = title
            document['summary'] = clean_text(summary)
            sections = []

            for sec_match in self.sections_re.finditer(rest):
                sec_text = sec_match.group()
                sec_match = self.section_re.search(sec_text)
                if sec_match:
                    section_name = sec_match.group('name')
                    section_text = sec_match.group('text')
                    subsections = []

                    for subsec_match in self.subsections_re.finditer(section_text):
                        subsec_text = subsec_match.group()
                        subsec_match = self.subsection_re.search(subsec_text)
                        if subsec_match:
                            subsection_name = subsec_match.group('name')
                            subsection_text = subsec_match.group('text')
                            subsections.append({
                                'name': subsection_name,
                                'text': clean_text(subsection_text)
                            })

                    sections.append({
                        'name': section_name,
                        'text': clean_text(section_text),
                        'subsections': subsections
                    })

            document['sections'] = sections
            return document

        return None



    def save_documents(self,
        documents: List[dict], base_filename: str,
        num_file: Optional[int] = None, total_files: Optional[int] = None
    ):
        """Guarda una lista de documentos (text, url) en un fichero tipo json lines
        (.json). El nombre del fichero se autogenera en base al base_filename,
        el num_file y total_files. Si num_file o total_files es None, entonces el
        fichero de salida es el base_filename.

        Args:
            documents (List[dict]): Lista de documentos.
            base_filename (str): Nombre base del fichero de guardado.
            num_file (Optional[int], optional):
                Posición numérica del fichero a escribir. (None por defecto)
            total_files (Optional[int], optional):
                Cantidad de ficheros que se espera escribir. (None por defecto)
        """
        assert base_filename.endswith(".json")

        if num_file is not None and total_files is not None:
            # Separamos el nombre del fichero y la extensión
            base, ext = os.path.splitext(base_filename)
            # Padding que vamos a tener en los números
            padding = len(str(total_files))

            out_filename = f"{base}_{num_file:0{padding}d}_{total_files}{ext}"

        else:
            out_filename = base_filename

        with open(out_filename, "w", encoding="utf-8", newline="\n") as ofile:
            for doc in documents:
                print(json.dumps(doc, ensure_ascii=True), file=ofile)


    def start_crawling(self, 
                    initial_urls: List[str], document_limit: int,
                    base_filename: str, batch_size: Optional[int], max_depth_level: int, # DAVID
                    ):        
         

        """Comienza la captura de entradas de la Wikipedia a partir de una lista de urls válidas, 
            termina cuando no hay urls en la cola o llega al máximo de documentos a capturar.
        
        Args:
            initial_urls: Direcciones a artículos de la Wikipedia
            document_limit (int): Máximo número de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.
            max_depth_level (int): Profundidad máxima de captura.
        """

        # URLs válidas, ya visitadas (se hayan procesado, o no, correctamente)
        visited = set()
        # URLs en cola
        to_process = set(initial_urls)
        # Direcciones a visitar
        queue = [(0, "", url) for url in to_process]
        hq.heapify(queue)
        # Buffer de documentos capturados
        documents: List[dict] = []
        # Contador del número de documentos capturados
        total_documents_captured = 0
        # Contador del número de ficheros escritos
        files_count = 0

        # En caso de que no utilicemos batch_size, asignamos None a total_files
        # así el guardado no modificará el nombre del fichero base
        if batch_size is None:
            total_files = None
        else:
            # Suponemos que vamos a poder alcanzar el límite para la nomenclatura
            # de guardado
            total_files = math.ceil(document_limit / batch_size)

        # Repetimos el proceso hasta que no haya urls en la cola o se alcance el límite de documentos
        while queue and total_documents_captured < document_limit:
            # 1. Seleccionamos una página no procesada de la cola de prioridad
            depth, parent_url, current_url = hq.heappop(queue)
            while current_url in visited:
                if not queue:
                    break
                depth, parent_url, current_url = hq.heappop(queue)
            if current_url in visited:
                continue
            visited.add(current_url)
            
            # 2. Descarga el contenido textual de la página y los enlaces que aparecen en ella.
            content = self.get_wikipedia_entry_content(current_url)
            if content is not None:
                text, links = content

                # 3. Añadir, si procede, los enlaces a la cola de páginas pendientes de procesar.
                for link in links:
                    # Transformar en absoluta
                    absolute_url = urljoin(current_url, link)
                    # Es válida y no supera la profundidad máxima
                    if self.is_valid_url(absolute_url) and depth < max_depth_level:
                        # No se ha visitado y no se ha añadido para procesar
                        if absolute_url not in visited and absolute_url not in to_process:
                            to_process.add(absolute_url)
                            hq.heappush(queue, (depth + 1, current_url, absolute_url))

                # 4. Analizar el contenido textual para generar el diccionario con el contenido estructurado del artículo.
                document = self.parse_wikipedia_textual_content(text, current_url)
                if document is not None:
                    documents.append(document)
                    total_documents_captured += 1
                    # Guardar los documentos en un fichero si se alcanza el batch_size
                    if batch_size is not None and total_documents_captured % batch_size == 0:
                        files_count += 1
                        self.save_documents(documents, base_filename, files_count, total_files)
                        documents = []

        # Guardar los documentos restantes al finalizar
        if documents:
            files_count += 1
            self.save_documents(documents, base_filename, files_count, total_files)


    def wikipedia_crawling_from_url(self,
        initial_url: str, document_limit: int, base_filename: str,
        batch_size: Optional[int], max_depth_level: int
    ):
        """Captura un conjunto de entradas de la Wikipedia, hasta terminar
        o llegar al máximo de documentos a capturar.
        
        Args:
            initial_url (str): Dirección a un artículo de la Wikipedia
            document_limit (int): Máximo número de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.
            max_depth_level (int): Profundidad máxima de captura.
        """
        if not self.is_valid_url(initial_url) and not initial_url.startswith("/wiki/"):
            raise ValueError(
                "Es necesario partir de un artículo de la Wikipedia en español"
            )

        self.start_crawling(initial_urls=[initial_url], document_limit=document_limit, base_filename=base_filename,
                            batch_size=batch_size, max_depth_level=max_depth_level)



    def wikipedia_crawling_from_url_list(self,
        urls_filename: str, document_limit: int, base_filename: str,
        batch_size: Optional[int]
    ):
        """A partir de un fichero de direcciones, captura todas aquellas que sean
        artículos de la Wikipedia válidos

        Args:
            urls_filename (str): Lista de direcciones
            document_limit (int): Límite máximo de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.

        """

        urls = []
        with open(urls_filename, "r", encoding="utf-8") as ifile:
            for url in ifile:
                url = url.strip()

                # Comprobamos si es una dirección a un artículo de la Wikipedia
                if self.is_valid_url(url):
                    if not url.startswith("http"):
                        raise ValueError(
                            "El fichero debe contener URLs absolutas"
                        )

                    urls.append(url)

        urls = list(set(urls)) # eliminamos posibles duplicados

        self.start_crawling(initial_urls=urls, document_limit=document_limit, base_filename=base_filename,
                            batch_size=batch_size, max_depth_level=0)




if __name__ == "__main__":
    raise Exception(
        "Esto es una librería y no se puede usar como fichero ejecutable"
    )
