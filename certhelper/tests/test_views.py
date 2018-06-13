import types

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from mixer.backend.django import mixer

from certhelper.views import *

pytestmark = pytest.mark.django_db


def assert_view_requires_no_login(view):
    req = RequestFactory().get("/")
    req.user = AnonymousUser()
    resp = get_view_response(view, req)
    assert resp.status_code == 200

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
    assert resp.status_code == 200 or resp.status_code == 302 and "login" not in resp.url


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


class TestUpdateRun():
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
        assert resp.status_code == 200

    def test_post(self):
        run = mixer.blend("certhelper.RunInfo", run_number=654321)
        # TODO test model_to_dict

        data = {
            'type': run.type.pk,
            'reference_run': run.reference_run.pk,
            'run_number': 123445,
            'trackermap': run.trackermap,
            'number_of_ls': run.number_of_ls,
            'int_luminosity': run.int_luminosity,
            'pixel': run.pixel,
            'sistrip': run.sistrip,
            'tracking': run.tracking,
            'date': run.date,
        }
        req = RequestFactory().post("/bla/", data=data)
        req.user = mixer.blend(User)
        resp = UpdateRun.as_view()(req, pk=run.pk)
        #assert resp.status_code == 302, "should redirect to success view"
        #assert resp.url == "/"
        assert run.run_number != 123445
        run.refresh_from_db()
        assert run.run_number == 123445

    # TODO: test the following
    # DeleteRun
    # hard_deleteview
    # logout_view
    # load_subcategories
    # load_subsubcategories
