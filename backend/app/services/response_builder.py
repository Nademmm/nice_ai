from typing import Dict, List, Optional
import re


class RuleBasedResponseBuilder:
    """Build natural responses from context documents dengan smart semantic matching."""
    
    # Similarity threshold - jangan ambil dokumen yang distance-nya terlalu jauh
    # Chroma distance: 0 = perfect match, 1 = completely irrelevant
    # 0.8 allows docs with distance up to 0.8 (more lenient)
    SIMILARITY_THRESHOLD = 0.8

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
        """Rekomendasi produk dengan smart relevance filtering."""
        # Filter by type dan relevance
        products = RuleBasedResponseBuilder.filter_docs_by_type(docs, "product")
        products = RuleBasedResponseBuilder.filter_relevant_docs(products)
        
        if not products:
            return (
                "Maaf, saya tidak menemukan rekomendasi produk yang cocok untuk kebutuhan Anda. "
                "Bisa Anda detail lebih lanjut tentang kebutuhan area, ukuran, atau penggunaan? "
                "Hubungi tim kami di WhatsApp untuk konsultasi gratis dan penawaran terbaik."
            )

        response = "✨ Berdasarkan kebutuhan Anda, berikut rekomendasi PJUTS yang paling sesuai:\n"
        
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
            return content

        # Fallback
        return (
            "CV Niscahya Indonesia Cerdas adalah perusahaan terkemuka di bidang energi terbarukan, "
            "khususnya penyediaan solusi penerangan jalan berbasis tenaga surya (PJUTS). "
            "Kami berkomitmen memberikan produk berkualitas tinggi dengan layanan profesional."
        )

    @staticmethod
    def build_faq_answer(docs: List[Dict], question: str) -> str:
        """Jawab FAQ dengan exact matching ke pertanyaan user."""
        # Cari FAQ yang paling match
        matching_faq = RuleBasedResponseBuilder.find_matching_faq(docs, question)
        
        if matching_faq:
            answer = matching_faq.get("content", "").strip()
            answer = RuleBasedResponseBuilder.extract_faq_answer(answer)
            answer = " ".join(answer.split())
            # Add a friendly closing untuk FAQ answers
            return f"{answer}\n\nAda pertanyaan lain? Hubungi tim kami untuk info lebih detail!"

        # Fallback ke product docs jika ada
        products = RuleBasedResponseBuilder.filter_docs_by_type(docs, "product")
        if products:
            content = products[0].get("content", "").strip()
            content = " ".join(content.split())
            if len(content) > 300:
                content = content[:300] + "..."
            return f"Berdasarkan knowledge base kami, berikut informasi relevan:\n\n{content}\n\nUntuk jawaban yang lebih spesifik, silakan hubungi tim support kami."

        return "Pertanyaan bagus! Saya belum menemukan jawaban pasti untuk ini. Hubungi tim kami di WhatsApp untuk respons cepat dan akurat!"

    @staticmethod
    def build_lead_capture(user_input: str) -> str:
        """Respons untuk capture lead - encouraging dan specific."""
        return (
            "Terima kasih atas minat Anda! 🙌\n\n"
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
        """Respons umum dengan smart doc selection."""
        # Filter by relevance threshold dulu
        relevant_docs = RuleBasedResponseBuilder.filter_relevant_docs(docs)
        
        if not relevant_docs:
            return (
                "Terima kasih atas pertanyaannya! Topik Anda sangat menarik, tetapi saya belum menemukan informasi yang cukup relevan di knowledge base. "
                "Tim kami siap membantu dengan jawaban lengkap. Hubungi kami di WhatsApp untuk respons cepat dan detail!"
            )

        # Priority: product > faq > company_info
        doc_priority = {"product": 3, "faq": 2, "company_info": 1}
        
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
        if len(content) > 350:
            content = content[:350] + "..."
        
        return f"Berikut informasi terkait pertanyaan Anda:\n\n{content}\n\nAda yang lain?"

    @staticmethod
    def build_response(intent: str, docs: List[Dict], user_input: str = "") -> str:
        """Build response berdasarkan intent dengan semantic + relevance filtering."""
        if not docs:
            return (
                "Maaf, saat ini saya tidak menemukan informasi yang relevan. "
                "Silakan hubungi tim kami untuk bantuan lebih lanjut."
            )
        
        if intent == "product_recommendation":
            return RuleBasedResponseBuilder.build_product_recommendation(docs, user_input)
        elif intent == "company_info":
            return RuleBasedResponseBuilder.build_company_info(docs)
        elif intent == "faq":
            return RuleBasedResponseBuilder.build_faq_answer(docs, user_input)
        elif intent == "lead":
            return RuleBasedResponseBuilder.build_lead_capture(user_input)
        else:
            return RuleBasedResponseBuilder.build_general_response(docs, user_input)


response_builder = RuleBasedResponseBuilder()
