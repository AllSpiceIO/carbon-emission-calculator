#! /usr/bin/env python3

from argparse import ArgumentParser
import requests
import csv

ALLSPICE_DEMO_CARBON_EMISSION_DATA_URL = "https://hub.allspice.io/AllSpice-Demos/Demo-Data-Source/raw/branch/main/Carbon-Emissions-Figures-Archimajor/archimajor-carbon-emissions-figures.csv"


################################################################################
def get_carbon_emission_data_dict_from_source(url):
    # Post the request and get the response
    response = requests.get(url)
    # Get the text representation of the CSV data
    data_text = response.text
    # Ingest emissions data CSV into a dictionary
    emission_data = {}
    data_reader = csv.reader(data_text.splitlines(), delimiter=",", quotechar='"')
    for row in data_reader:
        emission_data[str(row[0])] = row[1]
    # Return the data
    return emission_data


################################################################################
def query_demo_carbon_emission_data_for_mfr_part_number(data, part_number):
    # Look up part number in dictionary, return emission figure if exists
    try:
        return (data[part_number]).strip().replace('"', "")
    # Return 0 as a default if part doesn't exist in data source
    except KeyError:
        return 0.0


################################################################################
if __name__ == "__main__":
    # Initialize argument parser
    parser = ArgumentParser()
    parser.add_argument("bom_file", help="Path to the BOM file")
    args = parser.parse_args()

    # Read the BOM file into list
    with open(args.bom_file, newline="") as bomfile:
        # Comma delimited file with " as quote character to be included
        bomreader = csv.reader(bomfile, delimiter=",", quotechar='"')
        # Save as a list
        bom_line_items = list(bomreader)
        # Skip the header
        del bom_line_items[0]

    # Initialize list of BOM item emissions data
    bom_items_emissions_data = []

    print("- Fetching carbon emissions data from demo data source")
    print("")
    emission_data = get_carbon_emission_data_dict_from_source(
        ALLSPICE_DEMO_CARBON_EMISSION_DATA_URL
    )

    # Fetch emissions figures for all parts in the BOM
    for line_item in bom_line_items:
        print("- Fetching info for " + line_item[0] + "... ", end="")
        # Search for emission figure for a part in demo data source
        emission_figure = query_demo_carbon_emission_data_for_mfr_part_number(
            emission_data, line_item[0]
        )
        # Add the obtained figure to the list of BOM items part data
        bom_items_emissions_data.append((line_item[0], float(emission_figure)))
        # Print the obtained figure
        print(str(emission_figure) + "\n", end="", flush=True)

    # Report the sum of all component emissions
    print("")
    total_emission_for_pcba_BOM = 0.0
    for bom_item in bom_items_emissions_data:
        total_emission_for_pcba_BOM += bom_item[1]
    print("Total emissions from BOM parts: " + str(total_emission_for_pcba_BOM))
