import requests


class RunRegistryClient:
    """
    Implements a simple client that accesses the RunRegistry through the resthub API

    See:
    https://github.com/valdasraps/resthub
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/DqmRrApi
    """

    DEFAULT_URL = "http://vocms00170:2113"
    ALTERNATIVE_URL = "http://cmsrunregistryapi.cern.ch:2113"

    DEFAULT_NAMESPACE = "runreg_tracker"
    DEFAULT_TABLE = "dataset_lumis"

    def __init__(self, url=DEFAULT_URL):
        self.url = url

    def __get_json_response(self, resource):
        response = requests.get(self.url + resource)
        return response.json()

    def get_query_id(self, query):
        """
        Converts a SQL query string into a query id (qid), that will be used to access
        the RunRegistry.

        GET: /query/{query_id}

        :param query: SQL query string
        :return: query id
        """
        response = requests.post(self.url + "/query?", data=query)
        return response.text

    def execute_query(self, query):
        """
        Executes an arbitrary SQL query

        Limitations:
         - tables referred by namespace.table
         - all tables used must have the unique alias in a query
         - only tables that share the same connection can be used in a query
         - named parameters are supported, i.e. :name
         - by default named parameter is considered of string type
         - named parameter type can be changed with prefix:
           - s__{parameter name} string type, i.e. s__name, s__country
           - n__{parameter name} number type, i.e. n__id, n__voltage
           - d__{parameter name} date type, i.e. d__from, d__to
         - supported functions can be found under /info

        Example:
        >>> client = RunRegistryClient()
        >>> query = "select r.runnumber from runreg_global.runs r " \
                    "where r.run_class_name = 'Collisions15'" \
                    "and r.runnumber > 247070 and r.runnumber < 247081"
        >>> client.execute_query(query)
        {'data': [[247073], [247076], [247077], [247078], [247079]]}

        :param query: SQL query string
        :return: JSON dictionary
        """
        query_id = self.get_query_id(query)
        resource = "/query/" + query_id + "/data"
        return self.__get_json_response(resource)

    def get_table_description(self, namespace=DEFAULT_NAMESPACE, table=DEFAULT_TABLE):
        """
        Table description in JSON

        :param namespace: runreg_{workspace}, e.g. runreg_tracker
        :param table: runs, run_lumis, datasets, dataset_lumis
        :return: json containing the table description
        """
        resource = "/table/{}/{}".format(namespace, table)
        return self.__get_json_response(resource)

    def get_queries(self):
        """
        GET /query/{query_id}

        :return: list of queries
        """
        return self.__get_json_response("/queries")

    def get_query_description(self, query_id):
        """
        GET /query/{query_id}

        :return: json dictionary with query description
        """
        return self.__get_json_response("/query/{}".format(query_id))

    def get_info(self):
        """
        GET /info

        Contains a list of supported functions and the version numbers.

        :return json with general information about the service
        """
        return self.__get_json_response("/info")


class TrackerRunRegistryClient(RunRegistryClient):
    """
    Client to access the Tracker Workspace of the Run Registry

    https://cmswbmoffshift.web.cern.ch/cmswbmoffshift/runregistry_offline/index.jsf
    """

    def __get_runs(self, where_clause):
        query = (
            "select r.run_number, r.run_class_name, r.rda_name, r.rda_state, "
            "r.rda_last_shifter, r.rda_cmp_pixel, r.rda_cmp_strip, "
            "r.rda_cmp_tracking, r.rda_cmp_pixel_cause, r.rda_cmp_strip_cause, "
            "r.rda_cmp_tracking_cause "
            "from runreg_tracker.datasets r "
            "where {} "
            "and r.rda_name != '/Global/Online/ALL'".format(where_clause)
        )

        print(query)

        run_list = self.execute_query(query).get("data")

        keys = [
            "run_number",
            "run_class",
            "dataset",
            "state",
            "shifter",
            "pixel",
            "sistrip",
            "tracking",
            "pixel_lowstat",
            "sistrip_lowstat",
            "tracking_lowstat",
        ]

        run_dict = [dict(zip(keys, run)) for run in run_list]

        for run in run_dict:
            run["pixel_lowstat"] = run["pixel_lowstat"] == "LOW_STATS"
            run["sistrip_lowstat"] = run["sistrip_lowstat"] == "LOW_STATS"
            run["tracking_lowstat"] = run["tracking_lowstat"] == "LOW_STATS"

        return run_dict

    def get_runs_by_range(self, min_run_number, max_run_number):
        """
        Get list of run dictionaries from the Tracker workspace in the Run Registry

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_runs_by_range("323471", "323475")

        :param min_run_number: first run number
        :param max_run_number: last run number
        :return: dictionary containing the queryset
        """

        where_clause = "r.run_number >= '{}' and r.run_number <= '{}'".format(
            min_run_number, max_run_number
        )

        return self.__get_runs(where_clause)

    def get_runs_by_list(self, list_of_run_numbers):
        """
        Get list of run dictionaries from the Tracker workspace in the Run Registry

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_runs_by_list(["323423", "323471", "323397"])

        :param list_of_run_numbers: list of run numbers
        :return: dictionary containing the queryset
        """

        list_of_run_numbers = ["'" + str(item) + "'" for item in list_of_run_numbers]
        list_of_run_numbers = ", ".join(list_of_run_numbers)
        where_clause = "r.run_number in ({})".format(list_of_run_numbers)

        return self.__get_runs(where_clause)
