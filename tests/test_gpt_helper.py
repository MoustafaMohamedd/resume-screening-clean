import unittest
from unittest.mock import patch
from utils.gpt_helper import suggest_job_titles


class TestGPTHelper(unittest.TestCase):

    @patch("utils.gpt_helper.requests.post")
    def test_suggest_job_titles_success(self, mock_post):
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {
                    "content": "- Software Engineer\n- Backend Developer\n- Python Developer"
                }
            }]
        }

        skills = ["python", "flask"]
        result = suggest_job_titles(skills, api_key="fake-key")
        self.assertIsInstance(result, list)
        self.assertIn("Software Engineer", result)

    @patch("utils.gpt_helper.requests.post")
    def test_suggest_job_titles_empty(self, mock_post):
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }

        result = suggest_job_titles(["python"], api_key="fake-key")
        self.assertEqual(result, ["❌ GPT returned empty"])

    def test_missing_api_key(self):
        # Simulate empty env key
        result = suggest_job_titles(["sql"], api_key="")
        self.assertEqual(result, ["❌ Missing API key"])

    def test_no_skills(self):
        result = suggest_job_titles([], api_key="fake")
        self.assertEqual(result, ["❌ No skills provided"])
    @patch("utils.gpt_helper.requests.post", side_effect=Exception("Timeout"))
def test_gpt_api_error_handling(self, mock_post):
    result = suggest_job_titles(["Python"], api_key="fake")
    self.assertTrue(result[0].startswith("❌ GPT Error"))

        


if __name__ == "__main__":
    unittest.main()
