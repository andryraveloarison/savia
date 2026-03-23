import logging
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult
from app.domain.services.qualification_service import QualificationService
from app.domain.services.orientation_service import OrientationService
from app.infrastructure.ai.base import AIClient
from app.core.config import get_settings

logger = logging.getLogger("savia")
settings = get_settings()

class AIAnalysisService:
    @staticmethod
    async def run(ticket: TicketEntity, ai_client: AIClient, completeness: dict) -> dict:
        """
        Orchestre l'analyse IA avec fallback déterministe.
        """
        use_fallback = False
        ai_result: AIAnalysisResult | None = None
        
        # 1. Tentative d'analyse IA
        if settings.ai_enabled:
            
            try:
                ai_result = await ai_client.analyze_ticket(ticket)
                # Vérification du seuil de confiance    
                if ai_result.confidence_score < settings.confidence_threshold_ai:
                    logger.warning(f"AI confidence too low ({ai_result.confidence_score}), triggering fallback.")
                    use_fallback = True
            except Exception as e:
                logger.error(f"AI Analysis failed, falling back to rules engine: {e}")
                use_fallback = True
        else:
            use_fallback = True

        # 2. Fallback déterministe (Moteur de règles)
        if use_fallback:
            qualification = QualificationService.run(ticket)
            orientation = OrientationService.run(
                ticket,
                qualification,
                completeness
            )
            
            return {
                "category": qualification["category"],
                "urgency": qualification["urgency"],
                "action": orientation["action"],
                "confidence_score": orientation["confidence_score"],
                "justifications": ["Fallback: Deterministic rules engine applied"],
                "provider": "rules_engine"
            }

        # 3. Résultat IA validé
        return {
            "category": ai_result.category,
            "urgency": ai_result.urgency,
            "action": ai_result.action,
            "confidence_score": ai_result.confidence_score,
            "justifications": ai_result.justifications,
            "provider": f"ai_assisted"
        }
