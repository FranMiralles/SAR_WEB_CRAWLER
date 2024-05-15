from SAR_Crawler_lib import SAR_Wiki_Crawler

def main():
    # Inicializar el crawler
    crawler = SAR_Wiki_Crawler()

    # Definir la URL de prueba
    test_url = "https://es.wikipedia.org/wiki/Oric_1"

    # Obtener el contenido del artículo de Wikipedia
    content = crawler.get_wikipedia_entry_content(test_url)
    if content is None:
        print("No se pudo obtener el contenido del artículo.")
        return

    text, links = content

    # Mostrar el contenido crudo obtenido
    print("Contenido crudo del artículo:\n")
    print(text)

    # Parsear el contenido crudo
    parsed_content = crawler.parse_wikipedia_textual_content(text, test_url)
    if parsed_content is None:
        print("No se pudo parsear el contenido del artículo.")
        return

    # Mostrar el contenido parseado
    print("\nContenido parseado del artículo:\n")
    print(parsed_content)

if __name__ == "__main__":
    main()
