import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from utils.get_lanaguages import get_lanaguages

class TestGetLanaguages(unittest.TestCase):
    def test_get_lanaguages_int(self):
        """
        Test that it can find languages in a job description
        """
        data = "Minimum of five year of experience using a variety of development tools, including .NET (C#) , ASP.Net – MVC or ASP.Net Core, SQL, JavaScript front end frameworks, Angular, HTML5, Single Page Web Application Development."
        result = get_lanaguages(data, "../languages.json")
        self.assertEqual(result, ["HTML", "Javascript", "Java"])

if __name__ == '__main__':
    unittest.main()