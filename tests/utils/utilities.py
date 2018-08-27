import datetime

from mixer.backend.django import mixer


def create_runs(amount, first_run_number, runtype, reco, good=True, date=None):
    if runtype not in ["Collisions", "Cosmics"]:
        raise ValueError("Unknown run type: {}".format(runtype))
    if reco not in ["Express", "Prompt", "reReco"]:
        raise ValueError("Unknown reco type: {}".format(runtype))

    for i in range(first_run_number, first_run_number + amount):
        if good:
            if not date:
                mixer.blend("certhelper.RunInfo",
                            run_number=i,
                            type__runtype=runtype,
                            type__reco=reco,
                            pixel="Good",
                            sistrip="Good",
                            tracking="Good")
            else:
                mixer.blend("certhelper.RunInfo",
                            run_number=i,
                            type__runtype=runtype,
                            type__reco=reco,
                            pixel="Good",
                            sistrip="Good",
                            tracking="Good",
                            date=date)

        else:
            if not date:
                mixer.blend("certhelper.RunInfo",
                            run_number=i,
                            type__runtype=runtype,
                            type__reco=reco,
                            tracking="Bad")
            else:
                mixer.blend("certhelper.RunInfo",
                            run_number=i,
                            type__runtype=runtype,
                            type__reco=reco,
                            tracking="Bad",
                            date=date)



def create_recent_run(run_number=None):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if not run_number:
        mixer.blend("certhelper.RunInfo", date=today)
    else:
        mixer.blend("certhelper.RunInfo", run_number=run_number, date=today)


def print_mixer_code(runs):
    """
    Prints out mixer.blend code to create the objects in the QuerySet
    """
    for run in runs:
        print("mixer.blend('certhelper.RunInfo', "
              "run_number='{}', type={} {}, reference_run={} {}, trackermap='{}', "
              "number_of_ls='{}', int_luminosity='{}', pixel='{}', sistrip='{}', "
              "tracking='{}', date='{}', comment=\"\"\"{}\"\"\")\n".format(
            run.run_number, run.type.runtype, run.type.reco, run.reference_run.runtype, run.reference_run.reco, run.trackermap, run.number_of_ls, run.int_luminosity,
            run.pixel, run.sistrip, run.tracking, run.date, run.comment))

