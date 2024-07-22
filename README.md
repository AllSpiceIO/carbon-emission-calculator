# Carbon Emissions Calculator for PCBA
An actions repository for demonstrating the calculation of the sum carbon emission for a PCBA given an input BOM and a data source with component emissions data

## Usage

Add the following step to your actions:

```yaml
- name: Generate carbon emissions report for a PCBA given its BOM
  uses: https://hub.allspice.io/Actions/carbon-emission-calculator@v1
  with:
    bom_file: bom.csv
```

## Input BOM

The input BOM to this Action is assumed to be generated from the py-allspice BOM generation utility. The column names referenced and used in this Action script assume the naming convention as populated by the py-allspice BOM generation function. The user is to adjust the expected column positions and naming conventions when using their own BOM file input.

A typical workflow is to use the [BOM generation Actions add-on](https://hub.allspice.io/Actions/generate-bom) to generate the BOM first, and use the generated BOM as an input to this Action.
