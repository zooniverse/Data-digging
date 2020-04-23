

This Demo gives an example of how to call the dbscan module with sample input and output. Both demo_dbscan.py and dbscan.py must be in the current directory or dbscan.py must be in the sys path.

Note the sample data is a list as defined in Python. It can contain lists and/or tuples (or a mix for that matter) which each have at least two items in them which will be treated as an x and a y. These can be floats or integers. There can also be additional items for each point such as labels or weights. The additional info is effectively ignored by this clustering module.

In the demo eps and min_points are set and the class is called. The data is then passed using the usual instance_dot_method means usual to Python. The results are returned in the same way.

To prepare the results to write to a csv format file the json.dumps() ensure we end up with a known format usable in later scripts.
