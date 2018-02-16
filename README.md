# munin-scripts
Munin scripts that I have created or modified, including BOINC credit & PiHole blocked ads monitoring.

| Plugin | Description |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **boinc_credit_py** | Monitors BOINC credit for a user. Has graphs for RAC, Total Credit, Total Credit per Project and World Position. I created this because [this boinc_credit plugin](https://github.com/munin-monitoring/contrib/blob/master/plugins/boinc/boinc_credit) didn't work. |
| **pihole_stats** | Monitors blocked & total requests of a [PiHole](https://pi-hole.net/) installation. This re-creates PiHole's "Queries over last 24 hours" graph, but over longer timespans as well, due to Munin's nature. [This](https://github.com/Rauks/MuninPiholePlugins) plugin is better though. |
| **reddit_karma_** | Modification of https://github.com/munin-monitoring/contrib/tree/master/plugins/reddit_karma that adds custom user agent to prevent Reddit error 429. |
| **speedport_entry_2i_** | Monitors the upload/download speed of the ADSL or VDSL link for the Speedport Entry 2i modem/router. |
