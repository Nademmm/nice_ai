"""Test script untuk melihat hasil formatting response yang baru."""
import sys
sys.path.append('.')

from app.services.response_builder import RuleBasedResponseBuilder

print("="*80)
print("TEST: RESPONSE FORMATTING IMPROVEMENTS")
print("="*80)

# Test Product Recommendation
print("\n1️⃣ PRODUCT RECOMMENDATION FORMATTING:")
print("-" * 50)

# Mock product data
mock_products = [
    {
        "content": "Produk: PJUTS 40W\nSpesifikasi:\n- Watt: 40W\n- Battery: 20Ah LiFePO4\n- Tinggi Tiang: 4-5 meter\n- Cocok untuk: area sempit, persawahan, jalan gang kecil, taman komunal\n- Durasi Penerangan: 6-8 jam\n- Area Coverage: Optimal untuk area hingga 100m persegi",
        "metadata": {"type": "product"},
        "distance": 0.3
    },
    {
        "content": "Produk: PJUTS 60W\nSpesifikasi:\n- Watt: 60W\n- Battery: 40Ah LiFePO4\n- Tinggi Tiang: 5-6 meter\n- Cocok untuk: jalan residential, perumahan, jalan lingkungan, pabrik kecil\n- Durasi Penerangan: 10-12 jam\n- Area Coverage: Optimal untuk area 200-300m persegi dengan iluminasi bagus",
        "metadata": {"type": "product"},
        "distance": 0.5
    }
]

user_input = "Saya butuh lampu untuk taman rumah saya"
response = RuleBasedResponseBuilder.build_product_recommendation(mock_products, user_input)
print(response)

# Test FAQ Response
print("\n\n2️⃣ FAQ RESPONSE FORMATTING:")
print("-" * 50)

mock_faq = [
    {
        "content": "FAQ: Berapa harga PJUTS?\nJawaban: Harga PJUTS tergantung kapasitas watt dan spesifikasi. PJUTS 40W mulai dari Rp 3-4 juta, 60W Rp 4-5 juta, 80W Rp 5-7 juta, 100W Rp 7-8 juta, dan 120W Rp 8-10 juta. Harga bisa lebih murah untuk pembelian dalam jumlah besar. Hubungi tim kami untuk penawaran khusus.",
        "metadata": {"type": "faq"},
        "distance": 0.1
    }
]

faq_response = RuleBasedResponseBuilder.build_faq_answer(mock_faq, "harga")
print(faq_response)

# Test Company Info
print("\n\n3️⃣ COMPANY INFO FORMATTING:")
print("-" * 50)

mock_company = [
    {
        "content": "CV Niscahya Indonesia Cerdas adalah perusahaan yang bergerak di bidang energi terbarukan, khususnya specializes dalam produk PJUTS (Penerangan Jalan Umum Tenaga Surya) / PJU Tenaga Surya.\n\nProfil Perusahaan:\n- Nama: CV Niscahya Indonesia Cerdas\n- Bidang: Energi Terbarukan - Solar Street Lighting\n- Produk Utama: PJUTS / PJU Tenaga Surya berbagai kapasitas\n\nVisi: Menjadi perusahaan terdepan dalam penyediaan solusi penerangan jalan umum berbasis tenaga surya di Indonesia.\n\nMisi:\n1. Menyediakan produk PJUTS berkualitas tinggi\n2. Memberikan layanan terbaik kepada pelanggan\n3. Mendukung program pemerintah dalam penggunaan energi terbarukan\n4. Ikut serta dalam pembangunan infrastruktur hijau di Indonesia\n\nLayanan:\n- Konsultasi produk PJUTS\n- Penjualan lampu jalan tenaga surya\n- Jasa instalação / pemasangan\n- Pengiriman ke seluruh Indonesia\n- Garansi produk",
        "metadata": {"type": "company_info"},
        "distance": 0.2
    }
]

company_response = RuleBasedResponseBuilder.build_company_info(mock_company)
print(company_response)

# Test Lead Capture
print("\n\n4️⃣ LEAD CAPTURE FORMATTING:")
print("-" * 50)

lead_response = RuleBasedResponseBuilder.build_lead_capture("saya mau pesan")
print(lead_response)

print("\n" + "="*80)
print("✅ FORMATTING TEST COMPLETE")
print("Jawaban chatbot sekarang lebih rapi dan mudah dibaca!")
print("="*80)