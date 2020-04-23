### Flying HI marker extraction

This is a beta project to examine images of the Milky Way for features. There were 3 different kinds of marks: a point mark (background galaxy), a line mark (magnetically-aligned fiber features), and an ellipse mark ("other") with a text-entry sub-task. 

The file `extract_markings.py` reads the classification export, throws out classifications from old workflow versions, and extracts the marking information for each type of mark, writing each mark to a file. (There are multiple files written, one for each mark type.) The file also tracks which classifications were empty, i.e. no annotations. For this project, an empty classification amounts to a vote for "there's nothing here", which may end up being useful for data reduction purposes.

Each of the output files with markings is ready to be fed into a clustering routine. There are examples of these in other projects in this repo. For example, the [Galaxy Zoo Bar Lengths](https://github.com/zooniverse/Data-digging/blob/master/example_scripts/galaxy_zoo_bar_lengths/cluster_line_markings.py) folder has one for clustering line markings, which could be adapted without too much trouble to be run on the fiber markings here. 

Note: duplicate classifications aren't handled here yet.

The code is reasonably well commented, but if you have questions [post an issue](https://github.com/zooniverse/Data-digging/issues) and tag @vrooje.
