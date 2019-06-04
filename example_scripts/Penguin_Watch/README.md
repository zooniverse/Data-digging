## Kraken Script
- Input files: 'PW Consensus Click Data' (DOI: 10.5061/dryad.vv36g); the 'Penguin Watch Manifest'.
- Output files: 'Kraken Files'.

The Kraken Script (R version 3.6.0) creates a csv file of filtered 'consensus click' data and metadata for time-lapse images processed by the _Penguin Watch_ citizen science project (www.penguinwatch.org), by image set. The metadata included are: date/time, temperature (Fahrenheit), lunar phase and a URL link to a thumbnail of the time-lapse image.

In this script, adult penguin 'consensus clicks' must have been formed from four or more volunteer raw clicks to be included. Chick and egg 'consensus clicks' are included if they were formed from two or more raw clicks (please see the 'Technical Validation' section of Jones et al. (2018) (DOI: 10.1038/sdata.2018.124) for more information about these variables and thresholds.

## Narwhal Script
- Input files: 'Kraken Files' (see above)
- Output files: 'Narwhal Files'

The Narwhal Script (R version 3.6.0) is used to generate Narwhal Files.

Narwhal Files provide: 
- count data for adults, chicks and eggs
- mean and standard deviation adult nearest neighbour distances (nnd)
- mean and standard deviation chick nnd
- mean and standard deviation chick 2nd nnd (since the first nearest neighbour is likely to be its sibling in the nest)
- adult nnd between the ith and i-1th image (an approximation of adult movement between images)
- chick nnd between the ith and i-1th image (an approximation of chick movement between images)
- Metadata (date/time, temperature (in Fahrenheit and Celsius), lunar phase and a URL link to a thumbnail of the time-lapse image. 

## Narwhal Plotting Script
- Input files: 'Narwhal Files'
- Output files: 'Narwhal Plots'

The Narwhal Plotting Script (R version 3.6.0) is used to plot the variables calculated by the Narwhal Script (see above). 

The code produces a multi-panel plot for every time-lapse image, comprising the following:
- The time-lapse image
- Graph 1: number of adults and chicks (as a moving average)
- Graph 2: chick second nearest neighbour distance (as a moving average)
- Graph 3: Adult movement (adult nnd between the ith and i-1th image; as a moving average).

Each graph shows the trend up to, and including, the current image (to see the complete graphs, please plot the final image in the series).

## Pengbot Counting Script
- Input files: 'Pengbot Out Files'
- Output files: 'Pengbot Density Maps'; 'Pengbot Counts' 

The Pengbot Counting Script (R version 3.6.0) takes 'Pengbot Out Files' (generated using the Pengbot computer vision algorithm of Arteta et al. (2016) – see https://www.robots.ox.ac.uk/~vgg/data/penguins/ for more information), and creates 'Pengbot Density Maps' and 'Pengbot Counts'.