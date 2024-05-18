import SAR_Crawler_lib 

# Definir las URLs iniciales
initial_urls = [
    "https://es.wikipedia.org/wiki/oric_1",

]

document_limit = 2
base_filename = "wikipedia_articles.json"
max_depth_level = 3

crawler = SAR_Crawler_lib.SAR_Wiki_Crawler()


crawler.start_crawling(initial_urls, document_limit, base_filename, None, max_depth_level)