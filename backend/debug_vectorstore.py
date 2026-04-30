#!/usr/bin/env python
from app.services.vector_store import vector_store
from app.services.rag_service import rag_service

print('=' * 60)
print('VECTOR STORE DEBUG')
print('=' * 60)
print()

print(f'Total documents in vector store: {vector_store.count_documents()}')
print()

if vector_store.count_documents() > 0:
    print('Documents found:')
    all_docs = vector_store.get_all_documents()
    for i, doc in enumerate(all_docs[:5], 1):
        print(f'\n--- Doc {i} ---')
        print(f'ID: {doc["id"]}')
        print(f'Type: {doc["metadata"].get("type", "N/A")}')
        print(f'Content (first 150 chars): {doc["content"][:150]}...')
else:
    print('NO DOCUMENTS IN VECTOR STORE!')
    print('\nAttempting to load PDFs from uploads folder...')
    loaded = rag_service.load_pdf_from_uploads()
    print(f'Loaded {loaded} PDFs')
    print(f'Total documents after load: {vector_store.count_documents()}')
    
    if vector_store.count_documents() > 0:
        all_docs = vector_store.get_all_documents()
        for i, doc in enumerate(all_docs[:3], 1):
            print(f'\n--- Doc {i} ---')
            print(f'ID: {doc["id"]}')
            print(f'Type: {doc["metadata"].get("type", "N/A")}')
            print(f'Content (first 100 chars): {doc["content"][:100]}...')

print('\n' + '=' * 60)

# Test search
print('\nTesting search with query: "Berapa harga PJUTS 60W?"')
results = vector_store.search("Berapa harga PJUTS 60W?", n_results=5)
print(f'Search results: {len(results)} found')
for i, result in enumerate(results, 1):
    print(f'\nResult {i}:')
    print(f'  Distance: {result.get("distance", "N/A")}')
    print(f'  Type: {result.get("metadata", {}).get("type", "N/A")}')
    print(f'  Content (first 100 chars): {result.get("content", "")[:100]}...')
