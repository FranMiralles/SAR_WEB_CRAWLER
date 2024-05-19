import unittest

class TestSAR_Wiki_Crawler(unittest.TestCase):
    def setUp(self):
        self.crawler = SAR_Wiki_Crawler()
        self.sample_text_1 = """##Title##
Summary of the article that spans multiple lines and provides a brief overview.
==Section 1==
This is the text of section 1.
--Subsection 1.1--
Text of subsection 1.1.
==Section 2==
This is the text of section 2 without subsections.
"""
        self.sample_url_1 = "https://es.wikipedia.org/wiki/Sample"

    def test_parse_wikipedia_textual_content_basic(self):
        result = self.crawler.parse_wikipedia_textual_content(self.sample_text_1, self.sample_url_1)
        expected = {
            "url": "https://es.wikipedia.org/wiki/Sample",
            "title": "Title",
            "summary": "Summary of the article that spans multiple lines and provides a brief overview.",
            "sections": [
                {
                    "name": "Section 1",
                    "text": "This is the text of section 1.",
                    "subsections": [
                        {
                            "name": "Subsection 1.1",
                            "text": "Text of subsection 1.1."
                        }
                    ]
                },
                {
                    "name": "Section 2",
                    "text": "This is the text of section 2 without subsections.",
                    "subsections": []
                }
            ]
        }
        self.assertEqual(result, expected)

    def test_parse_wikipedia_textual_content_no_sections(self):
        text = "##Title##\nSummary only with no sections."
        result = self.crawler.parse_wikipedia_textual_content(text, self.sample_url_1)
        expected = {
            "url": "https://es.wikipedia.org/wiki/Sample",
            "title": "Title",
            "summary": "Summary only with no sections.",
            "sections": []
        }
        self.assertEqual(result, expected)

    def test_parse_wikipedia_textual_content_no_summary(self):
        text = "##Title##\n==Section 1==\nText of section 1."
        result = self.crawler.parse_wikipedia_textual_content(text, self.sample_url_1)
        self.assertIsNone(result)

    def test_parse_wikipedia_textual_content_complex(self):
        text = """##Complex Title##
Complex summary that has multiple sections and subsections.
==Main Section==
Main section text.
--Subsection A--
Text of Subsection A.
--Subsection B--
Text of Subsection B.
==Another Section==
Text of another section.
"""
        result = self.crawler.parse_wikipedia_textual_content(text, self.sample_url_1)
        expected = {
            "url": "https://es.wikipedia.org/wiki/Sample",
            "title": "Complex Title",
            "summary": "Complex summary that has multiple sections and subsections.",
            "sections": [
                {
                    "name": "Main Section",
                    "text": "Main section text.",
                    "subsections": [
                        {
                            "name": "Subsection A",
                            "text": "Text of Subsection A."
                        },
                        {
                            "name": "Subsection B",
                            "text": "Text of Subsection B."
                        }
                    ]
                },
                {
                    "name": "Another Section",
                    "text": "Text of another section.",
                    "subsections": []
                }
            ]
        }
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
