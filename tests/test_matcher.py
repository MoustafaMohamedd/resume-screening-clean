import unittest
from utils.matcher import (
    calculate_match_score,
    calculate_synonym_boosted_score,
    generate_feedback,
    get_bert_similarity
)


class TestMatcher(unittest.TestCase):

    def test_exact_match_score(self):
        resume_skills = ["python", "sql", "communication"]
        jd_skills = ["python", "sql", "excel"]
        score, matched = calculate_match_score(resume_skills, jd_skills)
        self.assertAlmostEqual(score, 66.67, places=1)
        self.assertIn("python", matched)
        self.assertIn("sql", matched)

    def test_synonym_boosted_score(self):
        resume_skills = ["leadership"]
        jd_skills = ["management"]
        score, matched = calculate_synonym_boosted_score(resume_skills, jd_skills)
        self.assertGreaterEqual(score, 50)
        self.assertIn("management", matched)

    def test_feedback_strong(self):
        feedback = generate_feedback(85, ["python"], ["python"])
        self.assertIn("Strong", feedback)

    def test_feedback_moderate(self):
        feedback = generate_feedback(60, ["python"], ["python", "sql"])
        self.assertIn("Moderate", feedback)

    def test_feedback_weak(self):
        feedback = generate_feedback(20, [], ["python", "sql"])
        self.assertIn("Weak", feedback)

    def test_bert_similarity_fallback(self):
        sim = get_bert_similarity("Python developer with Flask", "Backend engineer using Python")
        self.assertIsInstance(sim, float)
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 100.0)


if __name__ == "__main__":
    unittest.main()
