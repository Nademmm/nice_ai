from typing import Dict, List, Optional
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
import os
import PyPDF2
import io
from pathlib import Path


COMPANY_INFO = """
CV Niscahya Indonesia Cerdas adalah perusahaan yang bergerak di bidang energi terbarukan,
khususnya specializes dalam produk PJUTS (Penerangan Jalan Umum Tenaga Surya) / PJU Tenaga Surya.

Profil Perusahaan:
- Nama: CV Niscahya Indonesia Cerdas
- Bidang: Energi Terbarukan - Solar Street Lighting
- Produk Utama: PJUTS / PJU Tenaga Surya berbagai kapasitas

Visi: Menjadi perusahaan terdepan dalam penyediaan solusi penerangan jalan umum berbasis tenaga surya di Indonesia.

Misi:
1. Menyediakan produk PJUTS berkualitas tinggi
2. Memberikan layanan terbaik kepada pelanggan
3. Mendukung program pemerintah dalam penggunaan energi terbarukan
4. Ikut serta dalam pembangunan infrastruktur hijau di Indonesia

Layanan:
- Konsultasi produk PJUTS
- Penjualan lampu jalan tenaga surya
- Jasa instalação / pemasangan
- Pengiriman ke seluruh Indonesia
- Garansi produk

Kontak:
- Alamat: [Alamat kantor]
- WhatsApp: [Nomor WhatsApp]
- Email: [Email]
"""

SYSTEM_INSTRUCTION = """Anda adalah asisten virtual dari CV Niscahya Indonesia Cerdas,
perusahaan specializing dalam produk PJUTS (Penerangan Jalan Umum Tenaga Surya).

Tugas Anda:
1. Menjawab pertanyaan tentang perusahaan dengan profesional
2. Merekomendasikan produk PJUTS yang sesuai kebutuhan
3. Menjawab pertanyaan seputar harga, garansi, pengiriman, dan pemasangan
4. Mengumpulkan lead customer (nama, WhatsApp, kebutuhan proyek)

Selalu jawab dalam Bahasa Indonesia dengan ramah dan profesional.
Jika customer tertarik, minta informasi kontak mereka untuk follow-up.
"""


PRODUCT_RECOMMENDATION_PROMPT = """Berdasarkan kebutuhan customer berikut, rekomendasikan produk PJUTS yang sesuai:

Kebutuhan: {user_input}

Produk yang tersedia:
- PJUTS 40W: Untuk area sempit/persawahan, tiang 4-5 meter
- PJUTS 60W: Untuk jalan residential, tiang 5-6 meter
- PJUTS 80W: Untuk jalan protokol, tiang 6-7 meter
- PJUTS 100W: Untuk jalan utama/freeway, tiang 7-8 meter
- PJUTS 120W: Untuk area industri/parkiran, tiang 8-9 meter

Rekomendasi battery capacity:
- 20Ah: untuk penerangan 6-8 jam
- 40Ah: untuk penerangan 10-12 jam
- 50Ah: untuk penerangan 12-14 jam
- 80Ah: untuk penerangan 18-20 jam

Berikan rekomendasi produk dalam format:
Produk: [Nama Produk]
Watt: [Wattage]
Battery: [Kapasitas Battery]
Alasan: [Mengapa produk ini cocok]
"""


class IntentDetector:
    INTENT_KEYWORDS = {
        "company_info": [
            ("tentang perusahaan", 5), ("profil perusahaan", 5), ("visi", 4), ("misi", 4),
            ("siapa itu", 4), ("siapa kalian", 4), ("alamat", 3), ("kontak", 3), 
            ("Indonesia Cerdas", 5), ("tentang niscahya", 5)
        ],
        "product_recommendation": [
            ("butuh", 4), ("rekomendasi produk", 5), ("lampu jalan", 5), ("PJUTS", 5),
            ("tenaga surya", 4), ("cocok untuk", 4), ("area apa", 4), ("area mana", 4),
            ("sesuai", 3), ("mana produk", 4), ("produk mana", 4)
        ],
        "faq": [
            ("harga", 5), ("berapa harga", 5), ("harga produk", 5), ("berapa", 4),
            ("garansi", 5), ("ada garansi", 4), ("kirim", 4), ("pengiriman", 4),
            ("pemasangan", 4), ("instalasi", 4), ("maintenance", 4), ("umur baterai", 5),
            ("berapa lama", 3), ("bagaimana", 3), ("apa saja", 3)
        ],
        "lead": [
            ("tertarik", 5), ("pesan", 4), ("order", 4), ("hubungi", 4), ("WhatsApp", 4),
            ("telepon", 3), ("konsultasi", 3), ("mau beli", 5), ("mau pesan", 5)
        ]
    }

    @classmethod
    def detect(cls, message: str) -> str:
        """Detect intent dengan weighted scoring untuk akurasi lebih baik."""
        message_lower = message.lower()
        scores = {}

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            score = 0
            for keyword, weight in keywords:
                if keyword.lower() in message_lower:
                    score += weight
            scores[intent] = score

        # Jika semua score 0, return general
        if max(scores.values()) == 0:
            return "general"

        # Return intent dengan score tertinggi
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # Jika score terlalu rendah, mungkin general question
        if best_score < 2:
            return "general"
        
        return best_intent


class RAGService:
    def __init__(self):
        self.vector_store = vector_store
        self.llm = llm_service

    def load_pdf_from_uploads(self):
        """Load semua PDF dari folder uploads dan add ke vector store."""
        uploads_dir = Path("./uploads")
        if not uploads_dir.exists():
            print("[INIT] No uploads directory found")
            return 0
        
        pdf_count = 0
        for pdf_file in uploads_dir.glob("*.pdf"):
            try:
                print(f"[INIT] Loading PDF: {pdf_file.name}")
                with open(pdf_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    # Simpan setiap halaman sebagai dokumen terpisah
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        
                        if text.strip():
                            self.vector_store.add_document(
                                text=text,
                                metadata={
                                    "type": "uploaded_knowledge",
                                    "source": pdf_file.name,
                                    "file_type": "pdf",
                                    "page": page_num + 1
                                },
                                document_id=f"pdf_{pdf_file.stem.replace(' ', '_')}_page_{page_num + 1}"
                            )
                            pdf_count += 1
                    print(f"[INIT] Loaded {pdf_file.name} ({len(pdf_reader.pages)} pages)")
            except Exception as e:
                print(f"[INIT] Error loading {pdf_file.name}: {str(e)}")
        
        return pdf_count

    def initialize_default_knowledge(self):
        # First, try to load PDFs from uploads folder
        print("[INIT] Starting knowledge base initialization...")
        pdf_count = self.load_pdf_from_uploads()
        
        if pdf_count > 0:
            print(f"[INIT] Loaded {pdf_count} PDF files from uploads folder!")
            print(f"[INIT] Total docs in vector store: {self.vector_store.count_documents()}")
            return
        
        # If no PDFs found, load default knowledge base
        if self.vector_store.count_documents() == 0:
            print("[INIT] No PDFs found. Loading default knowledge base...")
            self.vector_store.add_document(
                text=COMPANY_INFO,
                metadata={"type": "company_info", "source": "default"},
                document_id="company_info_default"
            )
            print(f"[INIT] Added company info. Total docs: {self.vector_store.count_documents()}")

            products = [
                {
                    "name": "PJUTS 40W",
                    "watt": "40W",
                    "battery": "20Ah LiFePO4",
                    "pole_height": "4-5 meter",
                    "suitable_for": "area sempit, persawahan, jalan gang kecil, taman komunal",
                    "lighting_duration": "6-8 jam",
                    "coverage_area": "Optimal untuk area hingga 100m persegi"
                },
                {
                    "name": "PJUTS 60W",
                    "watt": "60W",
                    "battery": "40Ah LiFePO4",
                    "pole_height": "5-6 meter",
                    "suitable_for": "jalan residential, perumahan, jalan lingkungan, pabrik kecil",
                    "lighting_duration": "10-12 jam",
                    "coverage_area": "Optimal untuk area 200-300m persegi dengan iluminasi bagus"
                },
                {
                    "name": "PJUTS 80W",
                    "watt": "80W",
                    "battery": "40Ah LiFePO4",
                    "pole_height": "6-7 meter",
                    "suitable_for": "jalan protokol, jalan kota, main street, industrial area kecil",
                    "lighting_duration": "12-14 jam",
                    "coverage_area": "Optimal untuk area 400-500m persegi dengan coverage luas"
                },
                {
                    "name": "PJUTS 100W",
                    "watt": "100W",
                    "battery": "50Ah LiFePO4",
                    "pole_height": "7-8 meter",
                    "suitable_for": "jalan utama, freeway, highway, area komersial, parking area",
                    "lighting_duration": "14-16 jam",
                    "coverage_area": "Optimal untuk area 600-800m persegi dengan brightness tinggi"
                },
                {
                    "name": "PJUTS 120W",
                    "watt": "120W",
                    "battery": "80Ah LiFePO4",
                    "pole_height": "8-9 meter",
                    "suitable_for": "area industri besar, parkiran komersial, toll booth, stadion",
                    "lighting_duration": "18-20 jam",
                    "coverage_area": "Optimal untuk area 1000m+ persegi dengan illuminasi maksimal"
                }
            ]

            for i, product in enumerate(products):
                self.vector_store.add_document(
                    text=f"Produk: {product['name']}\nSpesifikasi:\n- Watt: {product['watt']}\n- Battery: {product['battery']}\n- Tinggi Tiang: {product['pole_height']}\n- Cocok untuk: {product['suitable_for']}\n- Durasi Penerangan: {product['lighting_duration']}\n- Area Coverage: {product['coverage_area']}",
                    metadata={"type": "product", "source": "catalog", "name": product['name']},
                    document_id=f"product_{i}_{product['name'].replace(' ', '_')}"
                )
            print(f"[INIT] Added {len(products)} products. Total docs: {self.vector_store.count_documents()}")

            faq_data = [
                {"question": "Berapa harga PJUTS?", "answer": "Harga PJUTS tergantung kapasitas watt dan spesifikasi. PJUTS 40W mulai dari Rp 3-4 juta, 60W Rp 4-5 juta, 80W Rp 5-7 juta, 100W Rp 7-8 juta, dan 120W Rp 8-10 juta. Harga bisa lebih murah untuk pembelian dalam jumlah besar. Hubungi tim kami untuk penawaran khusus."},
                {"question": "Apakah ada garansi?", "answer": "Ya, kami memberikan garansi 5 tahun untuk komponen utama (solar panel, baterai LiFePO4, controller). Garansi mencakup material defect dan performa panel minimal 80% di tahun ke-5. Layanan purna jual termasuk penggantian spare part dan support teknis."},
                {"question": "Apakah bisa kirim ke luar kota?", "answer": "Ya, kami melayani pengiriman ke seluruh Indonesia via kurir profesional. Untuk Jawa pengiriman 1-3 hari, luar Jawa 3-5 hari kerja. Kami juga siap kirim ke proyek dengan penanganan khusus untuk peralatan berat. Biaya pengiriman disesuaikan dengan lokasi."},
                {"question": "Apakah ada jasa pemasangan?", "answer": "Ya, kami menyediakan jasa instalasi profesional oleh teknisi bersertifikat. Biaya jasa pemasangan tergantung lokasi dan kompleksitas proyek. Kami akan melakukan surveі lokasi terlebih dahulu untuk memberikan penawaran akurat. Tim kami dapat menangani proyek skala kecil hingga besar."},
                {"question": "Berapa lama umur baterai?", "answer": "Baterai LiFePO4 yang kami gunakan memiliki durasi hidup 5-7 tahun atau 2000-3000 siklus charge-discharge. Dengan maintenance rutin dan operasional yang baik, baterai bisa bertahan lebih lama. Kapasitas akan menurun gradual, di tahun ke-5 masih mencapai 80% kapasitas normal."},
                {"question": "Bagaimana maintenance PJUTS?", "answer": "Maintenance PJUTS cukup simple: (1) Bersihkan panel surya setiap 2-3 bulan dari debu dan kotoran. (2) Periksa koneksi kabel setiap 6 bulan. (3) Monitoring software untuk checking kondisi baterai. (4) Ganti spare parts jika ada yang rusak. Kami menyediakan maintenance package tahunan dengan harga terjangkau."}
            ]

            for i, faq in enumerate(faq_data):
                self.vector_store.add_document(
                    text=f"FAQ: {faq['question']}\nJawaban: {faq['answer']}",
                    metadata={"type": "faq", "source": "default"},
                    document_id=f"faq_{i}"
                )
            print(f"[INIT] Added {len(faq_data)} FAQs. Total docs: {self.vector_store.count_documents()}")
            print(f"[INIT] Knowledge base initialization complete!")

    async def process_message(self, message: str, session_id: str = None) -> Dict:
        intent = IntentDetector.detect(message)

        # Search context dengan distance score
        context_docs = self.vector_store.search(message, n_results=10)
        
        # Re-rank dokumen: prioritize by type relevance + distance
        context_docs = self._rank_documents_by_intent(context_docs, intent)

        # Generate response dengan ranked context docs
        response = await self.llm.generate_response(
            prompt=PRODUCT_RECOMMENDATION_PROMPT.format(user_input=message),
            system_instruction=SYSTEM_INSTRUCTION,
            intent=intent,
            context_docs=context_docs,
            user_input=message
        )

        recommended_product = None
        if intent == "product_recommendation" and context_docs:
            for doc in context_docs:
                if doc['metadata'].get('type') == 'product':
                    recommended_product = {
                        "name": doc['metadata'].get('name', 'Unknown'),
                        "watt": "See details",
                        "battery": "See details"
                    }
                    break

        return {
            "answer": response,
            "intent": intent,
            "product": recommended_product
        }

    def _rank_documents_by_intent(self, docs: List[Dict], intent: str) -> List[Dict]:
        """Re-rank dokumen berdasarkan intent + distance untuk relevance lebih tinggi.
        Prioritize uploaded knowledge dari PDF.
        
        Filter out low-relevance docs (distance > threshold) sebelum return.
        """
        # Similarity threshold - Chroma distance 0-2, semakin kecil = lebih relevan
        # 1.5 improves recall for short user queries while remaining reasonably precise
        SIMILARITY_THRESHOLD = 1.5
        
        # Separate uploaded vs default knowledge
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('type') == 'uploaded_knowledge']
        other_docs = [d for d in docs if d.get('metadata', {}).get('type') != 'uploaded_knowledge']
        
        # Intent-to-type mapping
        intent_types = {
            "company_info": ["company_info", "uploaded_knowledge"],
            "product_recommendation": ["product", "uploaded_knowledge"],
            "faq": ["faq", "uploaded_knowledge"],
            "lead": ["product", "company_info", "uploaded_knowledge"],
            "general": ["product", "company_info", "faq", "uploaded_knowledge"]
        }

        target_types = intent_types.get(intent, [])
        
        # Process uploaded docs first with lenient filtering
        ranked_uploaded = []
        for doc in uploaded_docs:
            distance = doc.get("distance", 999)
            # Less strict filtering for uploaded knowledge
            if distance <= SIMILARITY_THRESHOLD + 0.4:  # More lenient
                ranked_uploaded.append((0, distance, doc))  # Priority 0 = highest
        
        # Process other docs
        ranked_other = []
        for doc in other_docs:
            distance = doc.get("distance", 999)
            
            # Skip jika distance terlalu jauh
            if distance > SIMILARITY_THRESHOLD:
                continue
            
            doc_type = doc.get("metadata", {}).get("type", "general")
            if doc_type in target_types:
                ranked_other.append((1, distance, doc))  # Priority 1 = medium
            else:
                ranked_other.append((2, distance, doc))  # Priority 2 = low

        # Sort by priority then by distance
        all_ranked = ranked_uploaded + ranked_other
        all_ranked.sort(key=lambda x: (x[0], x[1]))
        
        # Return docs only (drop priority and distance tuples)
        ranked = [doc for _, _, doc in all_ranked]
        return ranked[:5]  # Return max 5


rag_service = RAGService()
