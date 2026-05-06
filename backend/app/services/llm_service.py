import google.generativeai as genai
from app.core.config import settings
from typing import Optional, Dict, List
from app.services.response_builder import response_builder


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.use_ai_model = False
        
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.use_ai_model = True
        elif settings.OPENAI_API_KEY:
            self.use_ai_model = True

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        intent: str = "general",
        context_docs: Optional[List[Dict]] = None,
        user_input: str = ""
    ) -> str:
        # PRIORITAS UTAMA: Selalu gunakan knowledge base dari PDF/uploaded documents
        # Hanya gunakan AI model jika ada context yang cukup dari knowledge base
        if context_docs and len(context_docs) > 0:
            # Cek apakah ada uploaded knowledge dari PDF
            has_uploaded_knowledge = any(d.get('metadata', {}).get('source') == 'uploaded_knowledge' for d in context_docs)
            
            # Jika ada PDF atau context docs yang relevan, gunakan rule-based response builder
            # Ini memastikan jawaban HANYA dari knowledge base, bukan dari LLM general knowledge
            return self._generate_rule_based_response(intent, context_docs, user_input)
        
        # Jika tidak ada context docs, gunakan rule-based dengan empty docs
        return self._generate_rule_based_response(intent, context_docs or [], user_input)

    async def _generate_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def _generate_openai(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _generate_rule_based_response(self, intent: str, docs: List[Dict], user_input: str) -> str:
        """Generate response using rule-based templates dan konteks dari vector store."""
        return response_builder.build_response(intent, docs, user_input)


llm_service = LLMService()
