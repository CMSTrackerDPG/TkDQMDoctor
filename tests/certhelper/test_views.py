import types

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from mixer.backend.django import mixer

from certhelper.views import *

pytestmark = pytest.mark.django_db


def assert_view_requires_no_login(view):
    req = RequestFactory().get("/")
    req.user = AnonymousUser()
    resp = get_view_response(view, req)
    assert resp.status_code == 200 or "login" not in resp.url


def assert_view_requires_login(view):
    req = RequestFactory().get("/")
    req.user = AnonymousUser()

    resp = get_view_response(view, req)
    assert resp.status_code == 302, "should not be anonymous"
    assert "login" in resp.url

    req.user = mixer.blend(User)
    resp = get_view_response(view, req)
    assert resp.status_code == 200


def assert_view_requires_staff(view):
    with pytest.raises(AssertionError):
        assert_view_requires_login(view)

    req = RequestFactory().get("/")
    req.user = mixer.blend(User, is_staff=True)
    resp = get_view_response(view, req)
    assert (
        resp.status_code == 200 or resp.status_code == 302 and "login" not in resp.url
    )


def get_view_response(view, req):
    if isinstance(view, types.FunctionType):
        return view(req)
    return view.as_view()(req)


def test_authentication():
    assert_view_requires_no_login(listruns)
    assert_view_requires_no_login(logout_status)

    assert_view_requires_login(CreateRun)
    assert_view_requires_login(CreateType)
    assert_view_requires_login(ListReferences)
    assert_view_requires_login(summaryView)

    assert_view_requires_staff(ShiftLeaderView)
    assert_view_requires_staff(shiftleader_view)


class TestCreateRun:
    def test_invalid(self):
        the_type = mixer.blend("certhelper.Type")
        the_reference_run = mixer.blend(
            "certhelper.ReferenceRun", runtype=the_type.runtype
        )
        data = {
            "type": the_type.pk,
            "reference_run": the_reference_run.pk,
            "run_number": 123445,
        }

        form = RunInfoForm(data=data)

        assert {} != form.errors
        assert False is form.is_valid()

        req = RequestFactory().post(reverse("certhelper:create"), data=form.data)
        req.user = mixer.blend(User)
        resp = CreateRun.as_view()(req)
        assert 200 == resp.status_code, "should not redirect to success view"

        assert not RunInfo.objects.exists()

    def test_valid(self):
        the_type = mixer.blend("certhelper.Type")
        the_reference_run = mixer.blend(
            "certhelper.ReferenceRun", runtype=the_type.runtype
        )
        data = {
            "type": the_type.pk,
            "reference_run": the_reference_run.pk,
            "run_number": 123445,
            "trackermap": "Exists",
            "number_of_ls": 12,
            "int_luminosity": 42,
            "pixel": "Good",
            "sistrip": "Good",
            "tracking": "Good",
            "comment": "",
            "date": "2018-01-01",
        }

        form = RunInfoForm(data=data)

        assert {} == form.errors
        assert form.is_valid()

        req = RequestFactory().post(reverse("certhelper:create"), data=form.data)
        req.user = mixer.blend(User)
        resp = CreateRun.as_view()(req)
        assert 302 == resp.status_code, "should not redirect to success view"
        assert "/" == resp.url
        assert RunInfo.objects.exists()


class TestUpdateRun:
    # TODO: test if you can only edit your own runs
    def test_anonymous(self):
        run = mixer.blend("certhelper.RunInfo")
        req = RequestFactory().get("/")
        req.user = AnonymousUser()
        resp = UpdateRun.as_view()(req, pk=run.pk)
        assert resp.status_code == 302, "should not be anonymous"
        assert "login" in resp.url

    def test_get(self):
        run = mixer.blend("certhelper.RunInfo")
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        resp = UpdateRun.as_view()(req, pk=run.pk)
        assert resp.status_code == 302, "different user should not have enough rights"
        req.user = run.userid
        resp = UpdateRun.as_view()(req, pk=run.pk)
        assert resp.status_code == 200, "same user should be permitted to edit"
        req.user = mixer.blend(User)
        resp = UpdateRun.as_view()(req, pk=run.pk)
        assert resp.status_code == 302, "should not have enough rights"
        req.user.is_superuser = True
        assert req.user.userprofile.has_shift_leader_rights
        resp = UpdateRun.as_view()(req, pk=run.pk)
        assert resp.status_code == 200, "superuser should have enough rights"

    def test_post(self):
        assert not RunInfo.objects.all().exists()
        run = mixer.blend(
            "certhelper.RunInfo",
            run_number=654321,
            type__runtype="Collisions",
            reference_run__runtype="Collisions",
        )
        assert RunInfo.objects.all().exists()
        data = {
            "type": run.type.pk,
            "reference_run": run.reference_run.pk,
            "run_number": 123445,
            "trackermap": run.trackermap,
            "number_of_ls": 12,
            "int_luminosity": 42,
            "pixel": "Good",
            "sistrip": "Good",
            "tracking": "Good",
            "comment": "",
            "date": run.date,
        }

        form = RunInfoForm(data=data)

        assert {} == form.errors
        assert True is form.is_valid()

        req = RequestFactory().post(
            reverse("certhelper:update", kwargs={"pk": run.pk}), data=form.data
        )
        req.user = run.userid
        view = UpdateRun.as_view()
        resp = view(req, pk=run.pk)
        assert 302 == resp.status_code, "should redirect to success view"
        assert resp.url == "/"
        assert run.run_number != 123445
        run.refresh_from_db()
        assert run.run_number == 123445

    # TODO: test the following
    # DeleteRun
    # hard_deleteview
    # logout_view


class TestListRuns:
    def test_listruns(self):
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        resp = get_view_response(listruns, req)
        assert resp.status_code == 302, "should redirect with today parameter"
        assert "/?date" in resp.url

    def test_filter_parameters(self):
        # TODO test invalid parameter values
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        req.GET = req.GET.copy()
        req.GET["date_range_0"] = "2018-06-13"
        req.GET["date_range_1"] = "2018-06-13"
        req.GET["runs_0"] = "42"
        req.GET["runs_1"] = "1728"
        req.GET["type"] = "3"
        resp = get_view_response(listruns, req)
        assert resp.status_code == 200


class TestSummaryView:
    def test_no_filters(self):
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        resp = get_view_response(listruns, req)
        assert resp.status_code == 302
        assert "/?date=" in resp.url

    def test_with_filters(self):
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        req.GET = req.GET.copy()

        req.GET["date"] = "2018-06-01"
        req.GET["date_range_0"] = "2018-06-13"
        req.GET["date_range_1"] = "2018-06-13"
        req.GET["runs_0"] = "42"
        req.GET["runs_1"] = "1728"
        req.GET["type"] = "3"
        resp = get_view_response(summaryView, req)
        assert resp.status_code == 200

    def test_with_invalid_filters(self):
        req = RequestFactory().get("/")
        req.user = mixer.blend(User)
        req.GET = req.GET.copy()

        req.GET["date"] = "20sfd18-06-01"
        req.GET["date_range_0"] = "201-asasgsa6-13"
        req.GET["date_range_1"] = "BLUME"
        req.GET["runs_0"] = "sadfasdf"
        req.GET["runs_1"] = "ýxkushd"
        req.GET["type"] = " asad /4332re"
        resp = get_view_response(summaryView, req)
        assert resp.status_code == 200


class TestHardDeleteView:
    def test_authentication(self):
        run = mixer.blend("certhelper.RunInfo")
        req = RequestFactory().get("/")
        req.user = AnonymousUser()
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 302
        assert "login" in resp.url

        assert RunInfo.objects.exists()

        req.user = mixer.blend(User, is_staff=False)
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 302
        assert "login" in resp.url

        assert RunInfo.objects.exists()

        req.user = mixer.blend(User, is_staff=True)
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 200

        assert RunInfo.objects.exists()

    def test_hard_delete_post(self):
        run = mixer.blend("certhelper.RunInfo")
        req = RequestFactory().post("/")
        req.user = AnonymousUser()
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 302
        assert "login" in resp.url

        assert RunInfo.objects.exists()

        req.user = mixer.blend(User, is_staff=False)
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 302
        assert "login" in resp.url

        assert RunInfo.objects.exists()

        req.user = mixer.blend(User, is_staff=True)
        resp = hard_deleteview(req, run.run_number)
        assert resp.status_code == 302
        assert "login" not in resp.url

        assert not RunInfo.objects.exists(), "Successfully deleted"

    def test_doesnotexist(self):
        req = RequestFactory().get("/")
        req.user = mixer.blend(User, is_staff=True)
        with pytest.raises(Http404):
            hard_deleteview(req, 42)
