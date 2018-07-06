import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from mixer.backend.django import mixer

from certhelper.models import RunInfo
from certhelper.utilities.utilities import *

pytestmark = pytest.mark.django_db


class TestUtilities:
    def test_is_valid_date(self):
        assert True is is_valid_date("1999-01-01")
        assert True is is_valid_date("2000-12-31")
        assert True is is_valid_date("2018-02-28")
        assert True is is_valid_date("2018-02-28")
        assert False is is_valid_date("2018-02-29")
        assert True is is_valid_date("2020-02-29")
        assert False is is_valid_date("2020-02-30")
        assert True is is_valid_date("5362-02-13")

    def test_get_date_string(self):
        assert get_date_string("1900", "01", "01") == "1900-01-01"
        assert get_date_string("2099", "12", "31") == "2099-12-31"
        assert get_date_string("2999", "3", "7") == "2999-03-07"
        assert get_date_string("2018", "5", "31") == "2018-05-31"
        # assert get_date_string("2018", "03", "29") == ""
        assert get_date_string("2018", "03", "28") == "2018-03-28"
        assert get_date_string("2018", "", "28") == ""
        # assert get_date_string("a", "03", "28") == ""
        # assert get_date_string("2018", "bcd", "29") == ""
        # assert get_date_string("2018", "03", "!") == ""

    def test_to_date(self):
        d = to_date("2018-02-28")
        assert d == datetime.date(2018, 2, 28)
        assert to_date(datetime.date(2019, 12, 29)) == datetime.date(2019, 12, 29)
        assert to_date(datetime.datetime(2017, 1, 2, 3, 4, 5)) == datetime.date(2017, 1, 2)

        with pytest.raises(ValueError):
            to_date("2018-02-29")

    def test_to_weekdayname(self):
        assert to_weekdayname(to_date("2018-06-12")) == "Tuesday"

    def test_get_full_name(self):
        user1 = mixer.blend(User, username="abcdef1", first_name="Hans", last_name="Skywalker")
        user2 = mixer.blend(User, username="abcdef2", first_name="", last_name="Skywalker")
        user3 = mixer.blend(User, username="abcdef3", first_name="Hans", last_name="")
        user4 = mixer.blend(User, username="abc def4", first_name="", last_name="")

        assert get_full_name(user1) == "Hans Skywalker (abcdef1)"
        assert get_full_name(user2) == "Skywalker (abcdef2)"
        assert get_full_name(user3) == "Hans (abcdef3)"
        assert get_full_name(user4) == "abc def4"

    def test_is_valid_id(self):
        assert False is is_valid_id(1, RunInfo)
        mixer.blend("certhelper.RunInfo")
        assert True is is_valid_id(1, RunInfo)
        assert False is is_valid_id(2, RunInfo)
        assert False is is_valid_id("3", RunInfo)
        assert False is is_valid_id("a", RunInfo)
        assert True is is_valid_id("1", RunInfo)

    def test_get_this_week_filter_parameter(self):
        # TODO better test
        param = get_this_week_filter_parameter()
        assert param.startswith("?date__gte")
        assert "date__lte" in param

    def test_request_contains_filter_parameter(self):
        req = RequestFactory().get('/')
        assert False is request_contains_filter_parameter(req)
        user = mixer.blend(User)
        req.GET = req.GET.copy()
        req.GET["userid"] = user.id
        assert True is request_contains_filter_parameter(req)
        req = RequestFactory().get('/')
        req.GET = req.GET.copy()
        assert False is request_contains_filter_parameter(req)
        req.GET["date_year"] = "2017"
        assert True is request_contains_filter_parameter(req)
