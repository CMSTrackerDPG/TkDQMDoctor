from certhelper.utilities.utilities import get_ascii_table


class SummaryReport:
    """
    SummaryReport used in summary.html.
    Everything is returned per type.
    """

    def __init__(self, runs):
        self.runs = runs
        self.runs_per_type = runs.per_type()

    def reference_runs(self):
        return self.runs.reference_runs()

    def runs_checked_per_type(self):
        runs_checked = []

        for idx, runs_with_specific_type in enumerate(self.runs_per_type):
            column_description = [
                "Run",
                "Reference Run",
                "Number of LS",
                "Int. Luminosity",
                "Pixel",
                "Strip",
                "Tracking",
                "Comment"
            ]

            data = [[
                run.run_number,
                run.reference_run.reference_run,
                run.number_of_ls,
                run.int_luminosity,
                run.pixel,
                run.sistrip,
                run.tracking,
                run.comment
            ] for run in runs_with_specific_type]

            headline = "Type " + str(idx + 1) + ": " + str(
                runs_with_specific_type[0].type)
            table = get_ascii_table(column_description, data)
            runs_checked.append(headline + '\n' + table + '\n')

        return runs_checked

    def tracker_maps_per_type(self):
        tracker_maps = []
        for idx, runs_with_specific_type in enumerate(self.runs_per_type):
            text = "Type {}".format(idx + 1)
            tk_map_exists_runs = runs_with_specific_type.filter(trackermap="Exists")
            if tk_map_exists_runs.exists():
                run_numbers = tk_map_exists_runs.run_numbers()
                joined = " ".join(str(run_number) for run_number in run_numbers)
                text += "\n Exists: {}".format(joined)

            tk_map_missing_runs = runs_with_specific_type.filter(trackermap="Missing")
            if tk_map_missing_runs.exists():
                run_numbers = tk_map_missing_runs.run_numbers()
                joined = " ".join(str(run_number) for run_number in run_numbers)
                text += "\n Missing: {}".format(joined)
            tracker_maps.append(text + "\n")
        return tracker_maps

    def certified_runs_per_type(self):
        certified_run_numbers = []
        for idx, runs_with_specific_type in enumerate(self.runs_per_type):
            text = "Type {}".format(idx + 1)
            good = runs_with_specific_type.good()
            if good.exists():
                run_numbers = good.run_numbers()
                joined = " ".join(str(run_number) for run_number in run_numbers)
                text += "\n Good: {}".format(joined)

            bad = runs_with_specific_type.bad()
            if bad.exists():
                run_numbers = bad.run_numbers()
                joined = " ".join(str(run_number) for run_number in run_numbers)
                text += "\n Bad: {}".format(joined)
            certified_run_numbers.append(text + "\n")
        return certified_run_numbers

    def sum_of_quantities_per_type(self):
        certified_run_numbers = []
        for idx, runs_with_specific_type in enumerate(self.runs_per_type):
            column_description = [
                "Type {}".format(idx + 1),
                "Sum of LS",
                "Sum of int. luminosity"
            ]

            data = []
            good = runs_with_specific_type.good()
            bad = runs_with_specific_type.bad()

            if good.exists():
                data.append(
                    ["Good", good.lumisections(), int(good.integrated_luminosity())])

            if bad.exists():
                data.append(
                    ["Bad", bad.lumisections(), int(bad.integrated_luminosity())])

            table = get_ascii_table(column_description, data)
            certified_run_numbers.append(table)
        return certified_run_numbers
