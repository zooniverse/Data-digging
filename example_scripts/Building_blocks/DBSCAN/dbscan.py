class DBSCAN(object):
    def __init__(self, eps=0, min_points=2):
        self.eps = eps
        self.min_points = min_points
        self.noise = []
        self.clusters = []
        self.dp = []
        self.near_neighbours = []
        self.wp = set()
        self.proto_cores = set()
        self.points = []

    def cluster(self, points):
        c = 0
        self.dp = points
        self.near_neighbours = self.nn(points)
        while self.proto_cores:
            near_points = set(self.proto_cores)
            for p in near_points:
                c += 1
                core = self.add_core(self.near_neighbours[p])
                complete_cluster = self.expand_cluster(core)
                self.clusters.append(["Cluster: %d" % c, complete_cluster])
                self.proto_cores -= core
                break
        for pt in self.dp:
            flag = True
            for c in self.clusters:
                if pt in c[1]:
                    flag = False
            if flag:
                self.noise.append(pt)
        self.tags(self.clusters)

    # set up dictionary of near neighbours,create working_point and proto_core sets
    def nn(self, points):
        self.wp = set()
        self.proto_cores = set()
        i = -1
        near_neighbours = {}
        for p in points:
            i += 1
            j = -1
            neighbours = []
            for q in points:
                j += 1
                distance = (((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5)
                if distance <= self.eps:
                    neighbours.append(j)
            near_neighbours[i] = neighbours
            if len(near_neighbours[i]) > 1:
                self.wp |= {i}
            if len(near_neighbours[i]) >= self.min_points:
                self.proto_cores |= {i}
        return near_neighbours

    # add cluster core points
    def add_core(self, neighbours):
        core_points = set(neighbours)
        visited = set()
        while neighbours:
            points = set(neighbours)
            neighbours = set()
            for p in points:
                visited |= {p}
                if len(self.near_neighbours[p]) >= self.min_points:
                    core_points |= set(self.near_neighbours[p])
                    neighbours |= set(self.near_neighbours[p])
            neighbours -= visited
        return core_points

    # expand cluster to reachable points and rebuild actual point values
    def expand_cluster(self, core):
        core_points = set(core)
        full_cluster = []
        for p in core_points:
            core |= set(self.near_neighbours[p])
        for point_number in core:
            full_cluster.append(self.dp[point_number])
        return full_cluster

    def tags(self, cluster_list):
            for item in cluster_list:
                self.points.append((len(item[1]), self.avg_position(item[1])))
            return self.points

    def avg_position(self, list_points):
        sumx = 0
        sumy = 0
        if list_points != []:
            for n in list_points:
                sumx += n[0]
                sumy += n[1]
            avgx = int(round(sumx / len(list_points), 0))
            avgy = int(round(sumy / len(list_points), 0))
            return [avgx, avgy]
        else:
            return []
