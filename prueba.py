from sc2.position import Point2
import math

def get_intersections(a, b, r, map_center):
	dist_a_b = a.distance_to(b)
	if(dist_a_b >= 2*r):
		return a.towards(b, r)
	else: # two intersection points
		intersections = list(a.circle_intersection(b, 11))
		i1 = Point2(intersections[0])
		i2 = Point2(intersections[1])
		if i1.distance_to(map_center) < i2.distance_to(map_center):
			return i1
		return i2
		#return intersections.closest_to(map_center)

a = Point2((18,3))
b = Point2((13,19))
map_center = Point2((200,200))
