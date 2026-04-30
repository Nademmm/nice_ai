from typing import Dict, List, Optional
import re


class RuleBasedResponseBuilder:
    """Build natural responses from context documents dengan smart semantic matching."""
    
    # Similarity threshold - jangan ambil dokumen yang distance-nya terlalu jauh
    # Chroma distance: 0 = perfect match, 2 = completely irrelevant
    # 1.5 keeps good precision while improving recall for short/general queries
    SIMILARITY_THRESHOLD = 1.5

    @staticmethod
    def filter_docs_by_type(docs: List[Dict], doc_type: str) -> List[Dict]:
        """Filter dokumen berdasarkan type metadata."""
        return [d for d in docs if d.get("metadata", {}).get("type") == doc_type]

    @staticmethod
    def filter_relevant_docs(docs: List[Dict], threshold: float = SIMILARITY_THRESHOLD) -> List[Dict]:
        """Filter docs berdasarkan similarity threshold - exclude low relevance docs."""
        return [d for d in docs if d.get("distance", 999) <= threshold]

    @staticmethod
    def extract_faq_answer(content: str) -> str:
        """Extract hanya bagian jawaban dari FAQ format."""
        if "Jawaban:" in content:
            return content.split("Jawaban:")[-1].strip()
        return content.strip()

    @staticmethod
    def find_matching_faq(docs: List[Dict], question: str) -> Optional[Dict]:
        """Cari FAQ yang paling match dengan user question - exact atau semantic."""
        faq_docs = RuleBasedResponseBuilder.filter_docs_by_type(docs, "faq")
        if not faq_docs:
            return None
        
        # Sort by distance (relevance) - ambil yang paling relevan
        faq_docs_sorted = sorted(faq_docs, key=lambda x: x.get("distance", 999))
        
        # Return yang paling relevan
        if faq_docs_sorted and faq_docs_sorted[0].get("distance", 999) <= RuleBasedResponseBuilder.SIMILARITY_THRESHOLD:
            return faq_docs_sorted[0]
        
        return None

    @staticmethod
    def build_product_recommendation(docs: List[Dict], user_input: str) -> str:
        """Rekomendasi produk dengan smart relevance filtering - prioritize uploaded knowledge."""
        # Priority 1: uploaded knowledge dari PDF
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('type') == 'uploaded_knowledge']
        if uploaded_docs:
            # Filter by relevance
            relevant_uploaded = RuleBasedResponseBuilder.filter_relevant_docs(uploaded_docs)
            if relevant_uploaded:
                response = "Halo, saya bantu rekomendasikan produk yang paling sesuai berdasarkan dokumen kami.\n\n✨ Berdasarkan database produk kami, berikut rekomendasi yang sesuai kebutuhan Anda:\n"
                
                for i, doc in enumerate(relevant_uploaded[:3], 1):  # Max 3 produk
                    content = doc.get("content", "").strip()
                    content = " ".join(content.split())
                    response += f"\n{i}. {content}"
                
                response += "\n\n💡 Hubungi tim kami untuk diskusi detail, penawaran harga khusus, dan jadwal pengiriman. WhatsApp kami siap 24/7!"
                return response
        
        # Priority 2: existing product docs
        products = RuleBasedResponseBuilder.filter_docs_by_type(docs, "product")
        products = RuleBasedResponseBuilder.filter_relevant_docs(products)
        
        if not products:
            return (
                "Halo, saya belum menemukan rekomendasi produk yang spesifik untuk kebutuhan Anda di dokumen aktif. "
                "Namun, tim kami memiliki berbagai solusi PJUTS berkualitas tinggi. "
                "Kalau Anda mau, saya bisa bantu pilihkan produk berdasarkan watt, lokasi, atau lama nyala yang dibutuhkan."
            )

        response = "Halo, saya bantu rekomendasikan produk yang paling sesuai berdasarkan kebutuhan Anda.\n\n✨ Berdasarkan kebutuhan Anda, berikut rekomendasi PJUTS yang paling sesuai:\n"
        
        for i, product in enumerate(products[:2], 1):  # Max 2 produk
            content = product.get("content", "").strip()
            content = " ".join(content.split())
            response += f"\n{i}. {content}"

        response += "\n\n💡 Hubungi tim kami untuk diskusi detail, penawaran harga khusus, dan jadwal pengiriman."
        return response

    @staticmethod
    def build_company_info(docs: List[Dict]) -> str:
        """Info perusahaan dengan relevance filtering."""
        # Cari company_info type
        company_docs = RuleBasedResponseBuilder.filter_docs_by_type(docs, "company_info")
        company_docs = RuleBasedResponseBuilder.filter_relevant_docs(company_docs)
        
        if company_docs:
            content = company_docs[0].get("content", "").strip()
            content = " ".join(content.split())
            return f"Halo, berikut info perusahaan yang saya temukan:\n\n{content}"

        # Fallback
        return (
            "Halo, CV Niscahya Indonesia Cerdas adalah perusahaan terkemuka di bidang energi terbarukan, "
            "khususnya penyediaan solusi penerangan jalan berbasis tenaga surya (PJUTS). "
            "Kami berkomitmen memberikan produk berkualitas tinggi dengan layanan profesional."
        )

    @staticmethod
    def build_faq_answer(docs: List[Dict], question: str) -> str:
        """Jawab FAQ dengan matching ke pertanyaan user dan context dari PDF."""
        # Priority 1: uploaded knowledge dari PDF
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('type') == 'uploaded_knowledge']
        if uploaded_docs:
            # Sort by distance untuk relevance terbaik
            uploaded_docs = sorted(uploaded_docs, key=lambda x: x.get('distance', 999))
            content = uploaded_docs[0].get('content', '').strip()
            if content:
                content = " ".join(content.split())  # Clean up whitespace
                # Return dengan closing yang encourage follow-up
                return f"Halo, saya temukan informasi yang relevan di dokumen kami.\n\n{content}\n\n💡 Butuh info lebih detail? Saya bisa bantu jelaskan lagi atau carikan produk yang paling sesuai."
        
        # Priority 2: existing FAQs or fallbacks
        faq_docs = RuleBasedResponseBuilder.filter_docs_by_type(docs, "faq")
        if faq_docs:
            faq_docs_sorted = sorted(faq_docs, key=lambda x: x.get("distance", 999))
            if faq_docs_sorted[0].get("distance", 999) <= RuleBasedResponseBuilder.SIMILARITY_THRESHOLD:
                answer = faq_docs_sorted[0].get("content", "").strip()
                answer = RuleBasedResponseBuilder.extract_faq_answer(answer)
                answer = " ".join(answer.split())
                return f"Halo, berikut jawaban yang saya temukan.\n\n{answer}\n\nAda pertanyaan lain? Saya bisa bantu cari produk atau jelaskan spesifikasinya."

        # Priority 3: try any relevant doc from knowledge base
        relevant_docs = RuleBasedResponseBuilder.filter_relevant_docs(docs)
        if relevant_docs:
            content = relevant_docs[0].get('content', '').strip()
            if content:
                content = " ".join(content.split())
                if len(content) > 400:
                    content = content[:400] + "..."
                return f"Halo, berdasarkan knowledge base kami:\n\n{content}\n\n📞 Kalau perlu, saya bisa bantu arahkan ke produk yang paling cocok."

        # Fallback
            return "Halo, saya ingin mencari informasi yang paling akurat untuk Anda. Silakan hubungi tim support kami di WhatsApp untuk respons cepat dan detail!"

    @staticmethod
    def build_lead_capture(user_input: str) -> str:
        """Respons untuk capture lead - encouraging dan specific."""
        return (
            "Halo, terima kasih atas minat Anda! 🙌\n\n"
            "Kami siap membantu Anda menemukan solusi terbaik. "
            "Silakan share detail berikut:\n"
            "• Nama lengkap Anda\n"
            "• Nomor WhatsApp\n"
            "• Lokasi proyek\n"
            "• Kebutuhan spesifik\n\n"
            "Tim kami akan menghubungi Anda dengan penawaran khusus."
        )

    @staticmethod
    def build_general_response(docs: List[Dict], user_input: str) -> str:
        """Respons umum dengan smart doc selection - prioritize uploaded knowledge."""
        # Jika ada dokumen produk/PDF, pertanyaan umum lebih berguna jika diarahkan ke rekomendasi.
        if any(d.get('metadata', {}).get('type') in {'uploaded_knowledge', 'product'} for d in docs):
            return RuleBasedResponseBuilder.build_product_recommendation(docs, user_input)

        # Priority 1: uploaded knowledge dari PDF
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('type') == 'uploaded_knowledge']
        if uploaded_docs:
            # Filter by relevance dan sort
            relevant_uploaded = RuleBasedResponseBuilder.filter_relevant_docs(uploaded_docs)
            if relevant_uploaded:
                content = relevant_uploaded[0].get('content', '').strip()
                content = " ".join(content.split())
                if len(content) > 500:
                    content = content[:500] + "..."
                return f"Halo, berdasarkan informasi produk kami:\n\n{content}\n\n📞 Hubungi tim kami untuk konsultasi lebih detail dan penawaran khusus!"
            # Jika ada dokumen PDF tetapi tidak relevan dengan pertanyaan user,
            # jawab dengan jelas bahwa topik tidak tersedia di dokumen.
            return (
                f"Di dokumen PDF yang tersedia, saya belum menemukan informasi tentang '{user_input}'. "
                "Saat ini database berisi produk dan spesifikasi PJUTS/lampu jalan tenaga surya. "
                "Jika Anda mau, saya bisa bantu carikan produk PJUTS yang paling mendekati kebutuhan Anda."
            )
        
        # Priority 2: general relevance filtering
        relevant_docs = RuleBasedResponseBuilder.filter_relevant_docs(docs)
        
        if not relevant_docs:
            return (
                "Halo, saya ingin memberikan jawaban yang paling akurat. "
                "Silakan hubungi tim kami di WhatsApp untuk mendapatkan informasi lengkap dan konsultasi gratis!"
            )

        # Sort by type priority: product > faq > company_info
        doc_priority = {"product": 3, "uploaded_knowledge": 3, "faq": 2, "company_info": 1}
        
        best_doc = None
        best_priority = -1
        for doc in relevant_docs:
            doc_type = doc.get("metadata", {}).get("type", "general")
            priority = doc_priority.get(doc_type, 0)
            if priority > best_priority:
                best_priority = priority
                best_doc = doc
        
        if not best_doc:
            best_doc = relevant_docs[0]

        content = best_doc.get("content", "").strip()
        content = " ".join(content.split())
        
        # Truncate jika terlalu panjang
        if len(content) > 450:
            content = content[:450] + "..."
        
        return f"Halo, berikut informasi terkait pertanyaan Anda:\n\n{content}\n\n💡 Ada pertanyaan lebih lanjut? Saya bisa bantu carikan produk yang paling sesuai."

    @staticmethod
    def build_response(intent: str, docs: List[Dict], user_input: str = "") -> str:
        """Build response berdasarkan intent dengan semantic + relevance filtering."""
        if not docs:
            return (
                f"Halo, saya belum menemukan informasi tentang '{user_input}' di dokumen yang aktif. "
                "Silakan tanyakan seputar produk, spesifikasi, harga, garansi, atau pemasangan PJUTS."
            )
        
        # Prioritize uploaded knowledge from PDFs
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('type') == 'uploaded_knowledge']
        if uploaded_docs:
            docs = uploaded_docs
        
        if intent == "product_recommendation":
            return RuleBasedResponseBuilder.build_product_recommendation(docs, user_input)
        elif intent == "company_info":
            return RuleBasedResponseBuilder.build_company_info(docs)
        elif intent == "faq":
            return RuleBasedResponseBuilder.build_faq_answer(docs, user_input)
        elif intent == "lead":
            return RuleBasedResponseBuilder.build_lead_capture(user_input)
        else:
            answer = RuleBasedResponseBuilder.build_general_response(docs, user_input)

        if not answer.lower().startswith("halo,"):
            answer = f"Halo, saya bantu jawab berdasarkan dokumen yang tersedia.\n\n{answer}"

        return answer


response_builder = RuleBasedResponseBuilder()
