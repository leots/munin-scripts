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


class BoincStats:
    """A class to get Boinc statistics for a CPID from BAM!"""
    cpid = None
    stats_url = None

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
