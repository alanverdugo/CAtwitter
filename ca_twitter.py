#!/usr/bin/python
"""
 Description:
    This program will crawl the "Contrataciones Abiertas" API which basically 
    is data for contracts made by the Mexico City government.
    The program will tweet the contracts so normal people have a easy, fast 
    and reliable way to know about said contracts.

 References:
    Contracts main pages, (in Spanish):
    http://www.contratosabiertos.cdmx.gob.mx/datos-abiertos
    http://www.contratosabiertos.cdmx.gob.mx/contratos

    Open Contracting standard, (in Spanish):
    http://standard.open-contracting.org/latest/es/schema/reference/

    Open Contracting standard, (in English):
    http://standard.open-contracting.org/latest/en/schema/reference/

    Mexico City Open Contracts FAQ (In Spanish):
    http://www.contratosabiertos.cdmx.gob.mx/glosario

    Catalogos y elementos del Estandar de Contrataciones Abiertas (In Spanish),
    (Basically a data dictionary for the JSON responses):
    http://www.contratosabiertos.cdmx.gob.mx/archivos/CatalogosElementosEstandarContratacionesAbiertas-CDMX.pdf

    License, terms and propper usage of the API (In Spanish):
    http://www.contratosabiertos.cdmx.gob.mx/privacidad

    Fancy PDF explaining the whole idea (In Spanish and English):
    http://www.contratosabiertos.cdmx.gob.mx/archivos/CuadernilloContratacionesAbiertasEnero2017.pdf


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

# To read the configuration and parse API responses.
import json

# Handle logging.
import logging

# To get the API call results.
import requests

# Twitter module.
import twitter

# Environmental functionality.
import os

# Environmental functionality.
import sys

# To compare update timestamps.
import datetime


# The path were this program and the configuration file reside.
home_dir = os.path.dirname(os.path.abspath(__file__))

# The file were settings are specified.
config_file = os.path.join(home_dir, "config.json")

# Logging configuration.
log = logging.getLogger("ca_twitter")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
log.setLevel(logging.INFO)


def tweet(buyer, tender, description, amount, URL):
    '''
        Refer to:
        https://dev.twitter.com/resources/twitter-libraries
        https://dev.twitter.com/oauth/overview
        https://dev.twitter.com/oauth/overview/application-owner-access-tokens
        https://dev.twitter.com/oauth/overview/single-user
        https://pastebin.com/WMEh802V

        Example Teet:
        "Secretaria de finanzas contrato a Focus On Services S.A. de C.V. por 
        200 COMPUTADORAS PORTATILES Y 872 PC ESCRITORIO a 767,465.28 
        http://innovacion.finanzas.df.gob.mx/ocpsefin/INTERFASE2/GRP/OCDS/ARCHIVOS/contrato_ca_001_2016_20160616_125555.pdf"
        
        http://www.contratosabiertos.cdmx.gob.mx/contrato/OCDS-87SD3T-AD-SF-DRM-066-2015

        <buyer> contrato a <tender> por <description> a <amount> <URL>
    '''

    # Authenticate in Twitter.
    try:
        twitter_auth = twitter.OAuth(TWITTER_TOKEN, TWITTER_TOKEN_KEY, 
            TWITTER_CON_SEC, TWITTER_CON_SEC_KEY)
        twit = twitter.Twitter(auth=twitter_auth)
    except Exception as exception:
        log.error("Unable to authenticate to Twitter API. Exception: "\
            "{0}".format(exception))
        sys.exit(1)
    else:
        log.info("Successfully authenticated in Twitter.")

    try:
        tweet = "El contrato {0} fue creado por {1} con {2} presupuestados "\
            "a {3}".format()
        twit.statuses.update(status=tweet)
    except Exception as exception:
        log.error("Unable to tweet. Exception: {0}". format(exception))
    else:
        log.info("Contract successfully tweeted.")


def get_lastest_tweet_timestamp():
    '''
        This function will search and return the timestamp when the newest 
        tweet was created. Using this timestamp we will be able to know which 
        contracts are newer than that, which obviously will be the contracts 
        that we have not tweeted yet.
        https://dev.twitter.com/rest/reference/get/search/tweets
    '''
    pass


def read_config():
    '''
        Read settings from config.json and assign them to global constants.
    '''
    # Open the config JSON file.
    try:
        config = open(config_file,"r+")
        readable_config = json.load(config)
        config.close()
    except Exception as exception:
        log.error("Unable to read configuration file {0}. Exception: "\
            "{1}".format(config_file, exception))
        sys.exit(1)

    # Assign the settings to global variables.
    global HEADERS
    global ALL_CONTRACTS_URL
    global USER_FRIENDLY_FULL_CONTRACT_URL
    global UPDATED_CONTRACT_URL
    global TWITTER_TOKEN
    global TWITTER_TOKEN_KEY
    global TWITTER_CON_SEC
    global TWITTER_CON_SEC_KEY

    HEADERS = readable_config["headers"]

    ALL_CONTRACTS_URL = readable_config["URLs"]["all_contracts"]
    USER_FRIENDLY_FULL_CONTRACT_URL = readable_config["URLs"]["user_friendly_full_contract"]
    UPDATED_CONTRACT_URL = readable_config["URLs"]["updated_contract"]
    TWITTER_TOKEN = readable_config["twitter"]["token"]
    TWITTER_TOKEN_KEY = readable_config["twitter"]["token_key"]
    TWITTER_CON_SEC = readable_config["twitter"]["con_sec"]
    TWITTER_CON_SEC_KEY = readable_config["twitter"]["con_sec_key"]


def get_all_contracts_uris():
    '''
        This function will get the URIs listed in the page where ALL the 
        contracts are published, essentially creating a list of all the 
        pages detailing every contract, which will be very useful since we 
        need to visit all those URIs to get data for each contract.
    '''
    # Execute API call to ALL_CONTRACTS_URL.
    try:
        #api_response = requests.get(ALL_CONTRACTS_URL, headers=HEADERS)
        api_response = requests.get(ALL_CONTRACTS_URL)
    except Exception as exception:
        log.error("Unable to get response from API when calling {0}. "\
            "Exception: {1}".format(ALL_CONTRACTS_URL, exception))
        sys.exit(2)

    # The status code should be 200 (success). Catch anything else and handle.
    if api_response.status_code != 200:
        log.error("The response status is: {0}".format(response.status_code))
        sys.exit(3)

    # Validate that we got a non-empty result set.
    try:
        readable_api_response = api_response.json()
    except ValueError as exception:
        log.error("Empty result set. Request URL: {0}. "\
            "Exception: {1}".format(ca_url, exception))
        sys.exit(4)

    # Read all the URIs in the API response.
    all_contracts_uris_list = []
    try:
        for contrato in readable_api_response:
            all_contracts_uris_list.append(contrato["uri"])
    except KeyError as exception:
        log.error("There were no results found for "\
            "your request. Exception: {0}".format(exception))
        sys.exit(3)
    else:
        return all_contracts_uris_list


def get_updated_contracts(updated_contract_url):
    '''
        This function will receive the URL of the abridged version of the 
        contract and will look for the "updated_at" value. If we determine 
        that the contract was updated recently, we will add it to a list of 
        "updated contract" which we will eventually tweet.
    '''
    try:
        api_response = requests.get(updated_contract_url)
    except Exception as exception:
        log.error("Unable to get response from API when calling {0}. "\
            "Exception: {1}".format(uri, exception))
        sys.exit(4)

    # The status code should be 200 (success).
    # Catch anything else and handle.
    if api_response.status_code != 200:
        log.error("The response status is: "\
            "{0}".format(response.status_code))
        sys.exit(5)

    # Validate that we got a non-empty result set.
    try:
        readable_api_response = api_response.json()
    except ValueError as exception:
        log.error("Empty result set. Request URL: {0}. "\
            "Exception: {1}".format(uri, exception))
        sys.exit(6)

    # Unfortunately, this is the most reliable "update timestamp" I could find 
    # in all the endpoints. It has no timezone so we are never sure exactly 
    # when the update took place. We will assume it is Mexico's city timezone.
    # E.g. "2017-08-04 21:54:20"
    updated_at = readable_api_response["updated_at"]

    # Get now() - 24 hours. Anything update between then and now will be 
    # considered "updated recently".
    a_day_ago = (datetime.datetime.now() - datetime.timedelta(hours=24))
    updated_at = datetime.datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")

    if updated_at > a_day_ago:
        log.info("The contract {0} was updated recently (at "\
            "{1})".format(updated_contract_url, updated_at))
    else:
        log.info("The contract {0} was NOT updated recently (at "\
            "{1})".format(updated_contract_url, updated_at))




def main():
    # Read settings and environmental configurations.
    read_config()
    #counter = 0

    # First, lets get a list of ALL the contracts using ALL_CONTRACTS_URL.
    # This means we will get a list of ALL the contracts's URIs.
    for uri in get_all_contracts_uris():
        #counter = counter + 1
        #print counter
        # For every contract/URI, we must make a new request to get the 
        # individual data for said contract.
        try:
            api_response = requests.get(uri)
        except Exception as exception:
            log.error("Unable to get response from API when calling {0}. "\
                "Exception: {1}".format(uri, exception))
            sys.exit(4)

        # The status code should be 200 (success).
        # Catch anything else and handle.
        if api_response.status_code != 200:
            log.error("The response status is: "\
                "{0}".format(response.status_code))
            sys.exit(5)

        # Validate that we got a non-empty result set.
        try:
            readable_api_response = api_response.json()
        except ValueError as exception:
            log.error("Empty result set. Request URL: {0}. "\
                "Exception: {1}".format(uri, exception))
            sys.exit(6)


        # For every contract ID, we will open its own abridged data (using 
        # LAST_UPDATE_CONTRACT_URL) and look for the last update date, it is was 
        # updated recently, we will process the contract.

        print "----------------------------------------------------------------"

        # We only care about the last release in the contract, since it should 
        # be the most updated.
        last_release = int(len(readable_api_response["releases"])-1)
        release = readable_api_response["releases"][last_release]

        # The Unique identifier for the contract
        # (E.g. OCDS-87SD3T-AD-SF-DRM-066-2015).
        ocid = release["ocid"]
        ocid_full_contract_url = USER_FRIENDLY_FULL_CONTRACT_URL + ocid
        # This URL will be the andpoint of the abridged version of the contract 
        # (Which is also the only place where it seems an "update date" is 
        # located.)
        updated_contract_url = UPDATED_CONTRACT_URL + ocid
        print "ocid_full_contract_url:", ocid_full_contract_url


        # Using updated_contract_url, we will get the timestamp of the last 
        # update to the contract.
        get_updated_contracts(updated_contract_url)
        

        # Name of the government organization who is paying for the contract.
        buyer = release["buyer"]["name"]
        print "Buyer:", buyer

        # Some contracts are still in the early stages (like planning) so they 
        # do not have interesting information yet. We will ignore them for now.
        if len(release["contracts"]) == 0:
            log.info("This contract is NOT in the contracting phase yet.")
        else: 
            for contract in release["contracts"]:
                # The monetary amount of the contract.
                value = contract["value"]["amount"]
                print "value:", value

                description = contract["description"]
                print "description:", description

                # With the parsed information, call the tweet() function.

    #if contract_create time > get_lastest_tweet_timestamp():
        # Found a new contract (or a new update to a contract), let's parse it.

    # some translations because I do not know anything about legal stuff:
    # tender = licitacion/oferta/propuesta.
    # award = adjudicacion.

if __name__ == "__main__":
    main()
