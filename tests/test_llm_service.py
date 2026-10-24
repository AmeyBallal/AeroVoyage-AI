"""Unit tests for Groq LLM Service and Fallback Logic."""

import unittest
from unittest.mock import patch, MagicMock
from src.services.llm_service import (
    is_groq_available,
    parse_intent_with_llm,
    synthesize_travel_brief_with_llm,
    answer_travel_qa_with_llm,
)
from src.services.travel_engine import parse_intent_from_text


class TestLLMService(unittest.TestCase):

    def test_groq_availability_without_key(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": ""}):
            self.assertFalse(is_groq_available())
            self.assertIsNone(parse_intent_with_llm("trip to Tokyo"))
            self.assertIsNone(answer_travel_qa_with_llm("what is FET?"))

    @patch("requests.post")
    def test_parse_intent_with_mocked_groq(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"cities": ["Berlin", "Zurich", "Milan"], "days": 5, "budget": 2400, "is_business": true, "is_multi_city": true, "meeting_focus": "Fastest connections"}'
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test123"}):
            self.assertTrue(is_groq_available())
            intent = parse_intent_with_llm(
                "Plan a 5-day business trip across Berlin, Zurich, and Milan with fastest connections"
            )
            self.assertIsNotNone(intent)
            self.assertEqual(intent["cities"], ["Berlin", "Zurich", "Milan"])
            self.assertEqual(intent["days"], 5)
            self.assertEqual(intent["budget"], 2400.0)
            self.assertTrue(intent["is_business"])
            self.assertTrue(intent["is_multi_city"])

    @patch("requests.post")
    def test_answer_travel_qa_with_mocked_groq(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "You do not need an internal passport control when traveling between Zurich and Milan under Schengen regulations."
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test123"}):
            answer = answer_travel_qa_with_llm("Do I need border control from Zurich to Milan?")
            self.assertIn("Zurich and Milan", answer)

    def test_travel_engine_fallback_when_no_groq(self):
        # Even without Groq, travel engine extracts intent deterministically
        with patch.dict("os.environ", {"GROQ_API_KEY": ""}):
            intent = parse_intent_from_text(
                "Plan a 5-day business trip across Berlin, Zurich, and Milan"
            )
            self.assertIn("Berlin", intent["cities"])
            self.assertIn("Zurich", intent["cities"])
            self.assertIn("Milan", intent["cities"])
            self.assertEqual(intent["days"], 5)


if __name__ == "__main__":
    unittest.main()
