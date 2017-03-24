# Data-digging
This repository contains scripts and documentation related to analyzing classification data from Zooniverse projects.  Most content is tailored to Panoptes-based Project Builder projects, but there is also some legacy Ouroboros-based code.

*docs*: Column descriptions for Panoptes export CSV files.

*example_scripts*: The example_scripts directory holds top-level example scripts (which are generally applicable to any project) and project-specific subdirectories, each with scripts and data files.  These scripts convert classification data export CSV into more useful formats and data products.  In most cases, these scripts extract information from the compact JSON-formatted “annotations” column data into an easier flat CSV file.

*development*: Sandbox directory for code development.

### Project & Script Descriptions
Below we describe the analysis components implemented in each processing script.  Feel free to pick-and-choose features described below when writing new scripts for your own project.

#### [Andromeda Project Example Project](https://www.zooniverse.org/projects/lcjohnso/ap-aas229-test)
Marking star cluster locations in Hubble Space Telescope images.

*Script* -- Creates CSV of circular marker info from simple marking workflow.

#### Flying HI
A beta project to examine HI structures in the Milky Way.

*Scripts* -- Extracts markings from classification file into individual files (ready for clustering).

#### Galaxy Zoo Bar Lengths
Answering questions about the presence of bar structures and marking bar dimensions.

*Scripts* -- Analyzes joint question+marking workflow (but mostly the markings).

#### Planetary Response Network
Extracting markings of damage and other features from post-disaster satellite imagery.

*Script* -- puts classification information together with geocoordinate information from subject exports.

#### Pulsar Hunters
Classification of radio observations to identify pulsar candidates.

*Scripts* -- Analyzes responses and aggregates object type answer, also script for counting classifications.

#### [Rogue Worlds: Planet 9 Project](https://www.zooniverse.org/projects/marckuchner/planet-9-rogue-worlds)
Marking interesting objects (including moving objects) in images from the WISE satellite.

*Script* -- Creates CSV of point marker info from simple marking workflow.

#### [Steller Watch](https://www.zooniverse.org/projects/sweenkl/steller-watch)
Workflow #1: Yes/No if sea lions are present.

*Scripts* -- 1) Extracts normal csv from embedded JSON. 2) Aggregates results.

#### Decoding the Civil War
The decoding the civil war project invites volunteers to transcribe contemporary, hand-written transcripts of telegrams sent between allies during the American Civil War. Portions of these transcripts are enciphered using whole-word substitutions. The ultimate goal of the project is to allow volunteers to identify these substituted words based on their contextual appropriateness.

The bespoke consensus and aggregation code written for this project is archived and documented in a [separate repository](https://github.com/hughdickinson/DCWConsensus).

### Older Scripts (Ouroboros-based)

#### Galaxy Zoo: Misc
Includes scripts that generate progress reports for Ouroboros-based GZ project, and decision tree processing

#### Galaxy Zoo: Talk
Scripts that compute statistics and analyzes Talk data for Ouroboros-based GZ project.
