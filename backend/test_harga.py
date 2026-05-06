from app.services.vector_store import vector_store
docs = vector_store.search('harga', n_results=10)
print('Search results for "harga":')
for i, doc in enumerate(docs):
    print(f'{i+1}. Distance: {doc.get("distance", 999):.3f}')
    print(f'   Type: {doc["metadata"].get("type")}')
    print(f'   Content: {doc["content"][:100]}...')
    print()