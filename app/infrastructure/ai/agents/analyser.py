# app/infrastructure/ai/agents/analyser.py

import json
import logging
from typing import Dict, Any, List, Optional
from app.infrastructure.ai.agents.base import BaseAgent
from app.infrastructure.ai.base import BaseAIClient
from app.core.config import get_settings
from app.domain.entities.ticket import TicketEntity

logger = logging.getLogger("savia")

UNIFIED_ANALYSER_PROMPT = """
Tu es un expert SAV technique et un moteur d'analyse intelligent. Ta mission est de qualifier un ticket incident ET de fournir un diagnostic basé sur la documentation fournie.

### DONNÉES EN ENTRÉE :
1. **Message Client** : Description du problème.
2. **Référence Produit** : Modèle de l'appareil.
3. **Documentation Technique** : Extraits pertinents (RAG) issus des manuels.

### RÈGLES DE DÉCISION (CLASSIFICATION ET SÉCURITÉ) :
1. **Action Recommandée** :
   - `request_additional_info` : Si le message est trop court ou manque de précisions ET qu'aucune aide générale n'est disponible dans la doc.
   - `schedule_intervention` : Si le problème est critique (fuite, gaz, court-circuit).
   - `auto_resolution` : Si une solution claire est trouvée OU si la documentation contient une section "Dépannage" / "Vérifications de base" correspondant au symptôme général (ex: "ne chauffe plus"). Dans ce cas, propose ces étapes au lieu de poser des questions.
   - `escalate_to_human` : Si le problème est complexe, ou SI AUCUNE SOLUTION N'EST TROUVÉE DANS LA DOC malgré la présence de documentation.
2. **Priorité au Dépannage** : Si le client est vague (ex: "ça ne marche plus") mais que la doc liste des causes/solutions pour ce symptôme général, privilégie `auto_resolution` en listant ces solutions.
3. **Règle Anti-Hallucination** : 
   - SI de la documentation est fournie MAIS que le problème n'y est pas traité : force `action` à `escalate_to_human`.
   - NE JAMAIS inventer de solution technique qui n'est pas dans la doc.

### RÈGLES DE FORMATAGE (MESSAGE_IA) :
Le champ `message_ia` doit donner l'impression qu'un technicien humain répond. NE JAMAIS mentionner "IA", "moteur d'analyse" ou "documentation technique".

1. **SI DES INFORMATIONS SONT MANQUANTES** :
   Repond comme un technicien SAV pour demander les informations manquantes

2. **SI UNE SOLUTION EST TROUVÉE** :
   Utilise ce format Markdown :
   ```
   Problème identifié : <Brève explication>
   Numerote si ce sont des etapes sinon met juste des tirets
   - <Étape 1>
   - <Étape 2>
   
   ⚠️ Avertissements : (si applicable)
   - <Avertissement>
   ```

3. **SI AUCUNE SOLUTION N'EST TROUVÉE (ESCALADE)** :
   Utilise ce format :
   "Nous avons consulté la documentation technique mais n'avons pas trouvé de solution précise pour ce problème. Un technicien va vous recontacter."

### FORMAT DE SORTIE (JSON UNIQUEMENT) :
{
  "category": "<heating|plumbing|electrical|ventilation|other>",
  "urgency": "<critical|high|medium|low>",
  "action": "<auto_resolution|request_additional_info|schedule_intervention|escalate_to_human>",
  "confidence_score": <float 0.0-1.0>,
  "justifications": ["..."],
  "diagnostic_help": "<Diagnostic technique détaillé interne>",
  "recommended_actions": ["Étape 1", "Étape 2"],
  "important_warnings": ["Attention à..."],
  "message_ia": "<Le message formatté selon les règles ci-dessus>"
}
"""

class AnalyserAgent(BaseAgent, BaseAIClient):
    """
    Agent Unifié: Gère la classification ET le diagnostic.
    """
    def __init__(self):
        BaseAgent.__init__(self, "AnalyserAgent")
        BaseAIClient.__init__(self)

    async def process(
        self, 
        ticket: TicketEntity, 
        doc_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        Analyse complète du ticket avec ou sans documentation.
        """
        settings = get_settings()
        context_docs = "\n\n".join(doc_chunks) if doc_chunks else "AUCUNE DOCUMENTATION TROUVÉE POUR CETTE RÉFÉRENCE."
        
        prompt_user = f"""
### TICKET :
Message: {ticket.message}
Référence: {ticket.product_reference or 'Inconnue'}
Type: {ticket.problem_type or 'Non spécifié'}

### DOCUMENTATION TECHNIQUE :
{context_docs}
"""

        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": UNIFIED_ANALYSER_PROMPT},
                {"role": "user", "content": prompt_user}
            ],
            "temperature": 0.2
        }

        try:
            data = await self.post(payload)
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            cleaned = self._clean_json(raw)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"[{self.name}] Erreur : {e}")
            return self._fallback_response(str(e))

    def _clean_json(self, raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```json"): cleaned = cleaned[7:].strip()
        elif cleaned.startswith("```"): cleaned = cleaned[3:].strip()
        if cleaned.endswith("```"): cleaned = cleaned[:-3].strip()
        return cleaned

    def _fallback_response(self, error: str) -> Dict[str, Any]:
        return {
            "category": "other", "urgency": "medium", "action": "escalate_to_human",
            "confidence_score": 0.0, "justifications": [f"Erreur technique : {error}"],
            "message_ia": "Une erreur technique est survenue. Un conseiller va prendre le relais."
        }
