"""
Mapping of the 36 pages to be tested.
Each entry contains a description and the relative URL (after the hash #).
"""

PAGES = [
    {"name": "Dashboard", "path": "#home/"},
    {"name": "WiFi Settings", "path": "#wifi/"},
    {"name": "WiFi Radio", "path": "#wifi/radio/"},
    {"name": "WiFi 2.4GHz Details", "path": "#wifi/details/private:2"},
    {"name": "WiFi 5GHz Details", "path": "#wifi/details/private:5"},
    {"name": "WiFi 6GHz Details", "path": "#wifi/details/private:6"},
    {"name": "WAN Parameters", "path": "#wan/"},
    {"name": "LAN Settings", "path": "#lan/"},
    {"name": "Network", "path": "#network/"},
    {"name": "WiFi Scheduling", "path": "#wifi-scheduling/"},
    {"name": "Advanced Settings", "path": "#advanced/"},
    # TODO: Add the remaining 27 pages once the list is provided by the USER.
]
