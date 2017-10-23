class BoincStats:
    """A class to get Boinc statistics for a CPID from BAM!"""
    cpid = None
    stats_url = None

    def __init__(self, cpid):
        # Save the CPID
        self.cpid = cpid
        self.stats_url = "https://boincstats.com/en/stats/-1/user/detail/" + \
                         cpid + "/"

    def get_stats(self):
        # todo: missing implementation
        return [self.cpid]
