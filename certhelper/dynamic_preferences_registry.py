from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference, StringPreference, \
    IntegerPreference

# we create some section objects to link related preferences together
shiftleader = Section('shiftleader')


@global_preferences_registry.register
class ShiftLeaderPopupEnabled(BooleanPreference):
    section = shiftleader
    name = 'popup_enabled'
    help_text = "Should the shift leader see a reminding popup every now and then?"
    default = False


@global_preferences_registry.register
class ShiftLeaderPopupText(StringPreference):
    section = shiftleader
    name = 'popup_text'
    help_text = "The popup text that will be displayed every now and then"
    default = 'Please perform the daily checks'


@global_preferences_registry.register
class ShiftLeaderPopupInterval(IntegerPreference):
    section = shiftleader
    name = 'popup_time_period'
    help_text = "The periodic popup time in seconds"
    default = 10800  # 3 hours
