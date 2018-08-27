import logging
import random

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from certhelper.models import RunInfo, ChecklistItemGroup, ReferenceRun, Type
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
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.update_privilege()
    user.save()
    return user


@pytest.fixture
def second_shifter(django_user_model):
    user = django_user_model.objects.create(username=SHIFTER2_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
    user.userprofile.update_privilege()
    user.save()
    return user


@pytest.fixture
def shiftleader(django_user_model):
    user = django_user_model.objects.create(username=SHIFTLEADER_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
    user.userprofile.update_privilege()
    user.save()
    return user


@pytest.fixture
def expert(django_user_model):
    user = django_user_model.objects.create(username=EXPERT_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-experts"]}
    user.userprofile.update_privilege()
    user.save()
    return user


@pytest.fixture
def admin(django_user_model):
    user = django_user_model.objects.create(username=ADMIN_USERNAME)
    user.set_password(PASSWORD)
    user.userprofile.extra_data = {"groups": ["tkdqmdoctor-admins"]}
    user.userprofile.update_privilege()
    user.save()
    return user


@pytest.fixture
def firefox():
    """returns a Firefox browser webdriver instance"""
    options = webdriver.FirefoxOptions()
    options.set_preference('intl.accept_languages', 'en,en_US')
    options.add_argument("--headless")
    firefox_webdriver = webdriver.Firefox(firefox_options=options)
    yield firefox_webdriver
    firefox_webdriver.quit()


@pytest.fixture
def website(firefox, live_server):
    """
    Firefox instance with
    :return:
    """
    firefox.get('%s' % live_server.url)
    return firefox


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
    return WebDriverWait(firefox, 10)


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
def shiftleader_checklist():
    checklist = mixer.blend("certhelper.Checklist", identifier="shiftleader")

    mixer.blend("certhelper.ChecklistItemGroup", checklist=checklist)

    for checklistgroup in ChecklistItemGroup.objects.all():
        for i in range(random.randint(0, 15)):
            mixer.blend("certhelper.ChecklistItem", checklistgroup=checklistgroup)

    mixer.blend("certhelper.ChecklistItem", checklistgroup=checklistgroup,
                text="Make sure to do this and that.")


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
def runs_for_summary_report(legitimate_types, legitimate_reference_runs):
    """
    Certified runs for the current day.
    Used to test the summary report.

    All runs will be assigned to the first User that exists.

    Code was partially generated via print_mixer_code() helper in utilities.py
    """
    types = Type.objects.all()
    t1 = types.filter(runtype="Collisions", reco="Express")[0]
    t2 = types.filter(runtype="Collisions", reco="Prompt")[0]
    t3 = types.filter(runtype="Cosmics", reco="Express")[0]
    t4 = types.filter(runtype="Cosmics", reco="Prompt")[0]

    ref_runs = ReferenceRun.objects.all()
    r1 = ref_runs.filter(runtype="Collisions", reco="Express")[0]
    r2 = ref_runs.filter(runtype="Collisions", reco="Prompt")[0]
    r3 = ref_runs.filter(runtype="Cosmics", reco="Express")[0]
    r4 = ref_runs.filter(runtype="Cosmics", reco="Prompt")[0]

    today = timezone.now().date

    user = User.objects.first()

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300024', type=t4,
                reference_run=r4,
                trackermap='Missing', number_of_ls='372', int_luminosity='0.00',
                pixel='Lowstat', sistrip='Lowstat', tracking='Excluded',
                date=today, comment="""Water specific forget carry week. Likely 
                friend claim marriage. White long design. Drop daughter free free 
                analysis hang what run. Hospital administration one while the call.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300023', type=t3,
                reference_run=r3,
                trackermap='Exists', number_of_ls='207', int_luminosity='0.00',
                pixel='Good', sistrip='Good', tracking='Bad', date=today,
                comment="""Her arrive course management training probably anyone.
    Thank cut right manage enough state lose.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300022', type=t2,
                reference_run=r2,
                trackermap='Missing', number_of_ls='74', int_luminosity='874.62',
                pixel='Excluded', sistrip='Excluded', tracking='Lowstat',
                date=today, comment="""After weight institution whose produce. End 
                away finish anything voice. Turn worker success rather argue. Animal 
                right music material. Development clear suddenly bank send central 
                wall.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300021', type=t3,
                reference_run=r3,
                trackermap='Missing', number_of_ls='367', int_luminosity='0.00',
                pixel='Good', sistrip='Bad', tracking='Excluded', date=today,
                comment="""Still a usually member quite many cause. Summer now finish 
                may anything. Best hang light spend happen. Accept idea if should 
                possible ball official.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300020', type=t2,
                reference_run=r2,
                trackermap='Exists', number_of_ls='793', int_luminosity='572.98',
                pixel='Excluded', sistrip='Lowstat', tracking='Bad', date=today,
                comment="""Part by fight such policy candidate cold. Happy career 
                hope who. 
                
                Apply around seem win dog. Walk shot far record decade 
                message trouble.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300019', type=t2,
                reference_run=r2,
                trackermap='Missing', number_of_ls='520', int_luminosity='433.99',
                pixel='Excluded', sistrip='Good', tracking='Excluded',
                date=today,
                comment="""Nor particular them win share fire agree. Job kind offer 
                war lawyer couple card. Young degree go thus whether including away 
                on.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300018', type=t1,
                reference_run=r1,
                trackermap='Exists', number_of_ls='242', int_luminosity='983.49',
                pixel='Excluded', sistrip='Lowstat', tracking='Bad', date=today,
                comment="""Attack strategy raise smile and. West but alone position 
                ago finish change. Another message computer blood provide else 
                hard.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300017', type=t4,
                reference_run=r4,
                trackermap='Missing', number_of_ls='142', int_luminosity='0.00',
                pixel='Excluded', sistrip='Good', tracking='Bad', date=today,
                comment="""Employee hard hard cost near enter recent. Remember plan 
                hang.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300016', type=t2,
                reference_run=r2,
                trackermap='Exists', number_of_ls='188', int_luminosity='391.13',
                pixel='Excluded', sistrip='Good', tracking='Bad', date=today,
                comment="""Why before work contain these indicate seem. None clear 
                pass near minute once. Surface floor focus car number high still. 
                Western trial collection evidence prepare.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300015', type=t2,
                reference_run=r2,
                trackermap='Missing', number_of_ls='265', int_luminosity='432.73',
                pixel='Lowstat', sistrip='Lowstat', tracking='Lowstat',
                date=today,
                comment="""Better private while allow example style. Activity along 
                me effort. Exactly thing commercial hang. Course shake red son source 
                anything.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300014', type=t2,
                reference_run=r2,
                trackermap='Exists', number_of_ls='164', int_luminosity='836.49',
                pixel='Excluded', sistrip='Good', tracking='Excluded',
                date=today, comment="""Might surface line shoulder fund institution. 
                Factor pretty or sign benefit ten. Stock study nation bill. Use image 
                kitchen establish explain eye north still. Anyone news fight huge 
                region.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300013', type=t2,
                reference_run=r2,
                trackermap='Missing', number_of_ls='642', int_luminosity='138.83',
                pixel='Good', sistrip='Lowstat', tracking='Excluded', date=today,
                comment="""Bill suggest success new citizen. Clear apply already rich 
                cultural mouth support. Parent their case some win your news. Garden 
                wear body into character. Age security including later involve.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300012', type=t4,
                reference_run=r4,
                trackermap='Exists', number_of_ls='365', int_luminosity='0.00',
                pixel='Bad', sistrip='Bad', tracking='Bad', date=today,
                comment="""Care agree might TV paper response. Future support 
                certainly follow thousand network. Positive cell raise no property 
                science. Economic suffer market trade politics region huge.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300011', type=t1,
                reference_run=r1,
                trackermap='Missing', number_of_ls='826', int_luminosity='621.59',
                pixel='Excluded', sistrip='Lowstat', tracking='Bad', date=today,
                comment="""Serious character against water. With customer product 
                different. Understand heart civil main sit. Best set baby. 
                Traditional person picture create love maybe. Another his compare 
                gas.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300010', type=t1,
                reference_run=r1,
                trackermap='Missing', number_of_ls='378', int_luminosity='786.43',
                pixel='Excluded', sistrip='Bad', tracking='Excluded', date=today,
                comment="""Contain many the into television. Finally age little 
                treat. Note PM mention how oh assume wrong. Inside listen health. Off 
                degree how economy scientist.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300009', type=t3,
                reference_run=r3,
                trackermap='Exists', number_of_ls='134', int_luminosity='0.00',
                pixel='Lowstat', sistrip='Good', tracking='Lowstat', date=today,
                comment="""Turn drug science practice. Drop four budget section. Into 
                draw more rock create pretty democratic. Really clear determine 
                agreement foreign already him.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300008', type=t4,
                reference_run=r4,
                trackermap='Missing', number_of_ls='356', int_luminosity='0.00',
                pixel='Lowstat', sistrip='Bad', tracking='Good', date=today,
                comment="""Try billion collection lose. Site near thank class yard 
                major. Test anyone much either exactly candidate east. Hit force oh 
                professional network wide during fear. Pick figure young 
                television.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300007', type=t4,
                reference_run=r4,
                trackermap='Missing', number_of_ls='341', int_luminosity='0.00',
                pixel='Lowstat', sistrip='Lowstat', tracking='Lowstat',
                date=today,
                comment="""Yard central myself leg sit. Consumer remember fund 
                control then. Even near see girl hit season.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300006', type=t2,
                reference_run=r2,
                trackermap='Missing', number_of_ls='399', int_luminosity='954.85',
                pixel='Excluded', sistrip='Excluded', tracking='Bad', date=today,
                comment="""Training adult impact treatment die military. Glass cost 
                experience various rather anything human. Either gas area may and 
                any.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300005', type=t1,
                reference_run=r1,
                trackermap='Exists', number_of_ls='981', int_luminosity='510.75',
                pixel='Good', sistrip='Excluded', tracking='Bad', date=today,
                comment="""Enter quality material once rule with bill wind. Far whole 
                give run. Government authority many wish sport.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300004', type=t3,
                reference_run=r3,
                trackermap='Missing', number_of_ls='441', int_luminosity='0.00',
                pixel='Excluded', sistrip='Bad', tracking='Bad', date=today,
                comment="""Notice in affect information value carry. Great success 
                which on. Nation join doctor event. Actually local economy positive. 
                Left woman effort technology reality. Military you it.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300003', type=t3,
                reference_run=r3,
                trackermap='Missing', number_of_ls='574', int_luminosity='0.00',
                pixel='Lowstat', sistrip='Lowstat', tracking='Good', date=today,
                comment="""Ball west movie pain enough. Child tonight guy hotel 
                knowledge. Of everything past language heavy general. Goal option 
                probably prevent. Wonder general difference design test.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300002', type=t2,
                reference_run=r2,
                trackermap='Exists', number_of_ls='873', int_luminosity='273.88',
                pixel='Good', sistrip='Excluded', tracking='Bad', date=today,
                comment="""Important front more because nation check. Shoot accept 
                seem detail stand under. Poor shoot next admit close conference. Put 
                research watch mind.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300001', type=t2,
                reference_run=r2,
                trackermap='Exists', number_of_ls='834', int_luminosity='840.18',
                pixel='Good', sistrip='Excluded', tracking='Lowstat', date=today,
                comment="""Vote kind rule loss dark course. Across difficult people shoot.
    Thought real yeah improve. Explain media book yes business east.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300001', type=t1,
                reference_run=r1,
                trackermap='Exists', number_of_ls='997', int_luminosity='632.57',
                pixel='Bad', sistrip='Excluded', tracking='Excluded', date=today,
                comment="""Develop should across truth prevent single. Thus this much 
                method child. Population impact accept black drop say. Game thought 
                senior.""")

    mixer.blend('certhelper.RunInfo', userid=user, run_number='300000', type=t4,
                reference_run=r4,
                trackermap='Exists', number_of_ls='856', int_luminosity='0.00',
                pixel='Good', sistrip='Lowstat', tracking='Bad', date=today,
                comment="""Notice this resource center. Interest remain throughout 
                condition contain save problem. Town treatment magazine environmental 
                report all rule.""")


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


@pytest.fixture
def legitimate_reference_runs():
    """
    Reference runs as they might be used in production
    """
    mixer.blend("certhelper.ReferenceRun",
                reference_run=300100,
                reco="Express",
                runtype="Collisions",
                bfield="3.8 T",
                beamtype="Proton-Proton",
                beamenergy="13 TeV",
                dataset="/StreamExpress/Run2018A-Express-v1/DQMIO")

    mixer.blend("certhelper.ReferenceRun",
                reference_run=300101,
                reco="Express",
                runtype="Collisions",
                bfield="3.8 T",
                beamtype="Proton-Proton",
                beamenergy="13 TeV",
                dataset="/StreamExpress/Run2018A-Express-v1/DQMIO")

    mixer.blend("certhelper.ReferenceRun",
                reference_run=300150,
                reco="Prompt",
                runtype="Collisions",
                bfield="3.8 T",
                beamtype="Proton-Proton",
                beamenergy="13 TeV",
                dataset="/ZeroBias/Run2018D-PromptReco-v2/DQMIO")

    mixer.blend("certhelper.ReferenceRun",
                reference_run=300200,
                reco="Express",
                runtype="Cosmics",
                bfield="3.8 T",
                beamtype="Cosmics",
                beamenergy="Cosmics",
                dataset="/StreamExpressCosmics/Run2018D-Express-v1/DQMIO")

    mixer.blend("certhelper.ReferenceRun",
                reference_run=300250,
                reco="Prompt",
                runtype="Cosmics",
                bfield="3.8 T",
                beamtype="Cosmics",
                beamenergy="Cosmics",
                dataset="/Cosmics/Run2018D-PromptReco-v2/DQMIO")


@pytest.fixture
def legitimate_types():
    """
    Types as they might be used in production
    """
    mixer.blend("certhelper.Type",
                reco="Express",
                runtype="Collisions",
                bfield="3.8 T",
                beamtype="Proton-Proton",
                beamenergy="13 TeV",
                dataset="/StreamExpress/Run2018A-Express-v1/DQMIO")

    mixer.blend("certhelper.Type",
                reco="Prompt",
                runtype="Collisions",
                bfield="3.8 T",
                beamtype="Proton-Proton",
                beamenergy="13 TeV",
                dataset="/ZeroBias/Run2018D-PromptReco-v2/DQMIO")

    mixer.blend("certhelper.Type",
                reco="Express",
                runtype="Cosmics",
                bfield="3.8 T",
                beamtype="Cosmics",
                beamenergy="Cosmics",
                dataset="/StreamExpressCosmics/Run2018D-Express-v1/DQMIO")

    mixer.blend("certhelper.Type",
                reco="Prompt",
                runtype="Cosmics",
                bfield="3.8 T",
                beamtype="Cosmics",
                beamenergy="Cosmics",
                dataset="/Cosmics/Run2018D-PromptReco-v2/DQMIO")
