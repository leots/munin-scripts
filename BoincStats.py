from bs4 import BeautifulSoup
import requests


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
    return "#%02x%02x%02x" % (r, g, b)


class BoincStats:
    """A class to get Boinc statistics for a CPID from BAM!"""
    cpid = None
    stats_url = None

    # Define project colors (from boinc_credit plugin, which in turn are from
    # http://boinc.netsoft-online.com/e107_plugins/forum/forum_viewtopic.php?3)
    colors = {
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
        "rac": "Recent average credit RAC (according to BOINCstats)"
    }

    def __init__(self, cpid):
        # Save the CPID
        self.cpid = cpid
        self.stats_url = "https://boincstats.com/en/stats/-1/user/detail/" + \
                         cpid + "/"

    def get_stats(self):
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

        return stats
