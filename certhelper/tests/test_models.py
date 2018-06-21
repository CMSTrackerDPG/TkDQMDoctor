import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer

from certhelper.models import RunInfo

pytestmark = pytest.mark.django_db


class TestUserProfile:
    def test_init(self):
        user = mixer.blend(User)
        assert user.userprofile is not None
        assert user.userprofile.user_privilege == 0  # Guest per default
        assert user.userprofile.get_user_privilege_display() == "Guest"  # Guest per default

    def test_upgrade_user_privilege_if_changed(self):
        user = mixer.blend(User)
        userprofile = user.userprofile
        assert userprofile.user_privilege == 0
        userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
        assert userprofile.user_privilege == 0
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 10
        userprofile.extra_data.get("groups").append("cms-tracker-offline-shiftleader")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 20
        userprofile.extra_data.get("groups").append("tkdqmdoctor-experts")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 30
        userprofile.extra_data.get("groups").append("tkdqmdoctor-admins")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 50

    def test_upgrade_to_shiftleader(self):
        user = mixer.blend(User)
        userprofile = user.userprofile
        assert userprofile.user_privilege == 0
        userprofile.extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 20

    def test_downgrade_not_possible(self):
        user = mixer.blend(User)
        userprofile = user.userprofile

        userprofile.extra_data = {"groups": ["tkdqmdoctor-admins"]}
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 50

        userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
        assert userprofile.user_privilege == 50

        user = mixer.blend(User)
        userprofile = user.userprofile
        userprofile.extra_data = {"groups": ["tkdqmdoctor-shiftleaders"]}
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 20

        userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
        assert userprofile.user_privilege == 20

    def test_properties(self):
        user = mixer.blend(User)
        userprofile = user.userprofile
        assert userprofile.user_privilege == 0
        assert userprofile.is_guest
        assert not userprofile.is_shifter
        assert not userprofile.is_shiftleader
        assert not userprofile.is_expert
        assert not userprofile.is_admin
        assert not userprofile.has_shifter_rights
        assert not userprofile.has_shift_leader_rights
        assert user.is_staff is False
        assert user.is_superuser is False

        userprofile.extra_data = {"groups": ["tkdqmdoctor-shifters"]}
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 10
        assert not userprofile.is_guest
        assert userprofile.is_shifter
        assert not userprofile.is_shiftleader
        assert not userprofile.is_expert
        assert not userprofile.is_admin
        assert userprofile.has_shifter_rights
        assert not userprofile.has_shift_leader_rights
        assert user.is_staff is False
        assert user.is_superuser is False

        userprofile.extra_data.get("groups").append("cms-tracker-offline-shiftleader")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 20
        assert not userprofile.is_guest
        assert not userprofile.is_shifter
        assert userprofile.is_shiftleader
        assert not userprofile.is_expert
        assert not userprofile.is_admin
        assert userprofile.has_shifter_rights
        assert userprofile.has_shift_leader_rights
        assert user.is_staff is True
        assert user.is_superuser is False

        userprofile.extra_data.get("groups").append("tkdqmdoctor-experts")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 30
        assert not userprofile.is_guest
        assert not userprofile.is_shifter
        assert not userprofile.is_shiftleader
        assert userprofile.is_expert
        assert not userprofile.is_admin
        assert userprofile.has_shifter_rights
        assert userprofile.has_shift_leader_rights
        assert user.is_staff is True
        assert user.is_superuser is False

        userprofile.extra_data.get("groups").append("tkdqmdoctor-admins")
        userprofile.upgrade_user_privilege()
        assert userprofile.user_privilege == 50
        assert not userprofile.is_guest
        assert not userprofile.is_shifter
        assert not userprofile.is_shiftleader
        assert not userprofile.is_expert
        assert userprofile.is_admin
        assert userprofile.has_shifter_rights
        assert userprofile.has_shift_leader_rights
        assert user.is_staff is True
        assert user.is_superuser is True


class TestRuninfo:
    def test_init(self):
        run = mixer.blend('certhelper.RunInfo', run_number=42, number_of_ls=13, int_luminosity=7138641)
        assert run.__class__.__name__ == "RunInfo"
        assert run.pk == 1
        assert run.run_number == 42
        assert run.number_of_ls == 13
        assert run.int_luminosity == 7138641
        assert run.pixel in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.sistrip in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.pixel in ("Good", "Bad", "Lowstat", "Excluded")
        assert run.trackermap in ("Exists", "Missing")
        assert run.type.reco in ("Express", "Prompt", "reReco")
        assert run.type.runtype in ("Cosmics", "Collisions")

    def test_is_good(self):
        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Cosmics"),
                          sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.is_bad() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          sistrip="Bad")
        assert run.is_good() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Bad")
        assert run.is_good() is False

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          tracking="Bad")
        assert run.is_good() is False
        assert run.is_bad() is True

        run = mixer.blend('certhelper.RunInfo',
                          type=mixer.blend('certhelper.Type', runtype="Collisions"),
                          pixel="Good", sistrip="Good", tracking="Good")
        assert run.is_good() is True
        assert run.is_bad() is False

        assert len(RunInfo.objects.all()) == 7

    def test_delete(self):
        run = mixer.blend('certhelper.RunInfo', run_number=123456)

        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert run.run_number == 123456
        run.delete()
        assert RunInfo.objects.filter(run_number=123456).exists() is False
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.get(run_number=123456).pk == run.pk
        run.restore()
        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True
        run.hard_delete()
        assert RunInfo.objects.filter(run_number=123456).exists() is False
        assert RunInfo.all_objects.filter(run_number=123456).exists() is False
        assert run.run_number == 123456
        run.save()
        assert RunInfo.objects.filter(run_number=123456).exists() is True
        assert RunInfo.all_objects.filter(run_number=123456).exists() is True

    def test_to_string(self):
        run = mixer.blend('certhelper.RunInfo',
                          run_number=123456,
                          type__runtype="Cosmics",
                          type__reco="Express",
                          reference_run__reference_run=654321,
                          reference_run__reco="Prompt",
                          reference_run__runtype="Collisions",
                          )
        assert run.run_number == 123456
        assert run.type.runtype == "Cosmics"
        assert run.type.reco == "Express"
        assert run.reference_run.reference_run == 654321
        assert run.reference_run.reco == "Prompt"
        assert run.reference_run.runtype == "Collisions"

        assert str(run) == "123456, Cosmics Express (ref: 654321, Collisions Prompt)"
        assert "654321 Prompt Collisions" in str(run.reference_run)
        assert "Express Cosmics" in str(run.type)

    def test_validate_unique(self):
        with pytest.raises(ValidationError):
            t = mixer.blend('certhelper.Type')
            ref = mixer.blend('certhelper.ReferenceRun')

            r1 = mixer.blend('certhelper.RunInfo',
                             run_number=123456,
                             type=t,
                             reference_run=ref
                             )

            r2 = mixer.blend('certhelper.RunInfo',
                             run_number=123456,
                             type=t,
                             reference_run=ref
                             )


class TestCategory:
    def test_category_str(self):
        assert str(mixer.blend("certhelper.Category", name="cat1")) == "cat1"
        assert str(mixer.blend("certhelper.SubCategory", name="subcat1")) == "subcat1"
        assert str(mixer.blend("certhelper.SubSubCategory", name="subsubcat1")) == "subsubcat1"
