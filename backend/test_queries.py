import requests

url = 'http://127.0.0.1:8000/api/chat'

queries = ['harga', 'produk PJUTS', 'garansi']

for query in queries:
    data = {'message': query, 'session_id': 'test'}
    response = requests.post(url, json=data)
    result = response.json()
    print(f'Query: {query}')
    print(f'Intent: {result["intent"]}')
    print(f'Answer: {result["answer"][:150]}...')
    print('---')