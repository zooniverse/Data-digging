### Introduction

In the Classification download, the user's responses to each task are recorded in a field called 'annotations' (including those of experts and those tagged "TRUE" for being gold standard responses. The field is a JSON string. When loaded into Python using the json.loads() function from import json, it becomes a dictionary of dictionaries of form {{....}, {.....}, {....}} with a dictionary for each task the user is required to complete, in the order completed.
The form of the individual dictionaries for the tasks depends very much on what type of task it is - a question, drawing tool, transcription or survey task.  

The annotations dictionary element for a drawing task has the form:

{"task":"TX", "task_label":"drawing instructions the users saw", "value":\[list of drawings_made for that task]}.

The form of each "drawing_made" varies slightly depending what drawing tool type was used. In general they have the form:

{dictionary elements defining the drawing,"tool":a number defining which tool was selected,"frame":0,"details":\["subtask values"],"tool_label":"text for that tool from the project"}.

Just as for questions, we use the knowledge we have of the specific project to parse out the info we want. Often different drawing tools can be analysed separately, and the classification file is flattened to several output files with the data for only certain tasks included.  Example: for Fossil Finder one might analyse tooth and bone separately from tools or shells.
For the simple drawing tools without sub-tasks this is pretty simple, especially if one knows which of the blocks in annotations we are dealing with. Some of the drawing tools are more complex and multiple sub-tasks can complicate the 'details' section.

 ### Format of the drawing_object for the various drawing tools types:

 Point:{"x":161....,"y":203....,"tool":5,"frame":0,"details":\[],"tool_label":"point one"} where the origin (0,0) is the top left corner of the image with x increasing to the right and y increasing down, units are pixels of the subject image.

 Circle:{"x":625....,"y":238....,"r":65...."tool":5,"frame":0,"details":\[],"tool_label":"circle one"} where (x, y) is the centre of the circle and r the radius in pixels. Note drawings can be "picked up" and moved so x and y can be negative in some cases!

 Line:{"x1":681...,"x2":626....,"y1":132....,"y2":209....,"tool":0,"frame":0,"details":\[],"tool_label":"line one"} where (x1,y1)   is the first point set and (x2, y2) is the drawn out point.
 
 Vert_line:{"x":354.....,"tool":1,"frame":0,"details":\[],"tool_label":"full height line"} where x is thelocation
 of the vertical full height line.

 Horz_line:{"y":144.37255859375,"tool":0,"frame":0,"details":\[],"tool_label":"full width line"} where y is
 the location of the horizontal full width line.


 Rectangle:{"x":335..,"y":88...,"tool":1,"frame":0,"width":168...,"height":66...,"details":\[], "tool_label":"box one"} where (x,  y) is the upper left corner.

 Column:{"0":0,"x":559....,"tool":2,"frame":0,"width":45...,"details":\[],"tool_label"
:"column one"} where x is the start location of the left side of the column.

 Triangle:{"r":66...,"x":467...,"y":284...,"tool":3,"angle":-36...,"frame":0,"details":\[],
 "tool_label":"triangle one"} where r is the radius of a circle circumscribed around the triangle, (x, y) would be the centre of that circle, and the angle is between the vertical y axis and the line from the centre to the drawn out vertex, and is measured positive ccw.

 Ellipse:{"x":122...,"y":184...,"rx":129...,"ry":64...,"tool":4,"angle":-27...,"frame":0, "details":\[],"tool_label":"ellipse one"} where (x, y) is the centre of the ellipse, rx is the first axis drawn out and ry is the second axis set by default or later adjusted, and the angle is from the x axis to rx positive ccw.
 
 Polygon:,{"tool":3,"frame":0,"closed":true,"points":\[{"x":375....,"y":272....},{"x":513....,"y":272....},
     {"x":534....,"y":372...},{"x":461...,"y":408....},{"x":371....,"y":356....}],"details":\[],"tool_label":"polygon"}
     where the list of points are the vertices. Polygons can be drawn open or closed - the point list does not change.

 Bezier:{"tool":2,"frame":0,"closed":false,"points":\[{"x":480....,"y":262....},{"x":464.....,"y":23....},
     {"x":704.,"y":121.}],"details":\[],"tool_label":"bezier"} where the 1st, 3rd, 5th etc points are the vertices
     and the 2nd, 4th etc are the points drawn out to form the curves.  Bezier curves can be drawn open
     (total number of points is odd) or closed (always an even number of points).

### Dealing with sub-tasks

In the "drawing_made" dictionaries described above, there is a key 'details' which is where the values entered by the user for any drawing sub-tasks are found. They are of the form "details:\[{"value":1},{"value":\[1,2,6]},{"value":"8.4"},{"value":"equidem gloriatu"}]"  Note there are no labels! just the value elements in order of the sub-tasks that were defined, one for each sub-task defined (even if not used for that particular drawing. This is important because we must rely on the order to decode multiple sub-tasks.
In this example:

{"value":1} is the element for a single Required (radio button) question where 0 means the first possible answer is selected, while 1, 2 etc are the other possible choices in order in the project's sub-task menu.

{"value":\[1,2,6]} is the element for the second sub-task which is a multiple-allowed answer question. These return values as lists of the choices made, again starting at 0, in order.  No choices appears as \[]

{"value":"8.4"}  is typical of the output for a slider type sub-task. Depending on the range and step size this can look like values for single questions except for the quotes.

{"value":"text string"} is typical structure for a transcription sub-task.

Usually there is only one or two sub-tasks for a particular drawing tool. Since we know our project we can force the values into an ordered list which we can tack onto each drawing (point, circle, etc) - a "point" becomes \[x, y, 'label', list of sub-task values]. Note the sub-tasks are associated with a specific drawing, we can not split them off into additional columns - to make sense they have to stay with their drawing.

The crudest but simplest way we can do this is to change the append lines in the Block 1 to

`drawings_1.append([x, y, r, labels['1'], drawing_object['details']])`

If we do this,  each circle will appear like

\[345.0, 567.0, 65.0, ‘c’,\[{"value":\[1]},{"value":"8.4"}]] 

where we have two sub_tasks, a question and a slider.  We could make this neater if we convert the dictionaries to a simple list with a list comprehension.:

\[345, 567, 65, ‘c’, \[\[1], "8.4"]]



### Code blocks in flatten_class_drawing.py

**Block 1 Task uses one tool type (eg points or circles) without sub-tasks.**

The following block returns the drawing tool data for one drawing task which uses several tools of the **same** drawing type (eg colours of points representing different things, or rectangles of different colours to mark different blocks of text etc).


**Block 2 Adds sub-tasks to Block 1.**


**Block 3 More drawing tools: Line(s), Rectangle, Column, Triangle, Ellipse, Polygon, Bezier curve - Mixed tool types in a task.**

While the general idea is the same for all these tool types, the dictionary elements defining the figure change and we need to modify the code to handle these details. For drawing tasks that use different drawing tools within the same task we have to use the tool numbers defined in the project to explicitly select the code that will flatten and simplify the output. Find the tool numbers by looking for the tool labels in the raw data - there will be a one to one correspondence.
The data will need to be split out in columns - one column per task and drawing tool_label. Example:  two drawing tasks, one with four colours of points and another with one colour of circle would require five field names and give five columns.


### The Demos flatten_class_drawing_demo.py and flatten_class_drawing_demo2.py

The first demo has been built up using the basic frame and various general utility and question blocks plus the drawing Block 1 for circles, without sub-task details.  It fully flattens the Aerobotany classifications into a form suitable for aggregating over all users by subject_ids. It is based on flatten_classification_general_utilities_demo_2.py with a question task added, then the Drawing Block 1 integrated into that.

The second demo has been built with the basic frame and drawing block 3 for demonstration purposes only. It flattens lines, rectangles, triangles ellipses and columns, for one mixed tool type task.  Its input and output file are also included in this repository.
