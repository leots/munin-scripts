#!/usr/bin/env python
"""
boinc_credit_py - An implementation of boinc_credit (see below link) in Python.
https://github.com/munin-monitoring/contrib/blob/master/plugins/boinc/boinc_credit
"""
# Example config:
# [boinc_credit_py]
# env.cpid YOUR_CPID_HERE
#
# Munin  - Magic Markers
# %# family=auto
# %# capabilities=autoconf nosuggest

import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pymunin import MuninGraph, MuninPlugin, muninMain

__author__ = "Leonidas Tsekouras"
__version__ = "0.1"
__maintainer__ = "Leonidas Tsekouras"
__status__ = "Development"


def td_next_to(soup_table, text):
    """
    Given the (BeautifulSoup) BoincStats user overview table and the text on
    the left of the desired field, get the contents of its <td> sibling (which
    contains the value)
    :param soup_table:  BeautifulSoup table
    :param text:        Text to search for
    :return:
    """
    target_td = soup_table \
        .find("td", string=text) \
        .parent \
        .find_all("td")[1]
    return target_td.contents


def rgb(r, g, b):
    return "%02x%02x%02x" % (r, g, b)


def proj_name_to_id(proj_name):
    return (re.sub("[^a-zA-Z]+", "", proj_name)).lower()


class MuninBoincCreditPlugin(MuninPlugin):
    """
    Multigraph Munin Plugin for monitoring Boinc credit.
    """
    plugin_name = "boinc_credit_py"
    isMultigraph = True
    cpid = None
    stats_url = None

    # Define URLs for getting information
    url_base = "https://boincstats.com/en/stats/-1/user/detail/"
    projects_url_postfix = "/projectList"

    # Define project colors (from boinc_credit plugin, which in turn are from
    # http://boinc.netsoft-online.com/e107_plugins/forum/forum_viewtopic.php?3)
    project_colors = {
        "climatepredition.net": rgb(0, 139, 69),
        "Predictor@Home": rgb(135, 206, 235),
        "SETI@home": rgb(65, 105, 225),
        "Einstein@Home": rgb(255, 165, 0),
        "Rosetta@home": rgb(238, 130, 238),
        "PrimeGrid": rgb(205, 197, 191),
        "LHC@home": rgb(255, 127, 80),
        "World Community Grid": rgb(250, 128, 114),
        "BURP": rgb(0, 255, 127),
        "SZTAKI Desktop Grid": rgb(205, 79, 57),
        "uFluids": rgb(0, 0, 0),
        "SIMAP": rgb(143, 188, 143),
        "Folding@Home": rgb(153, 50, 204),
        "MalariaControl": rgb(30, 144, 255),
        "The Lattice Project": rgb(0, 100, 0),
        "Pirates@Home": rgb(127, 255, 0),
        "BBC Climate Change Experiment": rgb(205, 173, 0),
        "Leiden Classical": rgb(140, 34, 34),
        "SETI@home Beta": rgb(152, 245, 255),
        "RALPH@Home": rgb(250, 240, 230),
        "QMC@HOME": rgb(144, 238, 144),
        "XtremLab": rgb(130, 130, 130),
        "HashClash": rgb(255, 105, 180),
        "cpdn seasonal": rgb(255, 255, 255),
        "Chess960@Home Alpha": rgb(165, 42, 42),
        "vtu@home": rgb(255, 0, 0),
        "LHC@home alpha": rgb(205, 133, 63),
        "TANPAKU": rgb(189, 183, 107),
        "other": rgb(255, 193, 37),
        "Rectilinear Crossing Number": rgb(83, 134, 139),
        "Nano-Hive@Home": rgb(193, 205, 193),
        "Spinhenge@home": rgb(255, 240, 245),
        "RieselSieve": rgb(205, 183, 158),
        "Project Neuron": rgb(139, 58, 98),
        "RenderFarm@Home": rgb(210, 105, 30),
        "Docking@Home": rgb(178, 223, 238),
        "proteins@home": rgb(0, 0, 255),
        "DepSpid": rgb(139, 90, 43),
        "ABC@home": rgb(222, 184, 135),
        "BOINC alpha test": rgb(245, 245, 220),
        "WEP-M+2": rgb(0, 250, 154),
        "Zivis Superordenador Ciudadano": rgb(255, 239, 219),
        "SciLINC": rgb(240, 248, 255),
        "APS@Home": rgb(205, 91, 69),
        "PS3GRID": rgb(0, 139, 139),
        "Superlink@Technion": rgb(202, 255, 112),
        "BRaTS@Home": rgb(255, 106, 106),
        "Cosmology@Home": rgb(240, 230, 140),
        "SHA 1 Collision Search": rgb(255, 250, 205)
    }

    # Define text for finding the values in the Overview table
    td_contents = {
        "total_credit": "Current Credit based on incremental update",
        "world_position": "Link to position in BOINC combined World stats "
                          "based on incremental update",
        "rac": "Recent average credit RAC (according to BOINCstats)",
        "user_id": "User ID"
    }

    def get_stats_online(self):
        """
        Get stats from the boincstats.com website.
        :return: Stats object
        """
        # Initialize empty dictionary for stats
        stats = {}

        # Load main stats page
        r = requests.get(self.stats_url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find table with the main stats
        stats_table = soup.find("table", id="tblStats")

        # Find total credit
        td_contents = td_next_to(
            stats_table, self.td_contents["total_credit"])

        # Get total credit number (first line, before <br/>) and remove commas
        total_credit_str = td_contents[0].replace(",", "")

        # Parse the number as a float
        total_credit = float(total_credit_str)
        stats["total_credit"] = total_credit

        # Find world position
        td_contents = td_next_to(stats_table,
                                 self.td_contents["world_position"])
        stats["world_position"] = int(td_contents[0].text.replace(",", ""))

        # Find Recent Average Credit
        td_contents = td_next_to(stats_table, self.td_contents["rac"])
        stats["rac"] = float(td_contents[0].replace(",", ""))

        # Find BAM user id, to find their project list
        td_contents = td_next_to(stats_table, self.td_contents["user_id"])
        user_id = td_contents[0]

        # Load the projects list page
        projects_url = self.url_base + user_id + self.projects_url_postfix
        r = requests.get(projects_url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Add property to keep project stats
        stats["projects"] = []

        # Find the first <tbody>, which is the table we want, and its <tr>'s
        table_rows = soup.find("table", id="tblStats").find_all("tr")[2:]
        for row in table_rows:
            # Get project name and current project credit
            cells = row.find_all("td")
            proj_name = cells[0].text
            proj_credit = float(cells[1].text.replace(",", ""))

            stats["projects"].append((proj_name, proj_credit))

        return stats

    def get_stats(self):
        """
        Get BOINC stats for the saved CPID. Uses state to save previous values
        and prevent requests to boincstats.com more than once per hour.
        :return: Stats for the retrieveVals method
        """
        # Try to restore the projects list from state
        state = self.restoreState()

        # If no previous state is found or the data is old, get stats again
        if state is None \
                or (datetime.now() - state["time"]).total_seconds() > 60 * 60:
            stats = self.get_stats_online()
            curr_time = datetime.now()

            # Save the stats together with their timestamp
            state = {
                "stats": stats,
                "time": curr_time
            }
            self.saveState(state)
        return state["stats"]

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

        # Create stats URL
        self.stats_url = self.url_base + self.cpid

        # Set Munin graphs category
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
        for project in self.get_stats()["projects"]:
            project_name = project[0]

            # Find color for this project, if it exists
            if project_name in self.project_colors:
                color = self.project_colors[project_name]
            else:
                color = None

            graph.addField(proj_name_to_id(project_name), project_name.lower(),
                           type="GAUGE", draw="AREASTACK", colour=color,
                           info="Total Credit for project " + project_name)
        self.appendGraph("credits_per_proj", graph)

    def retrieveVals(self):
        """Retrieve values for graphs."""
        stats = self.get_stats()

        self.setGraphVal("total_credit", "credit", stats["total_credit"])
        self.setGraphVal("world_position", "position", stats["world_position"])
        self.setGraphVal("rac", "rac", stats["rac"])
        for project in stats["projects"]:
            self.setGraphVal("credits_per_proj", proj_name_to_id(project[0]),
                             project[1])

    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.
        @return: True if plugin can be auto-configured, False otherwise.
        """
        # We cannot guess the CPID, so False.
        return False


def main():
    sys.exit(muninMain(MuninBoincCreditPlugin))


if __name__ == "__main__":
    main()
