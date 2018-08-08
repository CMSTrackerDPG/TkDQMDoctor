import logging
import random

import pytest
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from certhelper.models import RunInfo, ChecklistItemGroup
from tests.credentials import SUPERUSER_USERNAME, PASSWORD, SHIFTER1_USERNAME, \
    SHIFTER2_USERNAME, SHIFTLEADER_USERNAME, EXPERT_USERNAME, ADMIN_USERNAME

pytestmark = pytest.mark.django_db

# Disables Logging when testing
logging.disable(logging.CRITICAL)


@pytest.fixture
def superuser(django_user_model):
    """returns a user with superuser rights"""
    return django_user_model.objects.create_superuser(
        username=SUPERUSER_USERNAME, password=PASSWORD, email=""
    )


@pytest.fixture
def shifter(django_user_model):
    user = django_user_model.objects.create(username=SHIFTER1_USERNAME)
    mixer.blend("certhelper.UserProfile", user=user)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def second_shifter(django_user_model):
    user = django_user_model.objects.create(username=SHIFTER2_USERNAME)
    mixer.blend("certhelper.UserProfile", user=user)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def shiftleader(django_user_model):
    user = django_user_model.objects.create(username=SHIFTLEADER_USERNAME)
    mixer.blend("certhelper.UserProfile", user=user)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def expert(django_user_model):
    user = django_user_model.objects.create(username=EXPERT_USERNAME)
    mixer.blend("certhelper.UserProfile", user=user)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-experts"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def admin(django_user_model):
    user = django_user_model.objects.create(username=ADMIN_USERNAME)
    mixer.blend("certhelper.UserProfile", user=user)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-admins"]}
    user.userprofile.upgrade_user_privilege()
    user.save()
    return user


@pytest.fixture
def firefox():
    """returns a Firefox browser webdriver instance"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    firefox_webdriver = webdriver.Firefox(firefox_options=options)
    yield firefox_webdriver
    firefox_webdriver.quit()


@pytest.fixture
def authenticated_browser(firefox, client, live_server, superuser):
    """returns a firefox browser instance with logged-in superuser"""
    client.login(username=SUPERUSER_USERNAME, password=PASSWORD)
    cookie = client.cookies["sessionid"]

    firefox.get(live_server.url)
    firefox.add_cookie(
        {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
    )
    firefox.refresh()

    return firefox


@pytest.fixture
def wait(firefox):
    return WebDriverWait(firefox, 5)


@pytest.fixture
def some_certified_runs():
    """
    run     type       reco    good
    1       Collisions Express True
    2       Collisions Express True
    3       Collisions Express True
    4       Collisions Express True
    5       Collisions Express False
    6       Collisions Express False
    7       Collisions Express False
    1       Collisions Prompt  True
    3       Collisions Prompt  True
    4       Collisions Prompt  False
    5       Collisions Prompt  True
    6       Collisions Prompt  False
    10      Cosmics    Express True
    11      Cosmics    Express True
    12      Cosmics    Express True
    13      Cosmics    Express True
    14      Cosmics    Express True
    11      Cosmics    Prompt  True
    14      Cosmics    Prompt  False
    """

    collisions_express = mixer.blend(
        "certhelper.Type", runtype="Collisions", reco="Express"
    )
    collisions_prompt = mixer.blend(
        "certhelper.Type", runtype="Collisions", reco="Prompt"
    )
    cosmics_express = mixer.blend("certhelper.Type", runtype="Cosmics", reco="Express")
    cosmics_prompt = mixer.blend("certhelper.Type", runtype="Cosmics", reco="Prompt")

    # == Collisions ==
    # == Express ==
    # == Good ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=1,
        type=collisions_express,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=2,
        type=collisions_express,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=3,
        type=collisions_express,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=4,
        type=collisions_express,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )

    # == Bad ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=5,
        type=collisions_express,
        pixel="Good",
        sistrip="Bad",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=6,
        type=collisions_express,
        pixel="Bad",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=7,
        type=collisions_express,
        pixel="Good",
        sistrip="Good",
        tracking="Bad",
    )

    # == Prompt ==
    # == Good ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=1,
        type=collisions_prompt,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=3,
        type=collisions_prompt,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=5,
        type=collisions_prompt,
        pixel="Good",
        sistrip="Good",
        tracking="Good",
    )

    # == Bad ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=4,
        type=collisions_prompt,
        pixel="Good",
        sistrip="Bad",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=6,
        type=collisions_prompt,
        pixel="Bad",
        sistrip="Good",
        tracking="Good",
    )

    # == Cosmics ==
    # == Express ==
    # == Good ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=10,
        type=cosmics_express,
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=11,
        type=cosmics_express,
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=12,
        type=cosmics_express,
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=13,
        type=cosmics_express,
        sistrip="Good",
        tracking="Good",
    )
    mixer.blend(
        "certhelper.RunInfo",
        run_number=14,
        type=cosmics_express,
        sistrip="Good",
        tracking="Good",
    )

    # == Prompt ==
    # == Good ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=11,
        type=cosmics_prompt,
        sistrip="Good",
        tracking="Good",
    )
    # == Bad ==
    mixer.blend(
        "certhelper.RunInfo",
        run_number=14,
        type=cosmics_prompt,
        sistrip="Bad",
        tracking="Good",
    )

    assert 19 == len(RunInfo.objects.all())
    assert 12 == len(RunInfo.objects.filter(type__runtype="Collisions"))
    assert 7 == len(RunInfo.objects.filter(type__runtype="Cosmics"))

    assert 7 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Express")
    )
    assert 5 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Prompt")
    )

    assert 5 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Express")
    )
    assert 2 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Prompt")
    )

    assert 4 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Express").good()
    )
    assert 3 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Express").bad()
    )
    assert 3 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Prompt").good()
    )
    assert 2 == len(
        RunInfo.objects.filter(type__runtype="Collisions", type__reco="Prompt").bad()
    )

    assert 5 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Express").good()
    )
    assert 0 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Express").bad()
    )
    assert 1 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Prompt").good()
    )
    assert 1 == len(
        RunInfo.objects.filter(type__runtype="Cosmics", type__reco="Prompt").bad()
    )


@pytest.fixture
def some_checklists():
    general = mixer.blend("certhelper.Checklist", identifier="general")
    trackermap = mixer.blend("certhelper.Checklist", identifier="trackermap")
    sistrip = mixer.blend("certhelper.Checklist", identifier="sistrip")
    pixel = mixer.blend("certhelper.Checklist", identifier="pixel")
    tracking = mixer.blend("certhelper.Checklist", identifier="tracking")

    mixer.blend("certhelper.ChecklistItemGroup", checklist=general)
    mixer.blend("certhelper.ChecklistItemGroup", checklist=trackermap)
    mixer.blend("certhelper.ChecklistItemGroup", checklist=sistrip)
    mixer.blend("certhelper.ChecklistItemGroup", checklist=pixel)
    mixer.blend("certhelper.ChecklistItemGroup", checklist=tracking)

    for i in range(random.randint(0, 15)):
        mixer.blend("certhelper.Checklist")
    for i in range(random.randint(0, 15)):
        mixer.blend("certhelper.ChecklistItemGroup")
    for i in range(random.randint(0, 15)):
        mixer.blend("certhelper.ChecklistItem")

    for checklistgroup in ChecklistItemGroup.objects.all():
        for i in range(random.randint(0, 15)):
            mixer.blend("certhelper.ChecklistItem", checklistgroup=checklistgroup)


@pytest.fixture
def runs_for_slr():
    """
    Certified runs used to test the shift leader report
    """
    conditions = [
        ["Cosmics", "Express", 0.1234, 72, "2018-05-14", "Good"],
        ["Collisions", "Prompt", 1.234, 5432, "2018-05-14", "Bad"],  #######
        ["Cosmics", "Prompt", 0, 25, "2018-05-14", "Bad"],  ########
        ["Collisions", "Express", 423.24, 2, "2018-05-15", "Good"],
        ["Collisions", "Express", 0, 72, "2018-05-14", "Good"],
        ["Cosmics", "Express", 0, 12, "2018-05-17", "Good"],
        ["Cosmics", "Express", 0, 72, "2018-05-17", "Bad"],
        ["Cosmics", "Express", 0, 42, "2018-05-14", "Bad"],  #######
        ["Collisions", "Express", 124.123, 72, "2018-05-18", "Good"],
        ["Cosmics", "Express", 0, 1242, "2018-05-14", "Good"],
        ["Cosmics", "Express", 0, 72, "2018-05-20", "Good"],
        ["Collisions", "Express", 999, 142, "2018-05-20", "Good"],
        ["Collisions", "Prompt", 0, 72, "2018-05-20", "Bad"],  #######
        ["Collisions", "Prompt", 123132.32, 4522, "2018-05-20", "Bad"],  #######
        ["Collisions", "Express", 0, 72, "2018-05-20", "Good"],
        ["Collisions", "Express", -1, 71232, "2018-05-14", "Good"],
        ["Cosmics", "Express", 0, 712, "2018-05-17", "Good"],
        ["Collisions", "Express", 5213, 142, "2018-05-14", "Good"],
        ["Collisions", "Express", 154543, 72, "2018-05-18", "Good"],
    ]

    for condition in conditions:
        mixer.blend(
            'certhelper.RunInfo',
            type=mixer.blend('certhelper.Type', runtype=condition[0],
                             reco=condition[1]),
            int_luminosity=condition[2],
            number_of_ls=condition[3],
            date=condition[4],
            pixel=condition[5],
            sistrip=condition[5],
            tracking=condition[5],
        )


@pytest.fixture
def runs_with_three_refs():
    mixer.blend("certhelper.ReferenceRun", reference_run=12)  # unused on purpose
    ref_1 = mixer.blend("certhelper.ReferenceRun", reference_run=1)
    ref_2 = mixer.blend("certhelper.ReferenceRun", reference_run=2)
    ref_3 = mixer.blend("certhelper.ReferenceRun", reference_run=3)
    mixer.blend("certhelper.ReferenceRun")  # unused on purpose

    mixer.blend("certhelper.RunInfo", reference_run=ref_1)
    mixer.blend("certhelper.RunInfo", reference_run=ref_2)
    mixer.blend("certhelper.RunInfo", reference_run=ref_3)
    mixer.blend("certhelper.RunInfo", reference_run=ref_2)
    mixer.blend("certhelper.RunInfo", reference_run=ref_3)
    mixer.blend("certhelper.RunInfo", reference_run=ref_2)
    mixer.blend("certhelper.RunInfo", reference_run=ref_1)
    mixer.blend("certhelper.RunInfo", reference_run=ref_1)
