#!/usr/bin/env python
"""pihole_stats - Munin Plugin to monitor stats of PiHole installation.
"""
# Example config:
# [pihole_stats]
# env.ip 192.168.1.73

# Munin  - Magic Markers
# %# family=auto
# %# capabilities=autoconf nosuggest

import json
import sys
import urllib

from pymunin import MuninGraph, MuninPlugin, muninMain

__author__ = "Leonidas Tsekouras"
__version__ = "0.1"
__maintainer__ = "Leonidas Tsekouras"
__status__ = "Development"


class MuninPiHolePlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring PiHole.
    """
    plugin_name = "pihole_stats"
    isMultigraph = False

    def __init__(self, argv=(), env=None, debug=False):
        """Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)

        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._category = "network"
        self.ip_addr = self.envGet("ip")
        self.pihole_url = "http://" + str(self.envGet("ip")) \
                          + "/admin/api.php?overTimeData10mins"

        graph = MuninGraph("PiHole Domains Over Time", self._category,
                           info="Number of requests.",
                           args="--lower-limit 0 --logarithmic")
        graph.addField("blocked", "blocked", type="GAUGE", draw="LINE2")
        graph.addField("total", "total", type="GAUGE", draw="LINE2")
        self.appendGraph("domains_graph", graph)

    def retrieveVals(self):
        """Retrieve values for graphs."""
        # Get data json
        response = urllib.urlopen(self.pihole_url)
        data = json.loads(response.read())

        # Find last complete 10 minute interval
        time_keys = sorted([key for key in data["domains_over_time"]])
        last_complete_key = time_keys[-2]

        # Use the found key to get the total & blocked request numbers
        total = data["domains_over_time"][last_complete_key]
        blocked = data["ads_over_time"][last_complete_key]

        # Add values to the graph
        self.setGraphVal("domains_graph", "blocked", blocked)
        self.setGraphVal("domains_graph", "total", total)

    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.

        @return: True if plugin can be  auto-configured, False otherwise.

        """
        # False because we can't guess the IP of the PiHole DNS server
        return False


def main():
    sys.exit(muninMain(MuninPiHolePlugin))


if __name__ == "__main__":
    main()
