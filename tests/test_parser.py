import unittest
from utils.parser import extract_resume_data


class TestParser(unittest.TestCase):

    def setUp(self):
        self.sample_text = """
        John Doe
        Email: john@example.com
        Phone: +1234567890

        Skills:
        - Python
        - Flask
        - SQL
        - Communication

        Experience:
        - Worked at ABC Corp as Backend Developer
        - Built APIs using Flask

        Education:
        - BSc in Computer Science
        """

    def test_extract_skills(self):
        data = extract_resume_data(self.sample_text)
        self.assertIn("Python", data["skills"])
        self.assertIn("Flask", data["skills"])
        self.assertIn("SQL", data["skills"])

    def test_extract_experience_length(self):
        data = extract_resume_data(self.sample_text)
        experience = data.get("experience")
        self.assertIsInstance(experience, str)
        self.assertGreater(len(experience.strip()), 0, "Experience section should not be empty")

    def test_extracted_data_structure(self):
        data = extract_resume_data(self.sample_text)
        self.assertIn("skills", data)
        self.assertIn("experience", data)
        self.assertIsInstance(data["skills"], list)
        self.assertIsInstance(data["experience"], str)

    def test_extracted_keywords_from_experience(self):
        data = extract_resume_data(self.sample_text)
        experience_text = data.get("experience", "").lower()
        self.assertIn("backend", experience_text)
        self.assertIn("developer", experience_text)
        self.assertIn("flask", experience_text)
        def test_empty_resume_text(self):
    data = extract_resume_data("")
    self.assertIsInstance(data, dict)
    self.assertEqual(data["skills"], [])
    self.assertEqual(data["experience"], "")

def test_resume_with_no_skills_section(self):
    text = "Just some plain text about hobbies and random info."
    data = extract_resume_data(text)
    self.assertIsInstance(data["skills"], list)
    self.assertEqual(len(data["skills"]), 0)



if __name__ == "__main__":
    unittest.main()
