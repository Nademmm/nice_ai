import sys
sys.path.insert(0, '.')

# Test response builder dengan mock context
from app.services.response_builder import response_builder

test_docs = [
    {
        "content": "Produk: PJUTS 60W\nSpesifikasi:\n- Watt: 60W\n- Battery: 40Ah\n- Tinggi Tiang: 5-6 meter\n- Cocok untuk: jalan residential, perumahan\n- Durasi Penerangan: 10-12 jam",
        "metadata": {"type": "product", "name": "PJUTS 60W"}
    }
]

# Test product recommendation
result = response_builder.build_response("product_recommendation", test_docs, "Saya butuh lampu jalan untuk area residential")
print("=== PRODUCT RECOMMENDATION ===")
print(result)
print("\n=== COMPANY INFO ===")
result = response_builder.build_response("company_info", test_docs)
print(result)
