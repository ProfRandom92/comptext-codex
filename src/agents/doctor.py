"""Doctor agent: diagnosis from compressed patient state."""

import os
from typing import Optional

import requests
from dotenv import load_dotenv

from src.core.schema import PatientState

load_dotenv()


class RemoteLLMClient:
    """Client for remote LLM inference with mock fallback.

    Reads the remote endpoint URL from the ``REMOTE_LLM_URL``
    environment variable.  When ``mock_mode`` is ``True`` (the
    default), the client returns deterministic dummy medical advice
    so the demo can run without a GPU server.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        mock_mode: bool = True,
    ) -> None:
        self.endpoint_url = endpoint_url or os.getenv("REMOTE_LLM_URL", "")
        self.mock_mode = mock_mode

    def generate(self, prompt: str) -> str:
        """Send a prompt to the remote LLM or return a mock response.

        Args:
            prompt: The text prompt to send.

        Returns:
            The generated text from the LLM or mock output.
        """
        if self.mock_mode or not self.endpoint_url:
            return self._mock_response(prompt)

        response = requests.post(
            self.endpoint_url,
            json={"prompt": prompt},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("text", "")

    @staticmethod
    def _mock_response(prompt: str) -> str:
        """Return deterministic mock medical advice."""
        return (
            "Based on the compressed patient state, the following is "
            "recommended:\n"
            "1. Monitor temperature and hydration levels closely.\n"
            "2. Administer antipyretics if fever exceeds 38.5°C.\n"
            "3. Schedule follow-up in 24-48 hours if symptoms persist.\n"
            "4. Consider blood work (CBC, CRP) to rule out infection.\n"
            "\n[Mock Mode] This is a simulated response. Connect a "
            "remote LLM endpoint via REMOTE_LLM_URL for real inference."
        )


class DoctorAgent:
    """Diagnosis agent that operates solely on the compressed state.

    Receives only the PatientState JSON—never the raw text—
    demonstrating the CompText State Transfer efficiency.
    """

    def __init__(self, llm_client: Optional[RemoteLLMClient] = None) -> None:
        self._llm = llm_client or RemoteLLMClient(mock_mode=True)

    def diagnose(self, state: PatientState) -> str:
        """Generate a diagnosis/recommendation from patient state.

        Args:
            state: The compressed PatientState object.

        Returns:
            A diagnosis/recommendation string.
        """
        prompt = (
            "You are a medical AI assistant. Based on the following "
            "compressed patient state, provide a brief differential "
            "diagnosis and recommended next steps.\n\n"
            f"Patient State:\n{state.model_dump_json(indent=2)}"
        )
        return self._llm.generate(prompt)
