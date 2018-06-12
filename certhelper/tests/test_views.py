from certhelper.tests.custom_asserts import *

pytestmark = pytest.mark.django_db


def test_authentication():
    assert_view_requires_no_login(listruns)
    assert_view_requires_no_login(logout_status)

    assert_view_requires_login(CreateRun)
    assert_view_requires_login(CreateType)
    assert_view_requires_login(ListReferences)
    assert_view_requires_login(summaryView)

    assert_view_requires_staff(ShiftLeaderView)
    assert_view_requires_staff(shiftleader_view)

    # TODO: test the following
    # UpdateRun
    # DeleteRun
    # shiftleader_view
    # hard_deleteview
    # logout_view
    # load_subcategories
    # load_subsubcategories
