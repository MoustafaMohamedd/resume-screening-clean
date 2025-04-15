import unittest
from utils.matcher import generate_skill_gap_suggestion

class TestSkillGapSuggestion(unittest.TestCase):

    def test_missing_skills_suggestion(self):
        resume_skills = ["Python", "SQL"]
        jd_skills = ["Python", "SQL", "AWS", "Docker"]
        suggestions = generate_skill_gap_suggestion(resume_skills, jd_skills)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any("AWS" in s or "Docker" in s for s in suggestions))

    def test_no_missing_skills(self):
        resume_skills = ["Python", "SQL", "Docker"]
        jd_skills = ["Python", "SQL"]
        suggestions = generate_skill_gap_suggestion(resume_skills, jd_skills)
        
        self.assertIsInstance(suggestions, list)
        self.assertIn("✅ No major skill gaps!", suggestions)

    def test_empty_input(self):
        suggestions = generate_skill_gap_suggestion([], [])
        self.assertIsInstance(suggestions, list)
        self.assertTrue("❌ No job description skills provided" in suggestions or len(suggestions) >= 1)
        def test_resume_has_skills_but_jd_is_empty(self):
        resume_skills = ["Python", "SQL"]
        jd_skills = []
        suggestions = generate_skill_gap_suggestion(resume_skills, jd_skills)
        self.assertIn("❌ No job description skills provided", suggestions)

        def test_identical_skills(self):
        resume_skills = ["Python", "SQL"]
        jd_skills = ["Python", "SQL"]
        suggestions = generate_skill_gap_suggestion(resume_skills, jd_skills)
        self.assertEqual(suggestions, ["✅ No major skill gaps!"])


if __name__ == "__main__":
    unittest.main()
