from typing import Dict, List, Optional
import re


class RuleBasedResponseBuilder:
    """Build natural responses from context documents dengan smart semantic matching."""
    
    SIMILARITY_THRESHOLD = 1.5

    @staticmethod
    def filter_docs_by_type(docs: List[Dict], doc_type: str) -> List[Dict]:
        return [d for d in docs if d.get("metadata", {}).get("type") == doc_type]

    @staticmethod
    def filter_relevant_docs(docs: List[Dict], threshold: float = SIMILARITY_THRESHOLD) -> List[Dict]:
        filtered = []

        for d in docs:
            if "distance" not in d:
                filtered.append(d)
                continue

            if d.get("distance", 999) <= threshold:
                filtered.append(d)

        return filtered

    @staticmethod
    def extract_faq_answer(content: str) -> str:
        if "Jawaban:" in content:
            return content.split("Jawaban:")[-1].strip()

        return content.strip()

    @staticmethod
    def extract_company_details(content: str) -> str:
        """Extract informasi penting perusahaan dari PDF."""

        lines = [line.strip() for line in content.splitlines() if line.strip()]

        keywords = [
            'alamat',
            'lokasi',
            'kantor',
            'jam operasional',
            'jam kerja',
            'telepon',
            'whatsapp',
            'email',
            'website',
            'tentang perusahaan',
            'visi',
            'misi'
        ]

        important_lines = []

        for line in lines:
            lower = line.lower()

            if any(keyword in lower for keyword in keywords):
                important_lines.append(line)

        if important_lines:
            return '\n'.join(important_lines[:15])

        cleaned = " ".join(content.split())

        if len(cleaned) > 500:
            cleaned = cleaned[:500] + "..."

        return cleaned

    @staticmethod
    def extract_product_summary(content: str) -> str:
        """Extract hanya nama, jenis, dan spesifikasi dari product content."""

        lines = content.split('\n')
        summary_lines = []
        include_line = False

        for line in lines:
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in [
                'nama',
                'jenis',
                'spesifikasi',
                'tipe',
                'model'
            ]):
                summary_lines.append(line)
                include_line = True

            elif include_line and (
                line.startswith('•') or
                line.startswith('-') or
                line.startswith('*')
            ):
                summary_lines.append(line)

            elif line.strip().startswith((
                'deskripsi',
                'keterangan',
                'harga',
                'garansi'
            )):

                break

            elif include_line and not line.strip():

                if any(keyword in ''.join(summary_lines).lower()
                       for keyword in ['nama', 'jenis', 'spesifikasi']):
                    break

        summary = '\n'.join(summary_lines[:10]).strip()

        if not summary or len(summary) < 30:
            summary = ' '.join(content.split())[:300]

        return summary

    @staticmethod
    def find_matching_faq(docs: List[Dict], question: str) -> Optional[Dict]:

        faq_docs = RuleBasedResponseBuilder.filter_docs_by_type(
            docs,
            "faq"
        )

        if not faq_docs:
            return None

        faq_docs_sorted = sorted(
            faq_docs,
            key=lambda x: x.get("distance", 999)
        )

        if (
            faq_docs_sorted and
            faq_docs_sorted[0].get("distance", 999)
            <= RuleBasedResponseBuilder.SIMILARITY_THRESHOLD
        ):
            return faq_docs_sorted[0]

        return None

    @staticmethod
    def build_product_recommendation(
        docs: List[Dict],
        user_input: str,
        detailed: bool = False
    ) -> str:

        uploaded_docs = [
            d for d in docs
            if d.get('metadata', {}).get('type') == 'uploaded_knowledge'
        ]

        if uploaded_docs:

            relevant_uploaded = RuleBasedResponseBuilder.filter_relevant_docs(
                uploaded_docs
            )

            if relevant_uploaded:

                if detailed:
                    response = (
                        "Halo 👋\n\n"
                        "Berikut detail lengkap produk yang Anda tanyakan:\n"
                    )
                else:
                    response = (
                        "Halo 👋\n\n"
                        "Saya bantu rekomendasikan produk terbaik "
                        "berdasarkan kebutuhan Anda.\n\n"
                        "✨ Berikut rekomendasi produk:"
                    )

                for i, doc in enumerate(relevant_uploaded[:3], 1):

                    content = doc.get("content", "").strip()

                    if not detailed:
                        content = RuleBasedResponseBuilder.extract_product_summary(
                            content
                        )

                    response += f"\n\n{i}. {content}"

                if detailed:
                    response += (
                        "\n\n---\n\n"
                        "💡 Jika ingin rekomendasi lain, silakan tanyakan lagi ya."
                    )
                else:
                    response += (
                        "\n\n---\n\n"
                        "Ketik 'detail' untuk melihat penjelasan lengkap produk."
                    )

                return response

        return (
            "Halo 👋\n\n"
            "Saya belum menemukan rekomendasi produk yang sesuai "
            "di dokumen aktif."
        )

    @staticmethod
    def build_company_info(docs: List[Dict]) -> str:
        """Info perusahaan dari CV NICE INDONESIA.pdf atau fallback company_info."""

        # Prioritas 1: Dokumen dari CV NICE INDONESIA.pdf
        cv_nice_docs = [
            d for d in docs
            if 'cv nice' in d.get('metadata', {}).get('source', '').lower()
            or 'nice indonesia' in d.get('metadata', {}).get('source', '').lower()
        ]

        # Prioritas 2: company_info type (fallback hardcoded)
        company_info_docs = [
            d for d in docs
            if d.get('metadata', {}).get('type') == 'company_info'
        ]

        # Prioritas 3: uploaded_knowledge with company_profile category
        company_profile_docs = [
            d for d in docs
            if d.get('metadata', {}).get('category') == 'company_profile'
        ]

        # Gabungkan semua sumber, prioritaskan CV NICE
        all_company_docs = cv_nice_docs + company_profile_docs + company_info_docs

        if not all_company_docs:
            # Fallback: cari dari semua uploaded docs
            all_company_docs = [
                d for d in docs
                if d.get('metadata', {}).get('type') in ('uploaded_knowledge', 'company_info')
            ]

        all_company_docs = sorted(
            all_company_docs,
            key=lambda x: x.get("distance", 999)
        )

        if all_company_docs:
            # Gabungkan konten dari semua dokumen perusahaan
            combined_content = []
            for doc in all_company_docs[:3]:
                content = doc.get("content", "").strip()
                if content and len(content) > 10:
                    combined_content.append(content)

            if combined_content:
                details = RuleBasedResponseBuilder.extract_company_details(
                    '\n'.join(combined_content)
                )

                return (
                    "Halo 👋\n\n"
                    "Saya NICE Chatbot dari CV Niscahya Indonesia Cerdas.\n"
                    "Saya siap membantu Anda terkait informasi perusahaan "
                    "maupun produk PJUTS.\n\n"
                    "📌 Berikut informasi perusahaan yang saya temukan:\n\n"
                    f"{details}\n\n"
                    "💡 Jika Anda membutuhkan informasi lainnya, "
                    "silakan tanyakan saja ya."
                )

        return (
            "Halo 👋\n\n"
            "Saya NICE Chatbot dari CV Niscahya Indonesia Cerdas.\n\n"
            "Saat ini saya belum menemukan data perusahaan "
            "di dokumen yang tersedia."
        )

    @staticmethod
    def build_faq_answer(docs: List[Dict], question: str) -> str:

        uploaded_docs = [
            d for d in docs
            if d.get('metadata', {}).get('type') == 'uploaded_knowledge'
        ]

        if uploaded_docs:

            uploaded_docs = sorted(
                uploaded_docs,
                key=lambda x: x.get('distance', 999)
            )

            content = uploaded_docs[0].get('content', '').strip()

            if content:

                content = " ".join(content.split())

                return (
                    "Halo 👋\n\n"
                    "Saya menemukan informasi berikut:\n\n"
                    f"{content}\n\n"
                    "---\n\n"
                    "💡 Jika masih ada yang ingin ditanyakan, "
                    "silakan tanyakan lagi ya."
                )

        return (
            "Halo 👋\n\n"
            "Maaf, saya belum menemukan jawaban yang sesuai."
        )

    @staticmethod
    def build_lead_capture(user_input: str) -> str:

        return (
            "Halo 👋\n\n"
            "Terima kasih atas minat Anda.\n\n"
            "Silakan kirim:\n"
            "• Nama\n"
            "• Nomor WhatsApp\n"
            "• Lokasi proyek\n"
            "• Kebutuhan produk\n\n"
            "📞 Tim kami akan segera membantu Anda."
        )

    @staticmethod
    def build_general_response(
        docs: List[Dict],
        user_input: str,
        detailed: bool = False
    ) -> str:

        if any(
            d.get('metadata', {}).get('type')
            in {'uploaded_knowledge', 'product'}
            for d in docs
        ):
            return RuleBasedResponseBuilder.build_product_recommendation(
                docs,
                user_input,
                detailed=detailed
            )

        return (
            "Halo 👋\n\n"
            "Silakan tanyakan informasi terkait produk "
            "atau perusahaan kami."
        )

    @staticmethod
    def build_response(
        intent: str,
        docs: List[Dict],
        user_input: str = ""
    ) -> str:

        user_text = user_input.lower().strip()

        # =========================
        # GREETING RESPONSE
        # =========================
        greetings = [
            "halo",
            "hai",
            "hi",
            "hello",
            "p",
            "assalamualaikum"
        ]

        if user_text in greetings:

            return (
                "Halo 👋\n\n"
                "Saya NICE Chatbot dari CV Niscahya Indonesia Cerdas.\n\n"
                "Saya siap membantu Anda terkait:\n"
                "• Informasi perusahaan\n"
                "• Produk PJUTS\n"
                "• Spesifikasi produk\n"
                "• Rekomendasi lampu tenaga surya\n"
                "• Harga dan konsultasi produk\n\n"
                "💬 Silakan tanyakan apa yang ingin Anda ketahui."
            )

        if not docs:

            return (
                f"Halo, saya belum menemukan informasi tentang "
                f"'{user_input}' di dokumen yang aktif."
            )

        # =========================
        # DETAIL KEYWORDS
        # =========================
        detail_keywords = [
            'detail',
            'lebih lanjut',
            'deskripsi',
            'spesifikasi lengkap',
            'penjelasan',
            'jelaskan',
            'info lengkap',
            'selengkapnya',
            'keterangan'
        ]

        detailed = any(
            keyword in user_text
            for keyword in detail_keywords
        )

        # =========================
        # PRODUCT BRAND KEYWORDS (lampu [merk])
        # =========================
        product_brand_keywords = [
            'lampu all in one', 'lampu aio', 'lampu king light',
            'lampu crossbow', 'lampu pjuts', 'lampu pju',
            'lampu solar', 'lampu tenaga surya',
            'lampu nc-pt', 'lampu nc-st', 'lampu nc-p',
            'lampu gw8860', 'lampu hf-rl', 'lampu by7',
            'lampu bct', 'lampu sdlb', 'lampu wl-302',
            'lampu sorot', 'lampu jalan', 'lampu taman',
        ]

        if any(keyword in user_text for keyword in product_brand_keywords):
            intent = "product_recommendation"

        # Detect generic "lampu [kata lain]" pattern
        if 'lampu ' in user_text and intent not in ('company_info',):
            after_lampu = user_text.split('lampu', 1)[-1].strip()
            if after_lampu and len(after_lampu) > 2:
                intent = "product_recommendation"

        # =========================
        # COMPANY KEYWORDS
        # =========================
        company_keywords = [
            'perusahaan',
            'company',
            'profil perusahaan',
            'tentang perusahaan',
            'profil',
            'alamat',
            'lokasi',
            'kantor',
            'office',
            'jam kerja',
            'jam operasional',
            'kontak',
            'whatsapp',
            'email',
            'tentang nice',
            'tentang niscahya',
            'cv nice',
            'niscahya'
        ]

        if any(keyword in user_text for keyword in company_keywords):
            intent = "company_info"

        uploaded_docs = [
            d for d in docs
            if d.get('metadata', {}).get('type') in ('uploaded_knowledge', 'company_info')
        ]

        if uploaded_docs:
            docs = uploaded_docs

        if intent == "product_recommendation":

            return RuleBasedResponseBuilder.build_product_recommendation(
                docs,
                user_input,
                detailed=detailed
            )

        elif intent == "company_info":

            return RuleBasedResponseBuilder.build_company_info(docs)

        elif intent == "faq":

            return RuleBasedResponseBuilder.build_faq_answer(
                docs,
                user_input
            )

        elif intent == "lead":

            return RuleBasedResponseBuilder.build_lead_capture(
                user_input
            )

        else:

            answer = RuleBasedResponseBuilder.build_general_response(
                docs,
                user_input,
                detailed=detailed
            )

        if not answer.lower().startswith("halo"):

            answer = (
                "Halo 👋\n\n"
                f"{answer}"
            )

        return answer


response_builder = RuleBasedResponseBuilder()