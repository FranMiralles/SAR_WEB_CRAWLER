from SAR_lib import SAR_Indexer

searcher = SAR_Indexer()
p1:list = [1,2,3,4,5]
p2:list = [1,2,4,5]

print(searcher.and_posting(p1,p2))

print(searcher.or_posting(p1,p2))

print(searcher.minus_posting(p1,p2))


