# Cerner-cross-domain-powerplan-compare
This project uses mostly standard python libraries (csv, json) to compare/contrast PowerPlan-specific CCL query outputs that's run between different Cerner domains of a client site to spot any differences between domains. Non-standard libraries (pandas, openpyxl) are mostly used to create the final output file


## How to run

### CCL queries
Run the applicable ccl queries, in dvd, and instead of saving them to Excel, save them into a text fiie using something like Notepad 

We're not using Excel because Excel tries to be helpful when you're pasting in rows of data. One issue that it will not pick up is if one of your fields has an unmatched quote, Excel will attempt to find another matching quote, and suddenly a lot of rows are missing

Instead, we save the results as tab-delimited files and read them in using the `csv` module, and the all important parameter: `quoting=csv.QUOTE_NONE`

Files should be saved in the data folder, grouped together by individual folders belonging to the same domain. For example:

```
cerner-domain-powerplan-compare
├── data
    ├── BUILD
    │   ├── comp_BUILD.txt
    │   ├── os_detail_BUILD.txt
    │   ├── os_filter_BUILD.txt
    │   ├── pathways_BUILD.txt
    |
    ├── PROD
    │   ├── comp_PROD.txt
    │   ├── os_detail_PROD.txt
    │   ├── os_filter_PROD.txt
    │   ├── pathways_PROD.txt
```

### Py scripts
The CSVs are hard coded. Feel free to change it so you can specify the files
- `domain_pathway_component_compare.py` will run the component compare and spit the output file to the current working directory as `output.xlsx`
    - `python domain_pathway_component_compare.py -a [folder_in_data_for_domain_1] -b [folder_in_data_for_domain_2]`

## TODO
- PowerPlan flexing between domains

## Caveats with this tool
- This project is merely pointing people to where they should look for discrepancies between domains. Because IDs are not consistent between domains, the project does not know if there was a synonym name change or a note change - all it knows is that something is different and one component does not appear in the other domain
- If PowerPlan names, Phase names or Clinical Category/Clinical Sub-Category names don't match up, the script will not bother looking into the components because it won't know if the PowerPlans/Phases/etc are truly the same