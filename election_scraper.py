#!/usr/bin/env python3
"""
project_03: 3rd project to ENGETO Online Python Academy

author: Martin Alex Urbiš
email: urbis.martin@gmail.com
discord: segen0
"""

# required libraries
import sys
import requests
import bs4
import csv
import traceback
import re
import pandas as pd
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

# Variable/constants declaration
file_name: str  # name of the output file
arguments: str  # necessary arguments passed for execution of program

kraj: str  # 1st component of URL for 2nd level of processing
xnumnuts: str  # 2nd component of URL for 2nd level of processing
kod_obce: str  # 1st component of individual row in the table
output_file: str  # CSV output file
first_level_processing_index: int = (
    0  # loop counter for 1st level of processing
)
current_municipality_index: int = 0  # loop counter for 2nd level of processing
party_result_index: int = (
    0  # looping through all parties in the municipalities
)

# URL string for individual municipality - full assembly
# with individual URL components (kraj, xnumnuts)
obec_url: str

# List of IDs individual municipalities in electoral district
# the list is source for processing of individual web pages
municip_id_results: list = []

# Header definition for output table (36 columns)
base_headers = ["code", "location", "registred", "envelopes", "valid"]

# Check if the 'parties.json' file exists
try:
    file_path = Path("parties.json")
    if not file_path.is_file():
        print(
            "\nError: the file 'parties.json' is missing in the current directory. Exiting the program.\n"
        )
        sys.exit(
            1
        )  # Exit the program with a non-zero status to indicate an error
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)  # Exit the program in case of any unexpected errors


with open("parties.json", "r", encoding="utf-8") as f:
    party_headers = json.load(f)

table_header = base_headers + party_headers

# Main table for results of individual municipalities
municipality_results: list = []

# Template for URL of individual municipalities there are two variable components
# of the URL (kraj, xnumnuts) parsed during processing of individual web pages
GENERIC_URL: str = "https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj="

# First five items for individual municipalities
five_first_items: list = []

# Temporary dictionary for election results
party_details: dict = {}

# All result of individual parties for individual municipalities
# are here - one row is one municipality
result_table: list = []


# Functions definition
def help_arguments() -> str:
    """Display parameters requirements for command line.

    Returns:
        str: a string with requirements for command line.
    """
    return "\nCommand line for execution: argument 1 = web link; argument 2 = file name always with extension 'csv'.\n"


def validate_url(input: str) -> bool:
    """
    Returns False if the URL is not valid.

    Args:
        input (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """

    # Main URL - start point for all individual URLs
    BASE_URL: str = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    # URL component template
    GENERIC_COMP: str = "https://www.volby.cz/pls/ps2017nss/"

    # Send a GET request to the webpage
    response = requests.get(BASE_URL)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all elements that match the pattern
    elements = soup.find_all("td", headers=lambda x: x and "sa3" in x)

    href_pattern = re.compile(
        r'href="(ps32\?xjazyk=CZ&amp;xkraj=\d+&xnumnuts=\d+)"'
    )

    # Extract the href attribute
    pattern = re.compile(r'href="([^"]+)"')

    # Loop through the elements and extract href values
    for td in elements:
        match = pattern.search(str(td))  # Convert to string and search
        if match:
            url = match.group(1).replace("&amp;", "&")  # Decode &amp;
            if GENERIC_COMP + url == input:
                return True
    return False


def fetch_url_components(url: str) -> tuple[str, str]:
    """
    Fetching value 'kraj' and 'xnumnuts' from URL
    territorial units reference - used for parsing values
    of individual municipalities.

    Args:
        url (str): URL of the web page containing the election results.

    Returns:
        tuple[str, str]: A tuple containing the values of 'kraj' and 'xnumnuts'.
    """
    match = re.search(r"xkraj=(?P<kraj>\d+).*?xnumnuts=(?P<xnumnuts>\d+)", url)
    if match:
        return match.group("kraj"), match.group("xnumnuts")
    raise ValueError("Unable to extract 'kraj' and 'xnumnuts' from URL")


def select_municipality_id(input: int) -> str:
    """
    Retrieve the municipality ID number as a string for the given index.

    Args:
        input (int): Index of the district in the list.

    Returns:
        str: The municipality ID number.
    """
    return municipality_id[input].getText()


def compile_url(index: int) -> str:
    """
    Assembly of the temporary url address
    for individual municipality.

    Args:
        input (int): Index of the municipality in the list of municipalities.

    Returns:
        str: Temporary URL for the individual municipality.
    """
    return f"{GENERIC_URL}{kraj}&xobec={municip_id_results[index]}&xvyber={xnumnuts}"


def get_kod_obce(input: int) -> str:
    """
    Return municipality ID (Kod obce)
    1st component of each row in the table.

    Args:
        input (int): Row index of the table to retrieve.

    Returns:
        str: Municipality ID (Kod obce).
    """
    kod_obce = municip_id_results[input]
    return kod_obce


def extract_text(element: list) -> str:
    """
    Extract text from an HTML element and remove formatting spaces.

    :param element: List of HTML elements to extract text from.
    :return: Formatted string with spaces removed, or None if no element is present.
    """
    if element:
        return (
            element[0]
            .get_text(strip=True)
            .replace("\xa0", "")
            .replace(" ", "")
        )
    else:
        return ""


def get_party_details(input: int) -> dict:
    """
    Get required party details from the table.

    :param input: Index to retrieve party details.
    :return: Dictionary containing party id and result.
    """
    return {
        "id": party_id[input].getText(),
        "result": party_results[input].getText(),
    }


def clean_text(input: str) -> str:
    """
    Remove non-breaking space and regular space from a string.

    :param input: string to be cleaned
    :return: cleaned string
    """
    return input.replace("\xa0", "").replace(" ", "")


# Validation of input arguments
# 1. Call up help
if sys.argv[1] == "help":
    print(help_arguments())
    exit()

# 2. No argument passed to command line
if len(sys.argv) == 1:
    print("\nError: No argument passed to command line! Exiting the program.")
    exit()

# 3. Passed only one argument from two
if len(sys.argv) == 2:
    print("\nError: Passed only one argument from two! Exiting the program.")
    exit()

# 4. Incorrect order of passed arguments
if len(sys.argv) > 2:
    if (
        sys.argv[1] != "help"
        and sys.argv[1].endswith(".csv")
        and sys.argv[2].startswith("https://")
    ):
        print(
            "\nError: Incorrect order of passed arguments! Exiting the program."
        )
        exit()

# 5. Incorrect html link
if validate_url(sys.argv[1]) != True:
    print("\nError: Incorrect html link! Exiting the program.")
    exit()

# = = = MAIN PROCESSING = = =
# 1st level of selection - main page of electoral district with individual municipalities

print("\nDOWNLOADING DATA FROM SELECTED URL:", sys.argv[1], "\n")

# Fetch 1st and 2nd component of URL for 2nd level of processing
kraj = fetch_url_components(sys.argv[1])[0]
xnumnuts = fetch_url_components(sys.argv[1])[1]

# Fetch the 1st level web page
server_resp = requests.get(sys.argv[1], timeout=10)

# Check if the request was successful
try:
    server_resp.raise_for_status()  # Raises an HTTPError for bad responses
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from {server_resp}: {e}")
    sys.exit(1)  # Exit the program


# Parse the HTML content
soup = BeautifulSoup(server_resp.text, "html.parser")

# Uploading the numbers of individual municipalities for the selected district
municipality_id = soup.find_all(
    "td",
    class_="cislo",
    headers=lambda h: "t1sa1" in h or "t2sa1" in h or "t3sa1" in h,
)

result_table.append(table_header)  # Add header into main table

# Fill list of individual municipality ID
for id in municipality_id:
    municip_id_results.append(
        select_municipality_id(first_level_processing_index)
    )
    first_level_processing_index += 1

# Processing of 2nd level of selection - pages with election results in the individual municipalities

for id in municip_id_results:
    # Get the unique url address
    server_resp = requests.get(
        compile_url(current_municipality_index), timeout=10
    )

    try:
        server_resp.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error fetching data from {server_resp}: {e}")
        sys.exit(1)  # Exit the program

    obec_url = compile_url(current_municipality_index)

    # Fetch the web page
    server_resp = requests.get(obec_url)

    # Parse the HTML content
    # Municipality identification - five first items for the table
    soup = BeautifulSoup(server_resp.text, "html.parser")

    # Add first five items to list - it is always only on
    # the begginig of processing of individual munucupalities

    # Field 'kod obce' col#1
    five_first_items.append(get_kod_obce(current_municipality_index))

    # Field 'obec' col#2
    obec = soup.find("h3", string=lambda text: text and "Obec:" in text)

    if obec:
        five_first_items.append(
            obec.get_text(strip=True).replace("Obec: ", "")
        )

    # Field 'volici v seznamu' col#3
    volici_seznam = soup.find_all("td", class_="cislo", headers="sa2")
    five_first_items.append(extract_text(volici_seznam))

    # Field 'vydane obalky' col#4
    vydane_obalky = soup.find_all("td", class_="cislo", headers="sa3")
    five_first_items.append(extract_text(vydane_obalky))

    # Field 'platne hlasy' col#5
    platne_hlasy = soup.find_all("td", class_="cislo", headers="sa6")
    five_first_items.append(extract_text(platne_hlasy))

    municipality_results.append(five_first_items)

    # Add values of individual parties in the municipality into teh row in the table col#6 - #36

    party_id = soup.find_all(
        "td",
        class_="cislo",
        headers=lambda h: "t1sa1" in h or "t2sa1" in h,
    )

    party_results = soup.find_all(
        "td",
        class_="cislo",
        headers=lambda h: "t1sb3" in h or "t2sb3" in h,
    )

    # get election results of individual parties in the municipality
    for input in range(len(party_id)):
        party_details[party_id[input].getText()] = clean_text(
            party_results[input].getText()
        )

    # Convert dictionary keys from strings to integers
    party_details = {int(k): v for k, v in party_details.items()}

    # Merge list and dictionary for current municipality
    merged_list: list = []

    merged_list = five_first_items[:]  # Start with the base list
    five_first_items.clear()

    # Loop through the individual parties in municipality
    for i in range(1, len(party_headers) + 1):
        if i in party_details:  # Check if i exists as a key in party_details
            merged_list.append(party_details[i])  # Append the value
        else:
            merged_list.append("-")  # Append '-' if key is missing

    result_table.append(merged_list)  # Add header into main table

    party_result_index = 1
    current_municipality_index += 1

# Save results in CSV file
file_name = sys.argv[2] + ".csv"
df_result_table = pd.DataFrame(result_table)
df_result_table.to_csv(file_name, index=False, header=False)

# Message to screen
print("SAVE TO FILE: ", file_name)
print("\nENDING THE PROGRAM ", sys.argv[0], "\n")
print(
    "If there is charcter hyphen (-) in the CSV file, it means that the party was not on the list in the electoral district.\n"
)
