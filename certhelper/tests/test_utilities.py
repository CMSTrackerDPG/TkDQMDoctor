from django.test import TestCase

from certhelper.utilities.utilities import is_valid_date, get_date_string, to_date


class UtilitiesTest(TestCase):
    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("1999-01-01"))
        self.assertTrue(is_valid_date("2000-12-31"))
        self.assertTrue(is_valid_date("2018-02-28"))
        self.assertTrue(is_valid_date("2018-02-28"))
        self.assertFalse(is_valid_date("2018-02-29"))
        self.assertTrue(is_valid_date("2020-02-29"))
        self.assertFalse(is_valid_date("2020-02-30"))
        self.assertTrue(is_valid_date("5362-02-13"))

    def test_get_date_string(self):
        self.assertEqual(get_date_string("1900", "01", "01"), "1900-01-01")
        self.assertEqual(get_date_string("2099", "12", "31"), "2099-12-31")
        self.assertEqual(get_date_string("2999", "3", "7"), "2999-03-07")
        self.assertEqual(get_date_string("2018", "5", "31"), "2018-05-31")
        #self.assertEqual(get_date_string("2018", "03", "29"), "")
        self.assertEqual(get_date_string("2018", "03", "28"), "2018-03-28")
        #self.assertEqual(get_date_string("a", "03", "28"), "")
        #self.assertEqual(get_date_string("2018", "bcd", "29"), "")
        #self.assertEqual(get_date_string("2018", "03", "!"), "")

    #TODO ?????
    #def test_get_weekdayname(self, datestring):
    #    return to_date(datestring).strftime("%A")
