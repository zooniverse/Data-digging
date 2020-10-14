# utility_scripts

Scripts that perform various duties and tasks on Panoptes projects and project
data exports.

### Script Descriptions

- `configure_training_subjects.py`: Perform core pieces of workflow config for
use of training subjects - metadata edit and workflow configuration dict update.
Note: additional Caesar config and workflow retirement criteria update by Zoo
team member is required for use.

- `delete_subjects.py`: Delete subjects (permanently!) selected based on subject
set ID and range of subject IDs.  Edit Python script and run from command line.

- `edit_metadata.py`: Add or edit fields in subject metadata for a given subject
set or sets.  Edit Python script and run from command line.

- `remove_combo_nesting.py`: Remove nested annotations that result from the use
of the Combo task from a classification data export. Call Python script from
command line and pass input variables via command line call.
