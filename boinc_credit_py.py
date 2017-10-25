#!/usr/bin/env python
"""
boinc_credit_py - An implementation of boinc_credit (see below link) in Python.
https://github.com/munin-monitoring/contrib/blob/master/plugins/boinc/boinc_credit
"""
# Munin  - Magic Markers
# %# family=auto
# %# capabilities=autoconf nosuggest

import re
import sys

from pymunin import MuninGraph, MuninPlugin, muninMain

from BoincStats import BoincStats

__author__ = "Leonidas Tsekouras"
__version__ = "0.1"
__maintainer__ = "Leonidas Tsekouras"
__status__ = "Development"


def proj_name_to_id(proj_name):
    return (re.sub("[^a-zA-Z]+", "", proj_name)).lower()


class MuninBoincCreditPlugin(MuninPlugin):
    """
    Multigraph Munin Plugin for monitoring Boinc credit.
    """
    plugin_name = "boinc_credit_py"
    isMultigraph = True
    cpid = None
    boinc_stats = None
    project_colors = None

    def __init__(self, argv=(), env=None, debug=False):
        """
        Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)
        """
        MuninPlugin.__init__(self, argv, env, debug)

        # Get CPID from environment
        if self.cpid is None and self.envHasKey("cpid"):
            self.cpid = self.envGet("cpid")
            self.boinc_stats = BoincStats(self.cpid)
            self.project_colors = self.boinc_stats.colors

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
        graph = MuninGraph("BOINC Recent Average Credit", self._category,
                           info="Recent Average Credit across all projects.",
                           vlabel="Cobblestones",
                           args="--lower-limit 0")
        graph.addField("rac", "R.A.C.", type="GAUGE", draw="LINE2")
        self.appendGraph("rac", graph)

        # Credit per project graph
        graph = MuninGraph("BOINC Total Credit per project", self._category,
                           info="BOINC credit for each project.",
                           vlabel="Cobblestones",
                           args="--base 1000")
        # Maybe the type could be COUNTER here... Credit shouldn't decrease

        # Only add to the graph the projects that are active for this user
        # todo: Find a way to not run below line every 5 minutes
        stats = self.boinc_stats.get_stats()
        for project in stats["projects"]:
            # Find color for this project, if it exists
            if project[0] in self.project_colors:
                color = self.project_colors[project[0]]
            else:
                color = None

            graph.addField(proj_name_to_id(project[0]), project[0].lower(),
                           type="GAUGE", draw="AREASTACK", colour=color,
                           info="Total Credit for project " + project[0])
        self.appendGraph("credits_per_proj", graph)

    def retrieveVals(self):
        """Retrieve values for graphs."""
        stats = self.boinc_stats.get_stats()

        self.setGraphVal("total_credit", "credit", stats["total_credit"])
        self.setGraphVal("world_position", "position", stats["world_position"])
        self.setGraphVal("rac", "rac", stats["rac"])
        for project in stats["projects"]:
            self.setGraphVal("credits_per_proj", proj_name_to_id(project[0]),
                             project[1])

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
