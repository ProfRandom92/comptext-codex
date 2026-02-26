"""Tests for MedGemma-CompText-Impact modules."""

import json

import pytest

from src.core.schema import PatientState
from src.core.comptext_mock import StateCompressor
from src.agents.nurse import NurseAgent
from src.agents.doctor import DoctorAgent, RemoteLLMClient


class TestPatientState:
    """Tests for the PatientState Pydantic model."""

    def test_default_values(self):
        state = PatientState()
        assert state.chief_complaint == ""
        assert state.vitals == {}
        assert state.symptoms == []
        assert state.history_summary == ""

    def test_with_values(self):
        state = PatientState(
            chief_complaint="headache",
            vitals={"temperature": "39°C"},
            symptoms=["headache", "fever"],
            history_summary="Since yesterday",
        )
        assert state.chief_complaint == "headache"
        assert state.vitals["temperature"] == "39°C"
        assert len(state.symptoms) == 2

    def test_json_serialization(self):
        state = PatientState(
            chief_complaint="fever",
            symptoms=["fever"],
        )
        data = json.loads(state.model_dump_json())
        assert data["chief_complaint"] == "fever"
        assert data["symptoms"] == ["fever"]


class TestStateCompressor:
    """Tests for the StateCompressor heuristic extractor."""

    def test_extract_symptoms(self):
        compressor = StateCompressor()
        state = compressor.compress("I have a headache and nausea")
        assert "headache" in state.symptoms
        assert "nausea" in state.symptoms

    def test_extract_temperature(self):
        compressor = StateCompressor()
        state = compressor.compress("My temperature is 39C")
        assert "temperature" in state.vitals
        assert "39" in state.vitals["temperature"]

    def test_extract_heart_rate(self):
        compressor = StateCompressor()
        state = compressor.compress("My heart rate is 92 bpm")
        assert "heart_rate" in state.vitals
        assert "92" in state.vitals["heart_rate"]

    def test_extract_blood_pressure(self):
        compressor = StateCompressor()
        state = compressor.compress("Blood pressure 120/80")
        assert "blood_pressure" in state.vitals
        assert "120/80" in state.vitals["blood_pressure"]

    def test_extract_duration(self):
        compressor = StateCompressor()
        state = compressor.compress("I have a headache since yesterday")
        assert "yesterday" in state.history_summary

    def test_chief_complaint_first_symptom(self):
        compressor = StateCompressor()
        state = compressor.compress("I have fever and headache")
        # Chief complaint is the first match from the keyword list
        assert state.chief_complaint in ("headache", "fever")

    def test_no_symptoms(self):
        compressor = StateCompressor()
        state = compressor.compress("I feel unwell")
        assert state.chief_complaint == "unspecified"
        assert state.symptoms == []


class TestNurseAgent:
    """Tests for the NurseAgent."""

    def test_intake_returns_patient_state(self):
        nurse = NurseAgent()
        state = nurse.intake("I have a headache and 39C fever")
        assert isinstance(state, PatientState)
        assert "headache" in state.symptoms
        assert "fever" in state.symptoms


class TestRemoteLLMClient:
    """Tests for the RemoteLLMClient."""

    def test_mock_mode_returns_response(self):
        client = RemoteLLMClient(mock_mode=True)
        response = client.generate("test prompt")
        assert len(response) > 0
        assert "Mock Mode" in response

    def test_mock_mode_default(self):
        client = RemoteLLMClient()
        assert client.mock_mode is True

    def test_endpoint_from_param(self):
        client = RemoteLLMClient(
            endpoint_url="http://example.com/api",
            mock_mode=True,
        )
        assert client.endpoint_url == "http://example.com/api"


class TestDoctorAgent:
    """Tests for the DoctorAgent."""

    def test_diagnose_returns_string(self):
        doctor = DoctorAgent()
        state = PatientState(
            chief_complaint="fever",
            vitals={"temperature": "39°C"},
            symptoms=["fever", "headache"],
        )
        result = doctor.diagnose(state)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_diagnose_uses_mock(self):
        doctor = DoctorAgent()
        state = PatientState(chief_complaint="cough")
        result = doctor.diagnose(state)
        assert "Mock Mode" in result
