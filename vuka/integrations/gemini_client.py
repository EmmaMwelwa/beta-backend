from __future__ import annotations
import json
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
GEMINI_MODEL = "gemini-3.5-flash"

class _GenQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str

class _GenQuizResponse(BaseModel):
    category: str
    questions: list[_GenQuestion]

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("No Gemini API key provided. Please set GEMINI_API_KEY in your .env file.")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_quiz(self, media_description: str, source_platform: str, external_media_url: str, num_questions: int = 4, category_hint: Optional[str] = None) -> dict:
        client = self._get_client()
        from google.genai import types

        prompt = f"""
You are the assessment engine for VUKA.

VUKA is a platform that helps Kenyan high-school graduates
turn educational social-media content into structured
career and skill development.

A user has consumed the following educational content.

Source platform:
{source_platform}

Content URL:
{external_media_url}

Content description:
\"\"\"
{media_description}
\"\"\"

Your task is to create a short assessment that checks
whether the user actually understood the content.

Generate exactly {num_questions} multiple-choice questions.

Rules:

1. Every question must be based ONLY on the provided content
   description.

2. Do not create questions based on the URL itself.

3. Do not create questions about the social-media platform.

4. Each question must have exactly 4 answer options.

5. Only one answer may be correct.

6. correct_index must be zero-based.

7. Provide a short explanation for the correct answer.

8. Questions should test comprehension rather than memorization
   whenever possible.

9. Classify the content into exactly ONE of these categories:

   technical_skills
   soft_skills
   career_readiness
   digital_literacy

Return valid JSON matching the requested schema.
"""

        if category_hint:
            prompt += f"""

The requested category hint is:
{category_hint}

Prefer this category when it is appropriate for the content.
"""

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_GenQuizResponse,
                temperature=0.4,
            ),
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            return json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini returned invalid JSON.") from exc