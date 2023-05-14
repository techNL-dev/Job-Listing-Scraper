import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from utils.get_category import get_category

class TestGetCategory(unittest.TestCase):
    def test_get_category_int(self):
        """
        Test that it can correctly categorize job by job title
        """
        data = "Software Developer"
        result = get_category(data, "../categories.json")
        self.assertEqual(result, "Software Developer")

if __name__ == '__main__':
    unittest.main()