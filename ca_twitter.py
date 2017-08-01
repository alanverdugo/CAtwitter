#!/usr/bin/python
"""

 Description:
    This program will crawl the "Contrataciones Abiertas" API which basically 
    is data for contracts made by the Mexico City government.
    The program will tweet the contracts so normal people have a easy, fast 
    and reliable way to know about said contracts.
    More information can be found here:
    http://www.contratosabiertos.cdmx.gob.mx/datos-abiertos

 Usage:
    python ca_twitter.py

 Arguments:


 Author:
    Alan Verdugo (alan@kippel.net)

 Creation date:
    2016-07-31

 Revision history:
    Author:     Date:       Notes:

"""


import json

import logging

# To get the API call results.
import requests


# TODO: Change this to read from config.json
headers = {'content-type': 'application/json'}
home_dir = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(home_dir, "config.json")

# Logging configuration.
log = logging.getLogger("ca_twitter")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
log.setLevel(logging.INFO)


def main():
    try:
        api_response = requests.get(ca_url, headers=headers)
    except Exception as error:
        log.error("Unable to get response from API: {0}".format(error))
        sys.exit(1)

    # The status code should be 200 (success). Catch anything else and handle.
    if api_response.status_code != 200:
        log.error("The response status is: {0}".format(response.status_code))
        sys.exit(1)

    # Validate that we got a non-empty result set.
    try:
        readable_api_response = api_response.json()
    except ValueError:
        log.warning("Empty result set. Request URL: {0}".format(ca_url))
        sys.exit(2)


if __name__ == "__main__":
    get_args(sys.argv[1:])
