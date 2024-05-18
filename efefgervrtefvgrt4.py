import unittest

class TestSARWikiCrawler(unittest.TestCase):

    def setUp(self):
        self.crawler = SAR_Crawler_lib.SAR_Wiki_Crawler()

    def test_parse_wikipedia_textual_content(self):
        text = (
            "##Videojuego##\n"
            "Un videojuego, o juego de vídeo es un juego electrónico en el que una o más personas ...\n"
            "==Historia==\n"
            "Los orígenes del videojuego se remontan a la década de 1950, cuando poco después de la ...\n"
            "==Generalidades==\n"
            "Típicamente, los videojuegos recrean entornos y situaciones virtuales en los que el ....\n"
            "--Tecnología--\n"
            "Un videojuego se ejecuta gracias a un programa de software (el videojuego en sí) que es ...\n"
            "--Plataformas--\n"
            "Los distintos tipos de dispositivo en los que se ejecutan los videojuegos se conocen como ...\n"
        )
        url = "https://es.wikipedia.org/wiki/Videojuego"
        expected_output = {
            "url": "https://es.wikipedia.org/wiki/Videojuego",
            "title": "Videojuego",
            "summary": "Un videojuego, o juego de vídeo es un juego electrónico en el que una o más personas ...",
            "sections": [
                {
                    "name": "Historia",
                    "text": "Los orígenes del videojuego se remontan a la década de 1950, cuando poco después de la ...",
                    "subsections": []
                },
                {
                    "name": "Generalidades",
                    "text": "Típicamente, los videojuegos recrean entornos y situaciones virtuales en los que el ....",
                    "subsections": [
                        {
                            "name": "Tecnología",
                            "text": "Un videojuego se ejecuta gracias a un programa de software (el videojuego en sí) que es ..."
                        },
                        {
                            "name": "Plataformas",
                            "text": "Los distintos tipos de dispositivo en los que se ejecutan los videojuegos se conocen como ..."
                        }
                    ]
                }
            ]
        }

        result = self.crawler.parse_wikipedia_textual_content(text, url)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
