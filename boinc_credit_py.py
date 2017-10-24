#!/usr/bin/env python
"""
boinc_credit_py - An implementation of boinc_credit (see below link) in Python.
https://github.com/munin-monitoring/contrib/blob/master/plugins/boinc/boinc_credit
"""
# Munin  - Magic Markers
# %# family=auto
# %# capabilities=autoconf nosuggest

import sys

from pymunin import MuninGraph, MuninPlugin, muninMain

from BoincStats import BoincStats

__author__ = "Leonidas Tsekouras"
__version__ = "0.1"
__maintainer__ = "Leonidas Tsekouras"
__status__ = "Development"


class MuninBoincCreditPlugin(MuninPlugin):
    """
    Multigraph Munin Plugin for monitoring Boinc credit.
    """
    plugin_name = "boinc_credit_py"
    isMultigraph = True
    cpid = ""  # todo: get from plugin configuration
    boinc_stats = BoincStats(cpid)

    def __init__(self, argv=(), env=None, debug=False):
        """
        Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)
        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._category = "htc"

        # Total credit graph
        graph = MuninGraph("BOINC Total Credit", self._category,
                           vlabel="Cobblestones",
                           info="Total credit across all projects.",
                           args="--base 1000 --logarithmic")
        graph.addField("credit", "credit", type="GAUGE", draw="LINE2")
        self.appendGraph("total_credit", graph)

        # World Position graph
        graph = MuninGraph("World Position (Total Credit)", self._category,
                           info="Position in BOINC combined World stats based "
                                "on total credit.",
                           args="--lower-limit 0")
        graph.addField("position", "position", type="GAUGE", draw="LINE2")
        self.appendGraph("world_position", graph)

        # RAC graph
        graph = MuninGraph("R.A.C. Combined", self._category,
                           info="Total RAC across all projects.",
                           args="--lower-limit 0")
        graph.addField("rac", "rac", type="GAUGE", draw="LINE2")
        self.appendGraph("rac", graph)

        # Credit per project graph
        graph = MuninGraph("BOINC Total Credit per project", self._category,
                           info="BOINC credit for each project.",
                           vlabel="Cobblestones",
                           args="--base 1000 --logarithmic")
        # Maybe the type could be COUNTER here... Credit shouldn't decrease
        projects = self.boinc_stats.colors
        for project in projects:
            graph.addField(project.lower(), project, colour=projects[project],
                           type="GAUGE", draw="AREASTACK",
                           info="Total Credit for project " + project)
        self.appendGraph("credits_per_proj", graph)

    def retrieveVals(self):
        """Retrieve values for graphs."""
        stats = self.boinc_stats.get_stats()
        self.setGraphVal("total_credit", "credit", stats["total_credit"])
        self.setGraphVal("world_position", "position", stats["world_position"])
        self.setGraphVal("rac", "rac", stats["rac"])
        for proj_credit in stats["projects"]:
            self.setGraphVal("credits_per_proj", proj_credit[0].lower(),
                             proj_credit[1])

    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.
        @return: True if plugin can be  auto-configured, False otherwise.
        """
        # We cannot guess the CPID, so False.
        return False


def main():
    sys.exit(muninMain(MuninBoincCreditPlugin))


if __name__ == "__main__":
    main()
