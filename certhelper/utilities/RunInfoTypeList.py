from terminaltables import AsciiTable


class RunInfoTypeList:
    def __init__(self, runinfo_type, count):
        self.type = runinfo_type  # runs[0].type if isinstance(runs, list) else runs.type # the Type itself
        self.type_count = count
        self.runs = []  # all runs of that particular type
        self.certified_dict = {}  # Good or Bad
        self.tk_dict = {}  # Dictionary of TrackerMaps, either 'Missing' or 'Exists'
        self.sums_dict = {}

        # self.add_runs(runs) if isinstance(runs, list) else self.add_run(runs)

    def add_run(self, run):
        assert run.type == self.type  # We only want runs of the same type

        self.runs.append([
            run.run_number,
            run.reference_run.reference_run,
            run.number_of_ls,
            run.int_luminosity,
            run.pixel,
            run.sistrip,
            run.tracking,
            run.comment
        ])

        if run.trackermap not in self.tk_dict:
            self.tk_dict[run.trackermap] = []
        self.tk_dict[run.trackermap].append(run.run_number)

        good_bad_key = 'Good' if run.is_good else 'Bad'
        if good_bad_key not in self.certified_dict:
            self.certified_dict[good_bad_key] = []
            self.sums_dict[good_bad_key] = {'ls': 0, 'int_lum': 0}

        self.certified_dict[good_bad_key].append(run.run_number)
        self.sums_dict[good_bad_key]['ls'] += run.number_of_ls
        self.sums_dict[good_bad_key]['int_lum'] += run.int_luminosity

    def add_runs(self, runs):
        for run in runs:
            self.add_run(run)

    @staticmethod
    def get_ascii_table(column_description, data):
        table = AsciiTable([column_description] + data)
        table.inner_row_border = True
        return table.table

    def get_runinfo_ascii_table(self):
        column_description = ["Run", "Reference Run", "Number of LS",
                              "Int. Luminosity", "Pixel", "Strip",
                              "Tracking", "Comment"]
        headline = "Type " + str(self.type_count) + ": " + str(self.type)
        table = self.get_ascii_table(column_description, self.runs)
        return headline + '\n' + table + '\n'

    def get_sums_ascii_table(self):
        column_description = ["Type " + str(self.type_count), "Sum of LS", "Sum of int. luminosity"]
        data = []
        for good_bad_key, columns in self.sums_dict.items():
            line = [good_bad_key, int(columns['ls']), int(columns['int_lum'])]
            data.append(line)
        return self.get_ascii_table(column_description, data)

    def get_tracker_maps_info(self):
        out = "Type " + str(self.type_count) + '\n'
        for key, list in self.tk_dict.items():
            out += " " + str(key) + ": "
            for item in list:
                out += str(item) + " "
            out += '\n'
        return out

    def get_certified_runs_info(self):
        out = "Type " + str(self.type_count) + '\n'
        for key, list in self.certified_dict.items():
            out += " " + str(key) + ": "
            for item in list:
                out += str(item) + " "
            out += '\n'
        return out
