import SAR_Crawler_lib 

# Definir las URLs iniciales
initial_urls = [
    "https://es.wikipedia.org/wiki/oric_1",

]

document_limit = 200
base_filename = "wikipedia_articles.json"
max_depth_level = 4

crawler = SAR_Crawler_lib.SAR_Wiki_Crawler()


crawler.start_crawling(initial_urls, document_limit, base_filename, 5, max_depth_level)