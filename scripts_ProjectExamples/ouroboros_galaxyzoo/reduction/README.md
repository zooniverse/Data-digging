# gz_reduce
Code for doing initial reduction of data from Ouroboros Galaxy Zoo projects

This code gets the question and answer tags from the CoffeeScript description of the tree used by the site itself.
This makes the resulting column names automatic and (fairly) consistent, but may require a bit of extra checking if
multiple questions/answers have the same tag (in which case the code appends a, b, c, ...).

Note that using these scripts requires access to a database dump of the classifications.
Regular emails with URLs to the latest dumps are sent to team members on request.

You will also need the subject catalogue, which is available on request (or see Slack #galaxyzoo channel).

The outputs from running these scripts are on dropbox – see Slack #galaxyzoo channel for a link.

This code may be useful for other Ouroboros-based projects.
