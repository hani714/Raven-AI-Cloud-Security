import re
import json
import time
import logging
from typing import Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv

from groq import AsyncGroq
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from .prompt_constructor import PromptConstructor
from app.monitoring.metrics import llm_calls_total, llm_response_duration_seconds

load_dotenv()
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.pc = PromptConstructor()
        self.provider: Optional[str] = None
        self.api_key: Optional[str] = None
        self.model_id: Optional[str] = None

        # Provider SDK clients
        self._groq_client = None
        self._gemini_client = None
        self._openai_client: Optional[AsyncOpenAI] = None
        self._anthropic_client: Optional[AsyncAnthropic] = None

    def configure(self, provider: str, api_key: Optional[str], model_id: Optional[str]) -> None:
        normalized = provider.strip().lower()
        if normalized in {"google", "google_ai", "googleai", "vertex_ai"}:
            normalized = "gemini"

        self.provider = normalized
        self.model_id = model_id

        if normalized == "gemini":
            self.api_key = api_key
            if not self.api_key:
                raise ValueError("Gemini API key is required.")
            self._gemini_client = genai.Client(api_key=self.api_key)

        elif normalized == "groq":
            self.api_key = api_key
            if not self.api_key:
                raise ValueError("Groq API key is required.")
            self._groq_client = AsyncGroq(api_key=self.api_key)

        elif normalized == "openai":
            self.api_key = api_key
            if not self.api_key:
                raise ValueError("OpenAI API key is required.")
            self._openai_client = AsyncOpenAI(api_key=self.api_key)

        elif normalized == "anthropic":
            self.api_key = api_key
            if not self.api_key:
                raise ValueError("Anthropic API key is required.")
            self._anthropic_client = AsyncAnthropic(api_key=self.api_key)

        elif normalized == "ollama":
            pass

        else:
            raise ValueError(f"Unsupported provider: {normalized}")

    def _ensure_configured(self) -> None:
        if not self.provider:
            raise ValueError("LLM provider is not configured. Call configure() first.")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            return {
                "error": "Failed to parse JSON response",
                "raw_text": text[:500]
            }

    async def _generate_text(self, prompt: str, temperature: float, max_tokens: int) -> str:
        self._ensure_configured()

        if self.provider == "gemini":
            return await self._generate_gemini(prompt, temperature, max_tokens)
        elif self.provider == "groq":
            return await self._generate_groq(prompt, temperature, max_tokens)
        elif self.provider == "openai":
            return await self._generate_openai(prompt, temperature, max_tokens)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(prompt, temperature, max_tokens)
        elif self.provider == "ollama":
            return await self._generate_ollama(prompt, temperature, max_tokens)

        raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _generate_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
    
        if not self.model_id:
            raise ValueError("Ollama model ID is not configured.")
        
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 8192
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    raise ValueError(f"Ollama request failed: {response.status}")
                
                result = await response.json()
                
                if not result.get("response"):
                    return ""
                
                return result["response"]

    async def _generate_gemini(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self._gemini_client:
            raise ValueError("Gemini client is not configured.")

        response = await self._gemini_client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )

        if not response.candidates or not response.candidates[0].content.parts:
            return ""

        return response.text

    async def _generate_groq(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self._groq_client:
            raise ValueError("Groq client is not configured.")

        response = await self._groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        if not response.choices or not response.choices[0].message.content:
            return ""

        return response.choices[0].message.content

    async def _generate_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self._openai_client:
            raise ValueError("OpenAI client is not configured.")

        response = await self._openai_client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    async def _generate_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self._anthropic_client:
            raise ValueError("Anthropic client is not configured.")

        response = await self._anthropic_client.messages.create(
            model=self.model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text or ""

    # ── The three core functions are unchanged ─────────────────────────────

    async def triage(self, risk_summary: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        prompt = await self.pc.construct_triage_prompt(risk_summary)
        try:
            text = await self._generate_text(prompt, temperature=0.3, max_tokens=1024)
            if not text:
                return {"error": "Empty response", "severity": "unknown", "requires_deep_analysis": False}
            result = self._extract_json(text)
            llm_calls_total.labels(stage='triage', status='success').inc()
            llm_response_duration_seconds.labels(stage='triage').observe(time.time() - start_time)
            return result
        except Exception as e:
            llm_calls_total.labels(stage='triage', status='error').inc()
            llm_response_duration_seconds.labels(stage='triage').observe(time.time() - start_time)
            return {"error": f"Triage failed: {str(e)}", "severity": "unknown", "requires_deep_analysis": False}

    async def deep_analysis(self, processed_data: Dict[str, Any], triage_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        prompt = await self.pc.construct_analysis_prompt(processed_data, triage_result)
        try:
            text = await self._generate_text(prompt, temperature=0.4, max_tokens=4096)
            if not text:
                return {"error": "Empty response", "attack_paths": []}
            result = self._extract_json(text)
            llm_calls_total.labels(stage='deep_analysis', status='success').inc()
            llm_response_duration_seconds.labels(stage='deep_analysis').observe(time.time() - start_time)
            return result
        except Exception as e:
            llm_calls_total.labels(stage='deep_analysis', status='error').inc()
            llm_response_duration_seconds.labels(stage='deep_analysis').observe(time.time() - start_time)
            return {"error": f"Analysis failed: {str(e)}", "attack_paths": []}

    async def generate_commands(self, attack_paths: list) -> Dict[str, Any]:
        start_time = time.time()
        prompt = await self.pc.construct_commands_prompt(attack_paths)
        try:
            text = await self._generate_text(prompt, temperature=0.2, max_tokens=2048)
            if not text:
                return {"error": "Empty response", "exploitation_commands": []}
            result = self._extract_json(text)
            llm_calls_total.labels(stage='command_generation', status='success').inc()
            llm_response_duration_seconds.labels(stage='command_generation').observe(time.time() - start_time)
            return result
        except Exception as e:
            llm_calls_total.labels(stage='command_generation', status='error').inc()
            llm_response_duration_seconds.labels(stage='command_generation').observe(time.time() - start_time)
            return {"error": f"Command generation failed: {str(e)}", "exploitation_commands": []}