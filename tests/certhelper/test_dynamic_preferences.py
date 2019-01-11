from dynamic_preferences.registries import global_preferences_registry

import pytest

pytestmark = pytest.mark.django_db

# We instantiate a manager for our global preferences
global_preferences = global_preferences_registry.manager()


# now, we can use it to retrieve our preferences
# the lookup for a preference has the following form: <section>__<name>
class TestGlobalPreferences:
    def test_global_preferences(self):
        assert global_preferences["shiftleader__popup_enabled"] is False
        assert (
            global_preferences["shiftleader__popup_text"]
            == "Please perform the daily checks"
        )
        assert global_preferences["shiftleader__popup_time_period"] == 10800
