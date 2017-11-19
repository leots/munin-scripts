#!/usr/bin/env python
"""speedport_entry_2i - Munin Plugin to monitor stats of Speedport Entry 2i
modem/router.
"""
# Example config:
# [speedport_entry_2i]
# env.ip 192.168.1.1
# Munin  - Magic Markers
# %# family=auto
# %# capabilities=autoconf nosuggest

import sys
import urllib
import xml.etree.cElementTree as ET

from pymunin import MuninGraph, MuninPlugin, muninMain

__author__ = "Leonidas Tsekouras"
__version__ = "0.1"
__maintainer__ = "Leonidas Tsekouras"
__status__ = "Development"


class MuninSpeedportPlugin(MuninPlugin):
    """Munin Plugin for monitoring Speedport Entry 2i modem/router.
    """
    plugin_name = "speedport_entry_2i"
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

        # Create the URL for the requests. Normally contains the current
        # timestamp, but that's probably to ignore any browser cache.
        self.xml_url = "http://" + str(self.ip_addr) \
                       + "/common_page/status_info_lua.lua"

        # Create graph
        graph = MuninGraph("Downstream/Upstream", self._category,
                           info="Current downstream & upstream speed in kbps.",
                           args="--lower-limit 0")
        graph.addField("upstream", "upstream", type="GAUGE", draw="LINE2")
        graph.addField("downstream", "downstream", type="GAUGE", draw="LINE2")
        self.appendGraph("down_up_graph", graph)

    def retrieveVals(self):
        """Retrieve values for graphs."""
        # Get XML and find up/downstream values
        response = urllib.urlopen(self.xml_url)
        tree = ET.fromstring(response.read())

        upstream = tree[4][0][5].text
        downstream = tree[4][0][9].text

        # Add values to the graph
        self.setGraphVal("down_up_graph", "upstream", upstream)
        self.setGraphVal("down_up_graph", "downstream", downstream)

    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.

        @return: True if plugin can be  auto-configured, False otherwise.

        """
        # False because we can't guess the IP of the Speedport modem/router
        return False


def main():
    sys.exit(muninMain(MuninSpeedportPlugin))


if __name__ == "__main__":
    main()
