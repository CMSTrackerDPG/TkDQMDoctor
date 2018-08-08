from certhelper.models import RunInfo
from certhelper.utilities.utilities import get_from_summary, to_weekdayname


class ShiftLeaderReport:
    bad_keyword = "Bad"
    day_keyword = "day"
    num_runs_keyword = "number_of_runs"
    intlum_keyword = "int_lum"
    types = ["Collisions", "Cosmics"]
    recos = ["Prompt", "Express"]
    attributes = [num_runs_keyword, intlum_keyword]

    def __init__(self, runs):
        self.summary = runs.summary()
        self.bad_summary = runs.bad().summary()
        self.summary_per_day = runs.summary_per_day()
        self.bad_summary_per_day = runs.bad().summary_per_day()

    def get_item(self, runtype, reco, bad_only=False, day=None):
        if day:  # for single day
            summary = self.summary_per_day if not bad_only else self.bad_summary_per_day
            item = get_from_summary(summary, runtype, reco, day)
        else:  # for whole week/ all runs
            summary = self.summary if not bad_only else self.bad_summary
            item = get_from_summary(summary, runtype, reco)
        assert len(item) <= 1
        return item[0] if len(item) == 1 else {}

    def number_of_runs(self, runtype, reco, bad_only=False, day=None):
        return self.get_attribute("runs_certified", runtype, reco, bad_only, day)

    def sum_int_lum(self, runtype, reco, bad_only=False, day=None):
        return self.get_attribute("int_luminosity", runtype, reco, bad_only, day)

    def run_numbers(self, runtype, reco, day=None):
        return self.get_attribute("run_numbers", runtype, reco, bad_only=False, day=day)

    def get_attribute(self, attribute, runtype, reco, bad_only=False, day=None,
                      default_value=0):
        return self.get_item(runtype, reco, bad_only, day).get(attribute, default_value)

    def get_active_days_list(self):
        days_list = []
        for item in self.summary_per_day:
            day = item["date"].strftime('%Y-%m-%d')
            if day not in days_list:
                days_list.append(day)
        return days_list

    def get_context(self):
        """
        Returns a dictionary that can be used in a Template

        For example:
        context['slreport'] = ShiftLeaderReport(RunInfo.objects.filter(date="2018-12-31)).get_context()

        and then in the template:

        <h1>Weekly Certification</h1>
        {{ slreport.Collisions.Prompt.number_of_runs }}
        {{ slreport.Bad.Collisions.Express.int_lum }}
        {{ slreport.Cosmics.Prompt.number_of_runs }}
        ...

        <h1>Day by Day notes</h1>
        {% for day in slreport.day %}
            {{ day.date }} {{ day.name|title }}
            {{ day.Collisions.Express.int_lum }}
            {{ day.Bad.number_of_runs }}
        {% endfor %}

        """
        context = self.fill_context()
        context[self.day_keyword] = []

        active_days = self.get_active_days_list()
        for idx, day in enumerate(active_days):
            context[self.day_keyword].append(self.fill_context(day))

        return context

    def build_context_structure(self):
        """
        Builds a dictionary without any values set yet.
        The Values wil be filled by the fill_context method
        """
        bad = self.bad_keyword
        context = {bad: {}}

        for type in self.types:
            context[type] = {}
            context[bad][type] = {}
            for reco in self.recos:
                context[type][reco] = {}
                context[bad][type][reco] = {}
                context[type][reco]["run_numbers"] = {}
                for attr in self.attributes:
                    context[type][reco][attr] = 0
                    context[bad][type][reco][attr] = 0

        return context

    def fill_context(self, day=None):
        """
        returns a dictionary with filled out values

        All/Bad, Collisions/Coscmics, Express/Prompt, number of runs, int luminosity
        """
        context = self.build_context_structure()

        context[self.bad_keyword][self.num_runs_keyword] = 0
        context[self.bad_keyword][self.intlum_keyword] = 0

        for runtype in self.types:
            for reco in self.recos:
                context[runtype][reco] = {
                    self.num_runs_keyword: self.number_of_runs(runtype, reco, day=day),
                    self.intlum_keyword: self.sum_int_lum(runtype, reco, day=day)
                }

                num_runs = self.number_of_runs(runtype, reco, bad_only=True, day=day)
                int_lum = self.sum_int_lum(runtype, reco, bad_only=True, day=day)
                context[self.bad_keyword][runtype][reco] = {
                    self.num_runs_keyword: num_runs,
                    self.intlum_keyword: int_lum
                }
                # TODO TEST THIS
                context[self.bad_keyword][self.num_runs_keyword] += num_runs
                context[self.bad_keyword][self.intlum_keyword] += int_lum

                run_numbers = self.run_numbers(runtype, reco, day=day)
                context[runtype][reco]["run_numbers"] = run_numbers

        if day:
            context["name"] = to_weekdayname(day)
            context["date"] = day
            runs_with_changed_flag = RunInfo.objects.filter(date=day).changed_flags()
            context["number_of_changed_flags"] = len(runs_with_changed_flag)
            context["runs_with_changed_flags"] = ", ".join(
                str(run) for run in runs_with_changed_flag)
        return context


class ShiftLeaderReportBase:
    """
    Base class for the shift leader report
    Just wraps the RunInfoQuerySet filter functions
    """

    def prompt(self):
        return type(self)(self.runs.prompt())

    def express(self):
        return type(self)(self.runs.express())

    def rereco(self):
        return type(self)(self.runs.rereco())

    def collisions(self):
        return type(self)(self.runs.collisions())

    def cosmics(self):
        return type(self)(self.runs.cosmics())

    def bad(self):
        return type(self)(self.runs.bad())

    def good(self):
        return type(self)(self.runs.good())

    def run_numbers(self):
        return self.runs.run_numbers()

    def integrated_luminosity(self):
        return self.runs.integrated_luminosity()

    def total_number(self):
        return self.runs.total_number()

    def flag_changed(self):
        return self.runs.filter_flag_changed()


class ShiftLeaderReportDay(ShiftLeaderReportBase):
    def __init__(self, runs):
        self.runs = runs
        try:
            day = runs[0].date
            self.day_name = to_weekdayname(day)
            self.day_date = day
        except IndexError:
            pass

    def name(self):
        return self.day_name

    def date(self):
        return self.day_date


class NewShiftLeaderReport(ShiftLeaderReportBase):
    def __init__(self, runs):
        self.runs = runs

    def day_by_day(self):
        return [ShiftLeaderReportDay(day) for day in self.runs.per_day()]
