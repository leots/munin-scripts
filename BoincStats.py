from bs4 import BeautifulSoup
import requests


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
        # Load main stats page
        r = requests.get(self.stats_url)
        soup = BeautifulSoup(r.text, "html.parser")

        stats_table = soup.find("table", id="tblStats")
        total_credit_td = stats_table \
            .find("td", string="Current Credit based on incremental update") \
            .parent \
            .find_all("td")[1]
        # Get number (first line, before <br/>) and remove commas
        total_credit_str = total_credit_td.contents[0].replace(",", "")

        # Parse the number as a float
        total_credit = float(total_credit_str)
        print total_credit

        return {
            total_credit: total_credit
        }
