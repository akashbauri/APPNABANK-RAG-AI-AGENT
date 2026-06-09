from langdetect import detect
from app.rag.chromadb_client import chroma_manager
from app.services.tavily_service import tavily_service
from app.services.gemini_service import gemini_service
from typing import Dict, Any

class HybridRAGPipeline:
    def __init__(self):
        self.collections = ["banking_knowledge", "stock_market_english", "stock_market_hindi"]

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            if lang in ['hi', 'bn']:
                return lang
            return 'en'
        except Exception:
            return 'en'

    def process_query(self, question: str, profile_data: Dict[str, Any] = None) -> Dict[str, Any]:
        detected_lang = self.detect_language(question)
        
        # Human readable language names for prompt anchoring
        lang_mapping = {"en": "English", "hi": "Hindi", "bn": "Bengali"}
        target_lang_name = lang_mapping.get(detected_lang, "English")

        best_context = ""
        best_source_name = "None"
        best_source_type = "fallback"
        highest_confidence = -1.0 # Cosine similarity threshold marker

        # Search across vector databases
        for col_name in self.collections:
            res = chroma_manager.query_collection(col_name, question, n_results=2)
            if res and res['documents'] and res['documents'][0]:
                # Chroma DB default cosine distance is returned (0 means identical, 1 means completely orthogonal)
                # Calculate simple matching metric: similarity = 1 - distance
                distance = res['distances'][0][0] if 'distances' in res and res['distances'] else 0.5
                similarity = 1.0 - distance

                if similarity > highest_confidence:
                    highest_confidence = similarity
                    best_context = "\n".join(res['documents'][0])
                    # Extract source metadata if present
                    if res['metadatas'] and res['metadatas'][0] and 'source' in res['metadatas'][0][0]:
                        best_source_name = res['metadatas'][0][0]['source']
                    else:
                        best_source_name = col_name
                    best_source_type = "pdf"

        # Hybrid fallback verification: Confidence evaluation boundary (Similarity threshold 0.35)
        if highest_confidence < 0.35:
            # Fall back to Tavily Web Search
            best_context = tavily_service.search(question)
            best_source_type = "tavily"
            best_source_name = "Tavily Financial Live Search Index"

        # Compile optional personalization parameters
        personalization = ""
        if profile_data:
            personalization = f"Age: {profile_data.get('age')}, Monthly Income: ₹{profile_data.get('monthly_income')}, Financial Goal: {profile_data.get('goal')}"

        # Generate response using Gemini
        answer = gemini_service.generate_response(
            question=question, 
            context=best_context, 
            language=target_lang_name, 
            personalization=personalization
        )

        return {
            "answer": answer,
            "source_type": best_source_type,
            "source_name": best_source_name,
            "detected_language": detected_lang
        }

rag_pipeline = HybridRAGPipeline()
