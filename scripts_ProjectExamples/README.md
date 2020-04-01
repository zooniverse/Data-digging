# scripts_ProjectExamples
Project-specific scripts in sub-directories.

### Project Descriptions
Below we describe the analysis components implemented in each processing script.  Feel free to pick-and-choose features described below when writing new scripts for your own project.

Some issues that all or most of these scripts address:
 - extracting classification marks/answers from within the JSON fields of the CSV classification data exports
 - cleaning the classification export files:
   - removing duplicate classifications (if they occur)
   - dealing with empty classifications (some projects throw them out, others count them as "nothing here" votes)
   - only including classifications from the most up-to-date workflow version(s)

NOTE: For R code that addresses these issues, please see https://www.github.com/aliburchard/DataProcessing.

#### [Andromeda Project Example Project](https://www.zooniverse.org/projects/lcjohnso/ap-aas229-test)
Marking star cluster locations in Hubble Space Telescope images.

*Script* -- Creates CSV of circular marker info from simple marking workflow.

*Marker type* -- circle

#### [Arizona Batwatch](https://www.zooniverse.org/projects/zooniverse/arizona-batwatch)
Watch videos of bats flying around their roost and tag the behaviors that you see.

*Scripts* -- to 1) turn original videos into smaller duration videos and populate a manifest and 2) upload subjects with manifest to Panoptes found in  [this repo](https://github.com/zooniverse/ArizonaBatWatch).

#### [Decoding the Civil War](https://www.zooniverse.org/projects/zooniverse/decoding-the-civil-war)
The decoding the civil war project invites volunteers to transcribe contemporary, hand-written transcripts of telegrams sent between allies during the American Civil War. Portions of these transcripts are enciphered using whole-word substitutions. The ultimate goal of the project is to allow volunteers to identify these substituted words based on their contextual appropriateness.

The bespoke consensus and aggregation code written for this project is archived and documented in a [separate repository](https://github.com/hughdickinson/DCWConsensus).

*Marker type* -- line, text input attached to mark

#### [Exoplanet Explorers](https://www.zooniverse.org/projects/ianc2/exoplanet-explorers)
An exoplanet-finding project run as part of Stargazing Live.

*Scripts* -- Aggregate simple question task (with weighting). Save outputs to Google Drive folder for easy data sharing. This script is adapted from the Pulsar Hunters aggregation script described below; it may be more generally applicable because it doesn't need a bunch of additional files with gold-standard data etc. *Update:* There is now also an aggregation script that's meant to run on a big classification export (the example is 16GB) without requiring a lot of memory, for those whose computers aren't at the bleeding edge in terms of their RAM.

*Marker Type* -- question task

#### [Flying HI](https://www.zooniverse.org/projects/vrooje/flying-hi)
A beta project to examine HI structures in the Milky Way.

*Scripts* -- Extracts markings from classification file into individual files (ready for clustering).

*Marker type* -- line, point, ellipse, text input attached to mark

#### [Focus on Wildlife -- Cleveland Metroparks](https://www.zooniverse.org/projects/pat-lorch/focus-on-wildlife-cleveland-metroparks)
A survey project run by Cleveland Metroparks.

*Scripts* -- Adapts the survey aggregation script initially developed and tested for Wildwatch Kenya (described below)

*Marker type* -- Survey

#### [Galaxy Zoo Bar Lengths](https://www.zooniverse.org/projects/vrooje/galaxy-zoo-bar-lengths/)
Answering questions about the presence of bar structures and marking bar dimensions.

*Scripts* -- Analyzes joint question+marking workflow (but mostly the markings).

*Marker type* -- line

#### [Notes from Nature](https://www.notesfromnature.org)
A transcription project for museum collections. The label reconciliation scripts are maintained in a [separate repository](https://github.com/juliema/label_reconciliations).

#### [Planetary Response Network](https://www.zooniverse.org/projects/vrooje/planetary-response-network-and-rescue-global-ecuador-earthquake-2016)
Extracting markings of damage and other features from post-disaster satellite imagery.

*Script* -- puts classification information together with geocoordinate information from subject exports.

*Marker type* -- point, polygon (though these aren't reduced here)

#### [Planet 9 Project](https://www.zooniverse.org/projects/marckuchner/backyard-worlds-planet-9)
Marking interesting objects (including moving objects) in images from the WISE satellite.

*Script* -- Creates CSV of point marker info from simple marking workflow.

*Marker type* -- point

#### [Pulsar Hunters](https://www.zooniverse.org/projects/zooniverse/pulsar-hunters)
Classification of radio observations to identify pulsar candidates.

*Scripts* -- Analyzes responses and aggregates object type answer, also script for counting classifications. IP address tracking was wonky during this project, so unique non-logged-in users were identified with browser session info instead.

*Marker type* -- no markers, only 1 question task

#### [Steller Watch](https://www.zooniverse.org/projects/sweenkl/steller-watch)
Workflow #1: Yes/No if sea lions are present.

*Scripts* -- 1) Extracts normal csv from embedded JSON. 2) Aggregates results.

*Marker type* -- no marks, only question tasks

#### [Wildwatch Kenya](https://www.zooniverse.org/projects/sandiegozooglobal/wildwatch-kenya)
A survey of species from camera trap data in Kenya.

*Scripts* -- Jailbreak survey annotations into a format more easily digestible by external scripts (1 line per species ID or "nothing here" classification), aggregate jailbroken annotations into a flattened CSV file with one line per subject. Also uses general utility scripts.

*Marker type* -- Survey

#### Galaxy Zoo Touch Table
Classifying galaxies according to shape on a touch table device.

*Scripts* -- In order to prepare a device's local database, this script will read a Panoptes subject export csv and produce an appropriately parsed csv file that is ready for import as a database (.db) file.

### Older Scripts (Ouroboros-based)

#### Galaxy Zoo

##### Misc
Includes scripts that generate progress reports for Ouroboros-based GZ project, and decision tree processing

##### Talk
Scripts that compute statistics and analyzes Talk data for Ouroboros-based GZ project.

##### Reduction
Fairly general scripts to process Galaxy Zoo classification database dumps into
vote fractions for each subject and match with subject metadata.  Note that
this does not (yet) include debiasing.
