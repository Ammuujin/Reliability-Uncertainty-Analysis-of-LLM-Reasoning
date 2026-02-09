"""
Thin wrapper around the Google Gemini API (google-genai SDK).
Handles authentication, rate limiting, and retry logic.
"""

import os
import time
import logging
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMClient:
    """Gemini API client with retry and rate-limiting support."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        rate_limit_rpm: int = 15,
        retry_max: int = 3,
        retry_backoff_seconds: float = 5.0,
    ):
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Copy .env.example to .env and add your key."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.retry_max = retry_max
        self.retry_backoff = retry_backoff_seconds

        # Simple rate limiter: minimum seconds between calls
        self._min_interval = 60.0 / rate_limit_rpm
        self._last_call_time: float = 0.0

    def _wait_for_rate_limit(self) -> None:
        """Block until we're allowed to make the next call."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_output_tokens: int = 1024,
    ) -> str:
        """
        Send a prompt to the model and return the response text.
        Retries on transient errors with exponential backoff.
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        last_error: Optional[Exception] = None

        for attempt in range(1, self.retry_max + 1):
            try:
                self._wait_for_rate_limit()
                self._last_call_time = time.time()

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""

            except Exception as e:
                last_error = e
                wait = self.retry_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "API call failed (attempt %d/%d): %s — retrying in %.1fs",
                    attempt,
                    self.retry_max,
                    str(e),
                    wait,
                )
                time.sleep(wait)

        raise RuntimeError(
            f"API call failed after {self.retry_max} retries: {last_error}"
        )
