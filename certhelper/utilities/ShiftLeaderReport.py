"""
Number of runs certified:
Collisions: X in Stream-Express (int lumi), Y in Prompt-Reco (int lumi)
Cosmics: X in Stream Express, Y in Prompt Reco
Total number of BAD runs = X (Int. Lumi) (see next slide for details)
Number of changed flags from Express to Prompt= X

slr.collisions.streamexpress.count
slr.collisions.streamexpress.intlumi

slr.collisions.promptreco.count
slr.collisions.promptreco.intlumi

"""


class ShiftLeaderReport:
    """
    contains information needed for
    the weekly certification of the shiftleader
    """

    def __init__(self) -> None:
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.days = []
        for day in weekdays:
            self.days.append(_ShiftLeaderReportDay(day))

    def update(self, runs):
        # TODO increment count and int lumi for every run in runs
        pass

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        text = ""
        for day in self.days:
            text += "\n" + str(day.name) + ":" + day.__str__() + "\n"
        return text


class _ShiftLeaderReportDay:
    def __init__(self, name) -> None:
        self.name = name
        self.cosmics = _ShiftLeaderReportRunType()
        self.collisions = _ShiftLeaderReportRunType()

    def update(self, run):
        # TODO increment count and int lumi
        pass

    def __str__(self) -> str:
        return "\n cosmics: " + self.cosmics.__str__() + "\n collisions " + self.collisions.__str__()


class _ShiftLeaderReportRunType:
    """Cosmics or Collisions"""

    def __init__(self) -> None:
        self.streamexpress = _ShiftLeaderReportRecoType()
        self.promptreco = _ShiftLeaderReportRecoType()

    def update(self, run):
        # TODO increment count and int lumi
        pass

    def __str__(self) -> str:
        return "\n\tstreamexpress: " + self.streamexpress.__str__() + "\n\t promptreco " + self.promptreco.__str__()


class _ShiftLeaderReportRecoType:
    """Express, Prompt, or reReco"""

    def __str__(self):
        return "\n\t\tcount: " + self.count.__str__() + "\n\t\tint lumni: " + self.intlumi.__str__()

    def update(self, run):
        # TODO increment count and int lumi
        pass

    def __init__(self) -> None:
        self.count = 0
        self.intlumi = 0
