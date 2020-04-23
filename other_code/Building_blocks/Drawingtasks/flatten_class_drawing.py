"""In the Classification download, the user's responses to each task are recorded in a field called
'annotations' (including those of experts and those tagged "TRUE" for being gold standard responses.
The field is a JSON string. When loaded into Python using the json.loads() function from import json,
it becomes a dictionary of dictionaries of form {{....}, {.....}, {....}} with a dictionary for each
task the user is required to complete, in the order completed.
The form of the individual dictionaries for the tasks depends very much on what type of task it is -
a question, drawing tool, transcription or survey task.  This set of scripts are for **drawing** tasks.

The annotations dictionary element for a drawing task has the form:
{"task":"TX", "task_label":"drawing instructions the users saw", "value":[list of drawing_made for that task]}.
The form of each "drawing_made" varies slightly depending what drawing tool type was used. In general
they have the form: {dictionary elements defining the drawing,"tool":a number defining which tool was selected,
"frame":0,"details":["subtask values"],"tool_label":"text for that tool from the project"},

Just as for questions, we use the knowledge we have of the specific project to parse out the info we want.
Often different drawing tools can be analysed separately, and the classification file is flattened to several
output files with the data for only certain tasks included.  Example: for Fossil Finder one might analyse tooth
and bone separately from tools or shells.
For the simple drawing tools without sub-tasks this is pretty simple, especially if one knows which of
the blocks in annotations we are dealing with. Some of the drawing tools are more complex and multiple sub-tasks
can complicate the 'details' section.

 Format of the drawing_object for the various drawing tools types:

 Point:{"x":161....,"y":203....,"tool":5,"frame":0,"details":[],"tool_label":"point one"} where the origin
    (0,0) is the top left corner of the image with x increasing to the right and y increasing down, units are
     pixels of the subject image.

 Circle:{"x":625....,"y":238....,"r":65...."tool":5,"frame":0,"details":[],"tool_label":"circle one"} where (x, y)
    is the centre of the circle and r the radius in pixels. Note drawings can be "picked up" and moved so x and y
    can be negative in some cases!

 Line:{"x1":681...,"x2":626....,"y1":132....,"y2":209....,"tool":0,"frame":0,"details":[],"tool_label":"line one"}
     where (x1,y1) is the first point set and (x2, y2) is the drawn out point.
     
 Vert_line:{"x":354.....,"tool":1,"frame":0,"details":[],"tool_label":"full height line"} where x is the location
      of the vertical full height line.

 Horz_line:{"y":144.37255859375,"tool":0,"frame":0,"details":[],"tool_label":"full width line"} where y is
      the location of the horizontal full width line.

 Rectangle:{"x":335...,"y":88...,"tool":1,"frame":0,"width":168...,"height":66...,"details":[],
     "tool_label":"box one"} where (x, y) is the upper left corner.

 Column:{"0":0,"x":559.....,"tool":2,"frame":0,"width":45....,"details":[],"tool_label":"column one"}
     where x is the start location on the left side of the column.

 Triangle:{"r":66...,"x":467...,"y":284...,"tool":3,"angle":-36...,"frame":0,"details":[],
     "tool_label":"triangle one"} where r is the radius of a circle circumscribed around the triangle,
     (x, y) would be the centre of that circle, and the angle is between the vertical y axis and the line
     from the centre to the drawn out vertex, and is measured positive ccw.

 Ellipse:{"x":122...,"y":184...,"rx":129...,"ry":64...,"tool":4,"angle":-27...,"frame":0,"details":[],
     "tool_label":"ellipse one"} where (x, y) is the centre of the ellipse, rx is the first axis drawn out
     and ry is the second axis set by default or later adjusted, and the angle is from the x axis to rx positive ccw.
     
 Polygon:{"tool":3,"frame":0,"closed":true,"points":[{"x":375....,"y":272....},{"x":513....,"y":272....},
     {"x":534....,"y":372...},{"x":461...,"y":408....},{"x":371....,"y":356....}],"details":[],"tool_label":"polygon"}
     where the list of points are the vertices. Polygons can be drawn open or closed - the point list does not change.

 Bezier:{"tool":2,"frame":0,"closed":false,"points":[{"x":480....,"y":262....},{"x":464....,"y":23....},
     {"x":704....,"y":121....}],"details":[],"tool_label":"bezier"} where the 1st, 3rd, 5th etc points are the vertices
     and the 2nd, 4th etc are the points pull or drawn out to form the curves.  Bezier curves can be drawn open
     (total number of points is odd) or closed (always an even number of points)."""

#  _______________________________________________________________________________________________________________

# Block 1 Task uses one tool type - example several colours of points or circles without sub-tasks.
# The following block returns the drawing tool data for one drawing task which uses several tools of the SAME
# drawing type (eg colours of points representing different things, or rectangles of different colours to mark
# different blocks of text etc).  For now we will assume no sub_tasks.  Block 2 will show how to add sub_tasks to
# the output. To use this block:

    #  First - place this line in the initialization area of a flatten_class_frame, with an element for each tool
        #  number defined in the task.  Replace 'label_X' with a short-form (single letter) designator for that tool.
    labels = {'0': 'label_0', '1': 'label_1', ...., 'N': 'label_N'}
        #  This will allow us to label each drawing with a short-form label that makes more sense to us than just
        #  a number. Example: for Fossil Finder tool 0 was to mark bones with blue points - we can set 'label_0'
        #  as 'b' so anytime we see a point marking a bone it will appear as [x_location, y_location, 'b'].
        #  This is not absolutely necessary but it can be very confusing looking at the lists of drawings (points)
        #  without some label to tell us which they are; using the full tool_label makes the lists of points unwieldy.
    # Secondly add appropriate field names to the list of output field names and to the writer, and assign them
        #  the values drawings_X.  Each tool (ie number or colour) will have a separate field name and column
        #  with a list of all the points or circles of that colour as the data in the field.
    # Third - add this block in the main area of the frame within the iteration loop over the classification records.

                # pull out [x,y], rounds data.
                drawings_0 = []
                drawings_1 = []
                #....
                drawings_N = []
                for task in annotations: # this for loop can be shared with other drawing or question blocks
                    try:
                        if 'drawing task snippet' in task['task_label']:
                            for drawing_object in task['value']:
                                if drawing_object['x'] is not None:
                                    # round to desired accuracy in pixels (0 or 1 decimal is about optimum)
                                    x = int(round((drawing_object['x']), 0))
                                    y = int(round((drawing_object['y']), 0))
                                    r = int(round(drawing_object['r'], 0)) #  Modify these lines as needed
                                    #  based on the tool type in use and the parameters shown above. Also modify
                                    #  the parameters in the append lists below.
                                    #  Various functions to test the validity of the drawing can be added
                                    #  here. See flatten_class_tests.py (not yet completed)
                                    #  test_bounds(x, y, image_size)
                                    #  test_radius(r, image_size, limits)
                                    if drawing_object['tool'] == '0':
                                        drawings_0.append([x, y, r, labels['0']])
                                    if drawing_object['tool'] == '1':
                                        drawings_1.append([x, y, r, labels['1']])
                                    #.....
                                    if drawing_object['tool'] == 'N':
                                        drawings_N.append([x, y, r, labels['N']])

                    except KeyError:
                        continue
                # return lists to JSON string format prior to writing them to file
                drawings_0 = json.dumps(drawings_0)
                drawings_1 = json.dumps(drawings_1)
                #....
                drawings_N = json.dumps(drawings_N)
# __________________________________________________________________________________________________________________

#  Block 2 Dealing with sub-tasks
#  In the "drawing_made" dictionaries described above, there is a key 'details' which is where the values
#  entered by the user for any drawing sub-tasks are found. They are of the form "details:[{"value":1},
#  {"value":[1,2,6]},{"value":"8.4"},{"value":"equidem gloriatu"}]"  Note there are no labels! just the value
#  elements in order of the sub-tasks that were defined, one for each sub-task defined (even if not used for
#  that particular drawing. This is important because we must rely on the order to decode multiple sub-tasks.
#  In this example:
#  {"value":1} is the element for a single Required (radio button) question where 0 means the first possible answer
#  is selected, while 1, 2 etc are the other possible choices in order in the project's sub-task menu.
#  {"value":[1,2,6]} is the element for the second sub-task which is a multiple-allowed answer question.
#  These return values as lists of the choices made, again starting at 0, in order.  No choices appears as []
#  {"value":"8.4"}  is typical of the output for a slider type sub-task. Depending on the range and step size this
#  can look like values for single questions except for the quotes.
#  {"value":"text string"} is typical structure for a transcription sub-task.

#  Usually there is only one or two sub-tasks for a particular drawing tool. Since we know our project we can
#  force the values into an ordered list which we can tack onto each drawing (point, circle, etc) - a "point" becomes
#  [x, y, 'label', list of sub-task values]. Note the sub-tasks are associated with a specific drawing, we can not
#  split them off into additional columns - to make sense they have to stay with their drawing.

#  The crudest but simplest way we can do this is to change the append lines in the above block to
                        drawings_1.append([x, y, r, labels['1'], drawing_object['details']])
#  If we do this,  each circle will appear like [345, 567, 65, a, [{"value":[1]},{"value":"8.4"}]] where we have
#  two sub_tasks, a question and a slider.  We could make this neater : [345, 567, 65, a, [[1], "8.4"]] if we
# convert the dictionaries to a simple list with a list comprehension.  The block above becomes:

                # pull out [x,y], rounds data.
                drawings_0 = []
                drawings_1 = []
                #....
                drawings_N = []
                for task in annotations: # this for loop can be shared with other drawing or question blocks
                    try:
                        if 'drawing task snippet' in task['task_label']:
                            for drawing_object in task['value']:
                                if drawing_object['x'] is not None:
                                    # round to desired accuracy in pixels (0 or 1 decimal is about optimum)
                                    x = int(round((drawing_object['x']), 0))
                                    y = int(round((drawing_object['y']), 0))
                                    r = int(round(drawing_object['r'], 0)) #  Modify these lines as needed
                                    #  based on the tool type in use and the parameters shown above. Also add
                                    #  the parameters to the append lists below.
                                    #  Various functions to test the validity of the drawing can be added
                                    #  here. See flatten_class_tests.py if completed
                                    #  test_bounds(x, y, image_size)
                                    #  test_radius(r, image_size, limits)
                                    detail = [item['value'] for item in drawing_object['details']]
                                    if drawing_object['tool'] == '0':
                                        drawings_0.append([x, y, r, labels['0'], detail])
                                    if drawing_object['tool'] == '1':
                                        drawings_1.append([x, y, r, labels['1'], detail])
                                    #.....
                                    if drawing_object['tool'] == 'N':
                                        drawings_N.append([x, y, r, labels['N'], detail])

                    except KeyError:
                        continue
                # return lists to JSON string format prior to writing them to file
                drawings_0 = json.dumps(drawings_0)
                drawings_1 = json.dumps(drawings_1)
                #....
                drawings_N = json.dumps(drawings_N)
#  __________________________________________________________________________________________________________________

#  Block 3 More drawing tools: Line, Rectangle, Column, Triangle, Ellipse, Mixed tool types in a task.
#  While the general idea is the same for all these tool types, the dictionary elements defining the figure
#  change and we need to modify the code to handle these details.
#  For drawing tasks that use different drawing tools within the same task we have to use the tool numbers
#  defined in the project to explicitly select the code that will flatten and simplify the output. Find the
#  tool numbers by looking for the tool labels in the raw data  - there will be a one to one correspondence.
#  The data will need to be split out in columns - one column per task and drawing tool_label. Example:  two
#  drawing tasks, one with four colours of points and another with one colour of circle would require five
# field names and give five columns.


#  To use this block:
    #  First - place a line similar to this in the initialization area of a flatten_class_frame.py, with an element
        # for each tool number defined in a task. Replace 'label_X' with a short-form (single letter) designator
        # for each tool number/label in the task. Add additional lines for more drawing tasks.
                task_1_labels = {'0': 'label_0', '1': 'label_1', ...., 'N': 'label_N'}
        #  This will allow us to label each individual drawing with a short-form label that makes more sense
        # to us than just a numbers which repeats from task to task, yet is not a unwieldy as the full tool_label.
    # Secondly add appropriate field names to the list of output field names and to the writer, and assign them
        #  the values drawings_X_N.  Each task and tool number will have a separate field name and column
        #  with a list of all the drawing objects for that task and tool number as the data in the field.
    # Third copy the function definitions for the tool type(s) you need to the definition section of frame.py
    

def pull_point(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, task_label, detail]
    return drawing


def pull_circle(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    r = round(drawn_object['r'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, r, task_label, detail]
    return drawing


def pull_line(drawn_object, task_label):
    x1 = round(drawn_object['x1'], 0)
    y1 = round(drawn_object['y1'], 0)
    x2 = round(drawn_object['x2'], 0)
    y2 = round(drawn_object['y2'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x1, y1, x2, y2, task_label, detail]
    return drawing


def pull_vert_line(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, task_label, detail]
    return drawing


def pull_horz_line(drawn_object, task_label):
    y = round(drawn_object['x'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [y, task_label, detail]
    return drawing


def pull_rectangle(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    w = round(drawn_object['width'], 0)
    h = round(drawn_object['height'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, w, h, task_label, detail]
    return drawing


def pull_column(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    w = round(drawn_object['width'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, w, task_label, detail]
    return drawing


def pull_triangle(drawn_object, task_label):
    r = round(drawn_object['r'], 0)
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    a = round(drawn_object['angle'], 2)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [r, x, y, a, task_label, detail]
    return drawing


def pull_ellipse(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    rx = round(drawn_object['rx'], 0)
    ry = round(drawn_object['ry'], 0)
    a = round(drawn_object['angle'], 2)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, rx, ry, a, task_label, detail]
    return drawing
   
   
def pull_polygon(drawn_object, task_label):
    points = [[round(item['x'], 0), round(item['y'], 0)] for item in drawn_object['points']]
    if not drawn_object['closed']:
        closed = 0  #  Closed = 0, polygon is open, closed = 1 polygon is closed (or auto-closed)
    else: closed = 1
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [points, closed, task_label, detail]
    return drawing
   

def pull_bezier(drawn_object, task_label):
    points = [[round(item['x'], 0), round(item['y'], 0)] for item in drawn_object['points']]
    if not drawn_object['closed']:
        closed = 0  #  Closed = 0, polygon is open, closed = 1 polygon is closed (or auto-closed)
    else: closed = 1
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [points, closed, task_label, detail]
    return drawing
   

    # Fourth - add working block below to the main area of the frame within the iteration loop - see demo.
        #  Select the correct conditional block for each tool number in the task, one per tool number eg if the
        #  task requires two boxes and a line to be drawn there will be one of the Line blocks and two of the
        #  Rectangle blocks and the others can be deleted. Carefully match up the tasks, tool numbers, the
        #  drawing_X_N variables and the field names in the blocks and the writer.

                # pull out drawing parameters and round data.
                drawings_1_0 = []
                drawings_1_1 = []
                #....
                drawings_X_N = []
                for task in annotations: # this loop can be shared with other drawing or question blocks and
                                         # is likely already there.
                    # For every drawing task in the project set up a try block with the appropriate conditional
                    #  phrases for the drawing task label, tool types and tool numbers used in that task.
                    try:
                        if 'drawing_task_1 snippet' in task['task_label']:
                            for drawing_object in task['value']:
                                #  select conditional phrases to match the project structure and insert correct tool#'s
                                if drawing_object['tool'] is P: #  Where P is an integer - the tool number for a Point
                                    drawings_1_P.append(pull_point(drawing_object, task_label_1))

                                if drawing_object['tool'] is C: #  Where C is an integer - the tool number for a Circle
                                    drawings_1_C.append(pull_circle(drawing_object, task_label_1))

                                if drawing_object['tool'] is L: #  Where L is an integer - the tool number for a Line
                                    drawings_1_L.append(pull_line(drawing_object, task_label_1))
                                    
                                if drawing_object['tool'] is V: #  Where V is an integer - the tool number for a Full
                                    # height Line
                                    drawings_1_V.append(pull_line(drawing_object, task_label_1))
                                    
                                if drawing_object['tool'] is H: #  Where H is an integer - the tool number for a Full
                                    # width Line
                                    drawings_1_H.append(pull_line(drawing_object, task_label_1)) 
                                
                                if drawing_object['tool'] is 'R': #  Where R is an integer - the tool# for a Rectangle
                                    drawings_1_R.append(pull_rectangle(drawing_object, task_label_1))

                                if drawing_object['tool'] is 'K': #  Where K is an integer - the tool# for a column
                                    drawings_1_K.append(pull_column(drawing_object, task_label_1))

                                if drawing_object['tool'] is 'T': #  Where T is an integer - the tool# for a Triangle
                                    drawings_1_T.append(pull_triangle(drawing_object, task_label_1))

                                if drawing_object['tool'] is 'E': #  Where E is an integer - the tool# for an Ellipse
                                    drawings_1_E.append(pull_ellipse(drawing_object, task_label_1))
                                    
                                if drawing_object['tool'] is 'G': #  Where G is an integer - the tool# for an Polygon
                                    drawings_1_G.append(pull_polygon(drawing_object, task_label_1))
                                    
                                if drawing_object['tool'] is 'B': #  Where B is an integer - the tool# for an 
                                    #  Bezier curve.  This output holds all the useful information but to use it 
                                    #  will likely require reconstructing the bezier curve in a functional form y = f(x) 
                                    #  from these defining points. See above for how the points are ordered.
                                    drawings_1_B.append(pull_bezier(drawing_object, task_label_1))

                    except KeyError:
                        continue
                # return lists to JSON string format prior to writing them to file
                drawings_1_0 = json.dumps(drawings_1_0)
                drawings_1_1 = json.dumps(drawings_1_1)
                #....
                drawings_X_N = json.dumps(drawings_X_N)

#  _________________________________________________________________________________________________________________
