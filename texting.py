from SAR_lib_plantilla import SAR_Indexer

searcher = SAR_Indexer()
p1:list = [1,2,3,4,5,3,2,1]
p2:list = [2,4,5,1,1]

print(searcher.and_posting(p1,p2))

print(searcher.or_posting(p1,p2))

print(searcher.minus_posting(p1,p2))