from app.services.vector_store import vector_store

results = vector_store.search('lampu', n_results=5)
print('Search results for "lampu":')
for i, doc in enumerate(results):
    print(f'{i+1}. Distance: {doc.get("distance", "N/A"):.3f}')
    print(f'   Content: {doc["content"][:200]}...')
    print(f'   Metadata: {doc["metadata"]}')
    print()