import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi.encoders import jsonable_encoder

from app.database.mongodb import store_result, get_by_scan_id
from app.repositories import ScanRepository, ByokRepository
from app.schemas import CurrentUser, AttackPath
from genai.data_preprocessor import DataPreprocessor
from genai.risk_analyzer import RiskAnalyzer
from genai.query import LLMClient
from app.utils import convert_dataclasses_to_dict, get_cached, set_cached, convert_objectids, decrypt_api_key

logger = logging.getLogger(__name__)

class GenAIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scan_repo = ScanRepository(db)
        self.byok_repo = ByokRepository(db)
        self.preprocessor = DataPreprocessor()
        self.risk_analyzer = RiskAnalyzer()
        self.llm = LLMClient()

    async def get_attack_path(self, scan_id: str, user_id: str, cache) -> Optional[AttackPath]:
        scan = await self.scan_repo.get_by_scan_id(scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found",
            )
        if str(scan["user_id"]) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to scan",
            )
        
        cache_key = f"attack_path:{scan_id}"

        if cached := await get_cached(cache, cache_key):
            return AttackPath(**cached[0])

        
        results = await get_by_scan_id("attack_analysis", scan_id)
        if not results:
                return None

        r = await convert_objectids(results)
        encoded_data = jsonable_encoder(r)
        await set_cached(cache, cache_key, encoded_data)
        return AttackPath(**encoded_data[0])
    
    async def attack_path(self, scan_id: str, model_id: str, current_user: CurrentUser, scan_results):
        try:
            analysis_level = (
                current_user.analysis_level.value
                if hasattr(current_user.analysis_level, "value")
                else str(current_user.analysis_level)
            )

            if model_id == "default":
                provider_slug = "ollama"
                provider_model = "qwen2.5-coder:7b"
                api_key = None

                self.llm.configure(provider_slug, api_key, provider_model)
            
            else:
                byok_key = await self.byok_repo.get_user_key_for_model(current_user.id, model_id)
                if not byok_key:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="BYOK model not found for user",
                    )

                provider_slug = byok_key.provider.slug
                provider_model = byok_key.model.model_id
                encrypted_api_key = byok_key.encrypted_key
                api_key = decrypt_api_key(encrypted_api_key)

                self.llm.configure(provider_slug, api_key, provider_model)

            # Stage 0: Get raw enumeration data
            enum_data = convert_dataclasses_to_dict(scan_results)
            
            # Stage 1: Preprocess data
            processed_data = self.preprocessor.preprocess_enumeration_data(enum_data)
            
            # Stage 2: Calculate risk scores
            risk_summary = self.risk_analyzer.analyze(processed_data)
            
            triage_result = None
            analysis_result = None
            commands_result = None

            # Stage 3: Quick triage with LLM
            if analysis_level in {'triage', 'deep', 'exploit'}:
                triage_result = await self.llm.triage(risk_summary)
                
            # Check if deep analysis is needed
            severity = triage_result.get('severity', 'low') if triage_result else 'low'
            requires_deep = triage_result.get('requires_deep_analysis', False) if triage_result else False
                
            if severity in ['critical', 'high'] or requires_deep:
                if analysis_level in {'deep', 'exploit'}:
                    # Stage 4: Deep analysis
                    analysis_result = await self.llm.deep_analysis(processed_data, triage_result)
                    
                if analysis_level == 'exploit':
                    # Stage 5: Generate commands
                    attack_paths = analysis_result.get('attack_paths', [])
                    commands_result = await self.llm.generate_commands(attack_paths)
            
            # Create AttackPath object
            ap = AttackPath(
                scan_id=scan_id,
                severity=severity,
                triage=triage_result,
                analysis=analysis_result,
                commands=commands_result,
                risk_summary=risk_summary
            )
            
            # Save to MongoDB
            result_id = await store_result(
                "attack_analysis",
                ap
            )
            
            exploitation_commands = commands_result.get('commands', []) if commands_result else []

            cleaned = []

            for path in exploitation_commands:
                cleaned.append({
                    "path_id": path["path_id"],
                    "path_title": path["path_title"],
                    "commands": [
                        {
                            "step": cmd["step"],
                            "description": cmd["description"],
                            "command": cmd["command"]
                        }
                        for cmd in path.get("commands", [])
                    ]
                })

            return ap
                
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to generate attack path: {str(e)}")
