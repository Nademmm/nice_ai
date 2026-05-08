import sys
sys.path.insert(0, '.')

from app.services.rag_service import IntentDetector
from app.services.response_builder import response_builder

user_query = 'dimana letak perusahaannya'
intent = IntentDetector.detect(user_query)
print(f'Query: {user_query}')
print(f'Detected Intent: {intent}')
print()

# Test response with company docs
docs = [{
    'content': 'CV Nice Indonesia\nAlamat: Jl. Medan No. 123, Jakarta\nJam operasional: Senin-Jumat 08:00-17:00\nTelepon: 0821-1234-5678',
    'metadata': {'type': 'uploaded_knowledge', 'source': 'cv_nice.pdf', 'category': 'deskripsi'}
}]

response = response_builder.build_response(intent, docs, user_query)
print('Response:')
print(response)
