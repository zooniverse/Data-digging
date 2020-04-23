# Data-digging
This repository contains scripts and documentation related to analyzing classification data from Zooniverse projects.  Most content is tailored to Panoptes-based Project Builder projects, but there is also some legacy Ouroboros-based code.

## Where do I go to get started?

You have a few choices when getting started analyzing Zooniverse data.
- *Try the Panoptes Aggregation Code (external):* Try out the [Panoptes Aggregation Code](https://aggregation-caesar.zooniverse.org/docs), a software package designed to take project data exports and produced aggregated results.
- *Try Data-digging's general python scripts:* The [*scripts_GeneralPython*](scripts_GeneralPython) directory contains multiple Python scripts and Jupyter notebooks to get you started.  See the README in that directory for more details.
- *Adapt Existing Scripts:* The Data-digging repo contains many examples of data reduction scripts from multiple projects.  Depending on your project type and details, find a similar project and edit their existing scripts to fit your specific use case.  Check out scripts in the [*scripts_ProjectExamples*](scripts_ProjectExamples) directory, or browse the library of [*External Links*](ExternalLinks.md) for analysis scripts that are hosted in external locations and repos.

## Contents

[*ExternalLinks.md*](ExternalLinks.md): File with links to external code.

[*docs:*](docs) Column descriptions for Panoptes export CSV files.

[*notebooks_ProcessExports:*](notebooks_ProcessExports) This directory holds Jupyter notebooks for performing basic parsing of data export CSVs.

[*scripts_GeneralPython:*](scripts_GeneralPython) This directory holds top-level example scripts that are generally applicable to any project.  These scripts convert a classification data export CSV into more useful formats and data products.  In most cases, these scripts extract information from the compact JSON-formatted “annotations” column data into an easier flat CSV file.

[*scripts_ProjectExamples:*](scripts_ProjectExamples) This directory holds project-specific subdirectories, each with scripts and data files.

[*scripts_Utility:*](scripts_Utility) This directory holds Python scripts for one-off tasks.

[*other_code:*](other_code) This directory holds other contributed code.
