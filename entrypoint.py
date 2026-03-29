#! /usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
import sys
import requests
import csv
import re

ALLSPICE_DEMO_CARBON_EMISSION_DATA_URL = "https://hub.allspice.io/AllSpice-Demos/Demo-Data-Source/raw/branch/main/Carbon-Emissions-RefDes-Coefficients/refdes-carbon-coefficients.csv"


def parse_bool(input: str | bool) -> bool:
    """
    Parse a YAML-like boolean string as a boolean.
    """

    if isinstance(input, bool):
        return input
    if input.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif input.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ArgumentTypeError(
            "One of: yes, no, true, false, t, f, y, n, 1, 0 expected."
        )


################################################################################
def get_carbon_emission_data_dict_from_source(url):
    # Post the request and get the response
    response = requests.get(url)
    # Get the text representation of the CSV data
    data_text = response.text
    # Ingest emissions data CSV into a dictionary
    emission_data = {}
    data_reader = csv.reader(data_text.splitlines(), delimiter=",", quotechar='"')
    data_reader.__next__()  # Skip the header row
    for row in data_reader:
        emission_data[str(row[0])] = row[1]
    # Return the data
    return emission_data


################################################################################
def query_demo_carbon_emission_data_for_mfr_part_number(data, reference_designator):
    # get the leading alpha characters of the reference designator
    reference_category = re.search(r"^[A-Z][a-z]*", reference_designator).group(0)
    # Look up part number in dictionary, return emission figure if exists
    try:
        return data[reference_category]
    # Return 0 as a default if part doesn't exist in data source
    except KeyError:
        return 0.0


# If markdown mode, add an empty column at the beginning and end of the given row
# to generate pipe-delimited table
def write_csv_row(csvwriter, is_markdown: bool, row: list[str]):
    # Avoid mutating data by reference
    _row = list(row)
    if is_markdown:
        _row.insert(0, "")
        _row.append("")
    csvwriter.writerow(_row)


################################################################################
if __name__ == "__main__":
    print(f"running: {sys.argv}")
    # Initialize argument parser
    parser = ArgumentParser()
    parser.add_argument("bom_file", help="Path to the BOM file")
    parser.add_argument(
        "--output_file", help="Path to outpub CSV file with emissions data"
    )
    parser.add_argument(
        "--markdown",
        type=parse_bool,
        default=False,
        help="Export table in markdown syntax",
    )
    args, unknown = parser.parse_known_args()

    # Read the BOM file into list
    with open(args.bom_file, newline="") as bomfile:
        # Comma delimited file with " as quote character to be included
        bomreader = csv.reader(bomfile, delimiter=",", quotechar='"')
        header = [x.lower() for x in bomreader.__next__()]
        pn_index = header.index("part number")
        des_index = header.index("designator")
        qty_index = header.index("quantity")
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
        print("- Fetching info for " + line_item[pn_index] + "... ", end="")
        # Search for emission figure for a part in demo data source
        emission_figure = int(line_item[qty_index]) * float(
            query_demo_carbon_emission_data_for_mfr_part_number(
                emission_data, line_item[des_index]
            )
        )
        # Add the obtained figure to the list of BOM items part data
        bom_items_emissions_data.append(
            (
                line_item[pn_index],
                line_item[des_index],
                line_item[qty_index],
                emission_figure,
            )
        )
        # Print the obtained figure
        print(str(emission_figure) + "\n", end="", flush=True)

    # Report the sum of all component emissions
    print("")
    total_emission_for_pcba_BOM = 0.0
    for bom_item in bom_items_emissions_data:
        total_emission_for_pcba_BOM += float(bom_item[3])
    print(f"Total emissions from BOM parts: {total_emission_for_pcba_BOM:.2g} kg CO2e")

    if args.output_file:
        with open(args.output_file, "w", newline="") as csvfile:
            delimiter = ","
            if args.markdown:
                delimiter = "|"
                csvfile.write("<details>\n<summary>Data</summary>\n\n")
            csvwriter = csv.writer(
                csvfile, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            header = ["Part Number", "Designator", "Quantity", "Emission"]
            write_csv_row(csvwriter, args.markdown, header)
            if args.markdown:
                write_csv_row(csvwriter, args.markdown, ["---"] * len(header))
            for row in bom_items_emissions_data:
                write_csv_row(csvwriter, args.markdown, row)

            if args.markdown:
                csvfile.write("\n</details>\n")
                csvfile.write(
                    f"Total emissions from BOM parts: {total_emission_for_pcba_BOM:.2g} kg CO2e"
                )
