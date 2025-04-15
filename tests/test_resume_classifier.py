import unittest
from ml_model.resume_classifier import predict_resume_title


class TestResumeClassifier(unittest.TestCase):

    def setUp(self):
        self.sample_resume = """
        Experienced data scientist with strong Python and machine learning skills.
        Worked on NLP projects using TensorFlow and scikit-learn.
        """

    def test_prediction_type_and_confidence(self):
        prediction, confidence = predict_resume_title(self.sample_resume)

        # Ensure output is a non-empty string
        self.assertIsInstance(prediction, str, "Prediction should be a string")
        self.assertGreater(len(prediction.strip()), 0, "Prediction should not be empty")

        # Confidence should be a float between 0 and 100
        self.assertIsInstance(confidence, float, "Confidence should be a float")
        self.assertGreaterEqual(confidence, 0.0, "Confidence must be >= 0")
        self.assertLessEqual(confidence, 100.0, "Confidence must be <= 100")

    def test_prediction_meaningfulness(self):
        prediction, _ = predict_resume_title(self.sample_resume)
        expected_keywords = ["Data", "Scientist", "Engineer", "Analyst"]
        match_found = any(keyword in prediction for keyword in expected_keywords)
        self.assertTrue(match_found, f"Prediction should contain one of: {expected_keywords}")
        def test_minimal_resume(self):
    short_text = "Python, SQL, Java"
    prediction, confidence = predict_resume_title(short_text)
    self.assertIsInstance(prediction, str)
    self.assertIsInstance(confidence, float)

def test_empty_resume(self):
    empty_text = ""
    prediction, confidence = predict_resume_title(empty_text)
    self.assertIsInstance(prediction, str)
    self.assertLessEqual(confidence, 50)



if __name__ == "__main__":
    unittest.main()
