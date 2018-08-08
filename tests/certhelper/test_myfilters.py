from certhelper.templatetags.myfilters import dateoffset, yyyymmdd_to_ddmmyyyy, \
    join_good_runs, join_bad_runs


def test_addclass():
    assert True  # TODO


def test_addplaceholder():
    assert True  # TODO


def test_dateoffset():
    assert dateoffset("2018-01-01", 1) == "2018-01-02"
    assert dateoffset("2018-02-28", 5) == "2018-03-05"
    assert dateoffset("2018-12-31", 1) == "2019-01-01"
    assert dateoffset("2018-01-01", -3) == "2017-12-29"


def test_yyyymmdd_to_ddmmyyyy():
    assert yyyymmdd_to_ddmmyyyy("2018-01-01") == "01-01-2018"
    assert yyyymmdd_to_ddmmyyyy("2018-02-28") == "28-02-2018"
    assert yyyymmdd_to_ddmmyyyy("2018-12-31") == "31-12-2018"

def test_join_good_runs():
    run_numbers = [123, 45, "12"]
    assert '<span class="good-runs">123, 45, 12</span>' == join_good_runs(run_numbers)

def test_join_bad_runs():
    run_numbers = [123, 45, "12"]
    assert '<span class="bad-runs">123, 45, 12</span>' == join_bad_runs(run_numbers)
