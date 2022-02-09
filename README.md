# Cerner-cross-domain-powerplan-compare
This project uses mostly native python libraries (csv, json) to compare/contrast PowerPlan-specific CCL query outputs that's run between different Cerner domains of a client site to spot any differences between domains

Please note that I'm sure there are better ways to write this, and there are plenty of things that I'm not proud of here, but.. it works? Refactoring can come later

## How to run
The CSVs are hard coded. Feel free to change it so you can specify the files
- `domain_pathway_compare.py` will run the pathway compare and spit the output file to your current working directory. This uses the hard-coded files:
    - b0783_pathway.csv
    - p0783_pathway.csv
- `domain_pathway_component_compare.py` will run the component compare and spit the output file to the current working directory
    - ONCP_comp_b0783.csv
    - ONCP_comp_p0783.csv
    - os_filter_b0783.csv
    - os_filter_p0783.csv
    - os_detail_b0783.csv
    - os_detail_p0783.csv
- `domain_regimen_compare.py` runs the regimen compare
    - b0783_regimens.csv
    - p0783_pathways.csv
- `main.py` will run all compares

## Why a million ccl scripts
Originally I was thinking to create a giant ccl script that pulls all of the information in. The problem that I kept running into was the hierarchical structure. I couldn't save everything as a 100+ mb json file. and csv outputs have a finite limit of what can be displayed to "mine", without output a file to one of the nodes and having to retrieve it later

So an alternative was to run multiple queries, have python combine them into a giant dictionary and then do the compare that way. This became a little bit more sustainable because it can cover more PowerPlans simultaneously. Using a giant ccl script and have to save the file each time generated meant having to figure out how to break up all of the powerplans