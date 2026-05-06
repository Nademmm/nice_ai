from typing import Dict, List, Optional
import re


class RuleBasedResponseBuilder:
    """Build natural responses from context documents dengan smart semantic matching."""
    
    # Similarity threshold - jangan ambil dokumen yang distance-nya terlalu jauh
    # Chroma distance: 0 = perfect match, 2 = completely irrelevant
    # Untuk PDF-based RAG: 1.5 (lebih lenient untuk menangkap dokumen PDF yang relevan)
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
    def extract_product_specs(product_doc: Dict) -> Dict:
        """Extract product specifications dari document untuk matching."""
        content = product_doc.get("content", "").lower()
        specs = {
            "original_content": product_doc.get("content", ""),
            "watt": 0,  # Default to 0 instead of None
            "battery": 0,  # Default to 0 instead of None
            "pole_height": None,
            "suitable_for": [],
            "lighting_duration": None,
            "coverage_area": None,
            "distance": product_doc.get("distance", 999) or 999  # Handle None
        }
        
        # Extract watt
        import re
        watt_match = re.search(r'(\d+)\s*w(?:att)?', content)
        if watt_match:
            try:
                specs["watt"] = int(watt_match.group(1))
            except (ValueError, IndexError):
                specs["watt"] = 0
        
        # Extract battery capacity
        battery_match = re.search(r'(\d+)\s*ah', content)
        if battery_match:
            try:
                specs["battery"] = int(battery_match.group(1))
            except (ValueError, IndexError):
                specs["battery"] = 0
        
        # Extract suitable_for keywords
        for_keywords = ["taman", "perumahan", "jalan", "area", "industri", "parkiran", "persawahan", 
                        "protokol", "freeway", "komersial", "residential", "lingkungan"]
        for keyword in for_keywords:
            if keyword in content:
                specs["suitable_for"].append(keyword)
        
        # Extract lighting duration
        duration_match = re.search(r'(\d+)[- ]?(\d+)\s*jam', content)
        if duration_match:
            specs["lighting_duration"] = f"{duration_match.group(1)}-{duration_match.group(2)} jam"
        
        return specs

    @staticmethod
    def extract_user_needs(user_input: str) -> Dict:
        """Extract kebutuhan user dari query untuk matching dengan produk."""
        user_input_lower = user_input.lower()
        needs = {
            "location_type": [],
            "scale": None,
            "keywords": user_input_lower
        }
        
        # Detect location types
        location_map = {
            "taman": ["taman", "garden"],
            "jalan": ["jalan", "street", "road"],
            "perumahan": ["perumahan", "residential", "kompleks"],
            "industri": ["industri", "pabrik", "factory"],
            "parkiran": ["parkiran", "parking"],
            "persawahan": ["sawah", "persawahan"],
            "komersial": ["komersial", "mall", "bisnis"],
            "area besar": ["besar", "luas", "banyak"],
            "area sempit": ["sempit", "kecil"],
        }
        
        for location, keywords_list in location_map.items():
            for keyword in keywords_list:
                if keyword in user_input_lower:
                    needs["location_type"].append(location)
        
        # Detect scale
        if any(word in user_input_lower for word in ["besar", "luas", "banyak", "main", "utama", "major", "100", "120"]):
            needs["scale"] = "large"
        elif any(word in user_input_lower for word in ["sempit", "kecil", "taman", "gang", "40", "60"]):
            needs["scale"] = "small"
        elif any(word in user_input_lower for word in ["sedang", "medium", "residential", "lingkungan", "80"]):
            needs["scale"] = "medium"
        
        return needs

    @staticmethod
    def calculate_product_match_score(product_specs: Dict, user_needs: Dict) -> float:
        """Calculate relevance score untuk product recommendation (0-100)."""
        score = 0
        max_score = 100
        
        # 1. Distance score (lebih kecil = lebih relevan)
        distance = product_specs.get("distance", 999) or 999  # Handle None
        if distance <= 0.5:
            score += 40
        elif distance <= 1.0:
            score += 30
        elif distance <= 1.5:
            score += 20
        else:
            score += 5
        
        # 2. Scale matching (30 points)
        user_scale = user_needs.get("scale")
        watt = product_specs.get("watt") or 0  # Handle None properly
        
        if user_scale == "large" and watt >= 80:
            score += 30
        elif user_scale == "medium" and 60 <= watt <= 80:
            score += 30
        elif user_scale == "small" and watt <= 60:
            score += 30
        elif watt > 0:
            score += 15  # Partial match
        
        # 3. Location type matching (30 points)
        user_locations = user_needs.get("location_type", [])
        product_suitable = product_specs.get("suitable_for", [])
        
        if user_locations and product_suitable:
            # Check for overlap
            overlap = len(set(user_locations) & set(product_suitable))
            if overlap > 0:
                score += 30
            else:
                score += 10  # Partial match
        elif product_suitable:
            score += 15  # Product has suitable_for info
        
        return min(score, max_score)

    @staticmethod
    def build_product_recommendation(docs: List[Dict], user_input: str) -> str:
        """Rekomendasi produk dengan intelligent matching berdasarkan kebutuhan user."""
        # Filter by type dan relevance
        products = RuleBasedResponseBuilder.filter_docs_by_type(docs, "product")
        products = RuleBasedResponseBuilder.filter_relevant_docs(products)

        if not products:
            return (
                "🙁 Maaf, saya tidak menemukan rekomendasi produk yang cocok untuk kebutuhan Anda.\n\n"
                "💡 Bisa Anda detail lebih lanjut tentang:\n"
                "• Area/lokasi penggunaan\n"
                "• Ukuran area (kecil/sedang/besar)\n"
                "• Kebutuhan spesifik lainnya\n\n"
                "📞 Hubungi tim kami di WhatsApp untuk konsultasi gratis dan penawaran terbaik."
            )

        # Extract user needs
        user_needs = RuleBasedResponseBuilder.extract_user_needs(user_input)

        # Score dan rank products
        scored_products = []
        for product in products:
            try:
                specs = RuleBasedResponseBuilder.extract_product_specs(product)
                match_score = RuleBasedResponseBuilder.calculate_product_match_score(specs, user_needs)
                scored_products.append({
                    "specs": specs,
                    "score": match_score,
                    "original_content": product.get("content", "")
                })
            except Exception as e:
                # Skip products that cause errors
                print(f"Warning: Error processing product: {e}")
                continue

        if not scored_products:
            return (
                "🙁 Maaf, terjadi kesalahan saat memproses rekomendasi produk.\n\n"
                "📞 Silakan hubungi tim kami di WhatsApp untuk bantuan langsung."
            )

        # Sort by score (highest first)
        scored_products.sort(key=lambda x: x["score"], reverse=True)

        # Build response dengan top recommendations - LEBIH RAPI
        response = "✨ **Rekomendasi PJUTS untuk Kebutuhan Anda**\n\n"

        for i, item in enumerate(scored_products[:2], 1):  # Max 2 produk
            specs = item["specs"]
            score = item["score"]

            # Header untuk setiap produk
            watt = specs.get('watt', 0)
            watt_str = f"{watt}W" if watt > 0 else "Spesifikasi Lengkap"
            response += f"🏆 **Rekomendasi #{i}: PJUTS {watt_str}**\n"
            response += f"🎯 *Match Score: {score:.0f}%*\n\n"

            # Spesifikasi dalam bullet points
            response += "📋 **Spesifikasi Produk:**\n"

            if watt > 0:
                response += f"• ⚡ Daya: {watt} Watt\n"

            battery = specs.get('battery', 0)
            if battery > 0:
                response += f"• 🔋 Baterai: {battery} Ah LiFePO4\n"

            suitable_for = specs.get("suitable_for", [])
            if suitable_for:
                response += f"• 📍 Cocok untuk: {', '.join(suitable_for[:3])}\n"

            lighting_duration = specs.get("lighting_duration")
            if lighting_duration:
                response += f"• 💡 Durasi Penerangan: {lighting_duration}\n"

            # Alasan rekomendasi
            reasons = []
            if suitable_for:
                reasons.append(f"cocok untuk area {', '.join(suitable_for[:2])}")
            if watt > 0:
                user_scale = user_needs.get("scale")
                if user_scale == "large":
                    reasons.append("power tinggi untuk area luas")
                elif user_scale == "small":
                    reasons.append("efisien untuk area terbatas")

            if reasons:
                response += f"\n💡 **Mengapa cocok:** {', '.join(reasons)}\n"

            # Separator antara produk
            if i < len(scored_products[:2]):
                response += "\n" + "─" * 50 + "\n\n"

        # Footer dengan call-to-action
        response += "\n" + "═" * 50 + "\n"
        response += "📞 **Hubungi Kami untuk Detail Lebih Lanjut**\n"
        response += "• Diskusi spesifikasi lengkap\n"
        response += "• Penawaran harga khusus\n"
        response += "• Jadwal pemasangan\n"
        response += "• Garansi & maintenance\n\n"
        response += "💬 WhatsApp: [Nomor WhatsApp Anda]"

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

            # Format company info lebih rapi
            response = "🏢 **Tentang CV Niscahya Indonesia Cerdas**\n\n"
            response += f"{content}\n\n"
            response += "📞 **Kontak Kami:**\n"
            response += "• WhatsApp: [Nomor WhatsApp]\n"
            response += "• Email: [Email Perusahaan]\n"
            response += "• Alamat: [Alamat Kantor]"

            return response

        # Fallback
        return (
            "🏢 **CV Niscahya Indonesia Cerdas**\n\n"
            "Kami adalah perusahaan terkemuka di bidang energi terbarukan, "
            "khususnya penyediaan solusi penerangan jalan berbasis tenaga surya (PJUTS).\n\n"
            "✨ **Komitmen Kami:**\n"
            "• Produk berkualitas tinggi\n"
            "• Layanan profesional\n"
            "• Solusi energi hijau\n\n"
            "📞 **Hubungi Kami**\n"
            "Untuk informasi lebih detail tentang perusahaan kami."
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

            # Format FAQ response lebih rapi
            response = "💡 **Jawaban FAQ**\n\n"
            response += f"{answer}\n\n"
            response += "❓ **Ada pertanyaan lain?**\n"
            response += "Hubungi tim kami untuk info lebih detail!"

            return response

        # Fallback ke product docs jika ada
        products = RuleBasedResponseBuilder.filter_docs_by_type(docs, "product")
        if products:
            content = products[0].get("content", "").strip()
            content = " ".join(content.split())
            if len(content) > 300:
                content = content[:300] + "..."

            response = "📚 **Informasi dari Knowledge Base**\n\n"
            response += f"{content}\n\n"
            response += "💡 **Untuk jawaban yang lebih spesifik:**\n"
            response += "Silakan hubungi tim support kami."

            return response

        return (
            "🤔 **Pertanyaan Bagus!**\n\n"
            "Saya belum menemukan jawaban pasti untuk ini.\n\n"
            "📞 **Hubungi tim kami di WhatsApp**\n"
            "Untuk respons cepat dan akurat!"
        )

    @staticmethod
    def build_lead_capture(user_input: str) -> str:
        """Respons untuk capture lead - encouraging dan specific."""
        response = "🙌 **Terima kasih atas minat Anda!**\n\n"
        response += "Kami siap membantu Anda menemukan solusi terbaik untuk kebutuhan penerangan Anda.\n\n"
        response += "📝 **Silakan share detail berikut:**\n"
        response += "• 👤 Nama lengkap Anda\n"
        response += "• 📱 Nomor WhatsApp\n"
        response += "• 📍 Lokasi proyek\n"
        response += "• 💡 Kebutuhan spesifik\n\n"
        response += "🎯 **Tim kami akan menghubungi Anda**\n"
        response += "Dengan penawaran khusus dan solusi terbaik!"

        return response

    @staticmethod
    def build_general_response(docs: List[Dict], user_input: str) -> str:
        """Respons umum dengan smart doc selection dan formatting."""
        # Filter by relevance threshold dulu
        relevant_docs = RuleBasedResponseBuilder.filter_relevant_docs(docs)

        if not relevant_docs:
            return (
                "🙏 **Terima kasih atas pertanyaannya!**\n\n"
                "Topik Anda sangat menarik, tetapi saya belum menemukan informasi yang cukup relevan di knowledge base.\n\n"
                "📞 **Tim kami siap membantu**\n"
                "Dengan jawaban lengkap. Hubungi kami di WhatsApp untuk respons cepat dan detail!"
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

        doc_type = best_doc.get("metadata", {}).get("type", "general")
        content = best_doc.get("content", "").strip()

        # Clean content - remove excessive whitespace
        content = " ".join(content.split())

        # For FAQ content, extract only the answer part
        if "Jawaban:" in content:
            content = content.split("Jawaban:")[-1].strip()

        # For product content, extract key info
        if "Produk:" in content and doc_type == "product":
            lines = content.split("\n")[:3]  # Take first 3 lines only
            content = " ".join(lines)

        # Truncate jika terlalu panjang
        if len(content) > 300:
            content = content[:300] + "..."

        # Format general response lebih rapi
        response = "📚 **Informasi Terkait**\n\n"
        response += f"*{user_input}*\n\n"
        response += f"{content}\n\n"
        response += "💡 **Butuh info lebih detail?**\n"
        response += "Hubungi tim kami!"

        return response

    @staticmethod
    def build_clarification_response(user_input: str) -> str:
        """Respons untuk query yang terlalu pendek atau ambigu."""
        return (
            f"Halo! Boleh saya tahu lebih detail tentang '{user_input}' yang "
            "Anda maksud? Misalnya jenis, ukuran, atau kebutuhan proyeknya? 😊"
        )

    @staticmethod
    def build_response(intent: str, docs: List[Dict], user_input: str = "") -> str:
        """Build response berdasarkan intent dengan semantic + relevance filtering.
        
        PENTING: Sistem ini dirancang untuk HANYA memberikan jawaban berdasarkan data dari PDF/knowledge base.
        Tidak akan memberikan jawaban umum atau dari LLM knowledge yang tidak ada di database.
        PRIORITAS: Uploaded knowledge dari PDF HARUS digunakan jika ada dan relevan.
        """
        if not docs:
            return (
                "Maaf, saat ini saya tidak menemukan informasi yang relevan di knowledge base kami. "
                "Silakan hubungi tim support kami di WhatsApp untuk jawaban yang akurat."
            )
        
        # STRICT MODE: Prioritize uploaded knowledge from PDFs - ONLY use these if available and relevant to intent
        uploaded_docs = [d for d in docs if d.get('metadata', {}).get('source') == 'uploaded_knowledge']
        
        # Filter uploaded docs by relevance threshold - MORE LENIENT
        relevant_uploaded_docs = RuleBasedResponseBuilder.filter_relevant_docs(uploaded_docs, threshold=1.5)
        
        # Check if relevant uploaded docs match the intent type
        intent_types = {
            "company_info": ["company_info"],
            "product_recommendation": ["product"],
            "faq": ["faq"],
            "lead": ["product", "company_info"],
            "general": ["product", "company_info", "faq"]
        }
        target_types = intent_types.get(intent, [])
        
        # Jika ada uploaded docs yang relevan, gunakan HANYA itu untuk respons
        if relevant_uploaded_docs:
            # Uploaded knowledge ditemukan - gunakan untuk respons
            docs = relevant_uploaded_docs
        else:
            # Tidak ada uploaded knowledge yang relevan - gunakan default knowledge
            # Filter semua docs by relevance
            all_relevant = RuleBasedResponseBuilder.filter_relevant_docs(docs, threshold=1.5)
            if all_relevant:
                docs = all_relevant
        
        # Check for short/ambiguous queries
        if len(user_input.split()) < 3:
            all_relevant = RuleBasedResponseBuilder.filter_relevant_docs(docs)
            if not all_relevant:
                return RuleBasedResponseBuilder.build_clarification_response(user_input)
        
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
