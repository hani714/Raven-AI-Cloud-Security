import os
import json
from datetime import datetime, date
from typing import Dict, Any

class PromptConstructor:
    def __init__(self):
        self.templates = {
            'stage1_triage': self._load_template('stage1_triage.txt'),
            'stage2_analysis': self._load_template('stage2_analysis.txt'),
            'stage3_commands': self._load_template('stage3_commands.txt')
        }

    def _load_template(self, filename: str) -> str:
        path = os.path.join(os.path.dirname(__file__), "templates", filename)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt template file not found at {path}")
        
        with open(path, 'r') as file:
            return file.read()
    
    def _custom_serializer(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    async def construct_triage_prompt(self, risk_summary: Dict[str, Any]) -> str:
        try:
            json_str = json.dumps(risk_summary, indent=2, default=self._custom_serializer)
            return self.templates['stage1_triage'].replace('{risk_summary}', json_str)
        except Exception as e:
            raise ValueError(f"Failed to construct triage prompt: {str(e)}") from e
    
    async def construct_analysis_prompt(self, processed_data: Dict[str, Any], triage_result: Dict[str, Any]) -> str:
        try:
            data_json = json.dumps(processed_data, indent=2, default=self._custom_serializer)
            triage_json = json.dumps(triage_result, indent=2, default=self._custom_serializer)
            scan_id = processed_data.get('metadata', {}).get('scan_id', 'N/A')
            
            prompt = self.templates['stage2_analysis']
            prompt = prompt.replace('{scan_id}', str(scan_id))
            prompt = prompt.replace('{triage_result}', triage_json)
            prompt = prompt.replace('{processed_data}', data_json)
            
            return prompt
        except Exception as e:
            raise ValueError(f"Failed to construct analysis prompt: {str(e)}") from e
    
    async def construct_commands_prompt(self, attack_paths: list) -> str:
        try:
            paths_json = json.dumps(attack_paths, indent=2, default=self._custom_serializer)
            return self.templates['stage3_commands'].replace('{attack_paths}', paths_json)
        except Exception as e:
            raise ValueError(f"Failed to construct commands prompt: {str(e)}") from e
