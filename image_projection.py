import laspy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#pano_000030_000568
camera_position = np.array([561742.673, 196432.121, 60.342]) 
pitch = -2.39499
heading = 53.92245
roll = -0.84353
img = mpimg.imread('C:/Users/96326/Desktop/568/pano_000030_000568.back.jpg')

#pano_000030_000580
# camera_position = np.array([561711.999, 196411.123, 60.075])
# pitch = -2.31015
# heading = 54.9393
# roll = -1.42075
# img = mpimg.imread('C:/Users/96326/Desktop/pano_000030_000580_back.jpg')

#data from RW
camera_position = np.array([561742.78, 196432.15, 60.19]) #pano_000030_000568

def scale_points(data, flag):
    """
    Scale the data read in from .las 

    :param data: point coordinates 
    :param flag: whether it is x coordinate, y coordiante or z coordinate
    :return: scaled point coordiantes
    """
    flags = {'X':0, 'Y':1, 'Z':2}
    idx = flags[flag]
    return (data*inFile.header.scale[idx]+inFile.header.offset[idx])

def to_unit(v):
    """
    Normalise a vector into a unit vector

    :param v: original vector
    :return: unit vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return False
    return v/norm

def get_direction(pitch, heading):
    """
    Calcualte the camera pose vector from pitch and heading angle

    :param pitch: pitch angle
    :param heading: heading angle
    :return: direction vector
    """
    tan_pitch = np.tan(-pitch * np.pi/180)
    tan_heading = np.tan(heading * np.pi/180)
    direction_x = tan_heading
    direction_z = tan_pitch * np.sqrt(1+direction_x**2)
    direction = np.array([direction_x,1,direction_z])
    direction = to_unit(direction)
    return direction

def angle_between(v1,v2):
    """
    Calculate the angle between two vectors 

    :param v1: vector 1
    :param v2: vector 2
    :return: angle in radians
    """
    v1 = to_unit(v1)
    v2 = to_unit(v2)
    angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
    if(v1[0]*v2[1] - v1[1]*v2[0] < 0):
        angle = -angle
    return angle

def coordinates_rotation_z(data, deg):
    """
    Rotate the coordinate frame around z axis

    :param data: point coordinates
    :param deg: rotation degree
    :return: rotated coordinates
    """
    #deg being clockwise deg from original axis to new axis
    data = data.transpose()
    X = data[0]*np.cos(deg) - data[1]*np.sin(deg)
    Y = data[0]*np.sin(deg) + data[1]*np.cos(deg)
    return np.vstack((X,Y,data[2])).transpose()

def coordinates_rotation_y(data, deg):
    """
    Rotate the coordinate frame around y axis

    :param data: point coordinates
    :param deg: rotation degree
    :return: rotated coordinates
    """
    #deg being clockwise deg from original axis to new axis
    data = data.transpose()
    X = data[0]*np.cos(deg) + data[2]*np.sin(deg)
    Z = data[2]*np.cos(deg) - data[0]*np.sin(deg)
    return np.vstack((X,data[1],Z)).transpose()

def coordinates_rotation_x(data, deg):
    """
    Rotate the coordinate frame around x axis

    :param data: point coordinates
    :param deg: rotation degree
    :return: rotated coordinates
    """
    #deg being clockwise deg from original axis to new axis
    data = data.transpose()
    Y = data[1]*np.cos(deg) - data[2]*np.sin(deg)
    Z = data[1]*np.sin(deg) + data[2]*np.cos(deg)
    return np.vstack((data[0],Y,Z)).transpose()

def discard_v2(data, rgb):
    """
    Discard points that are not projected in the image

    :param data: point coordinates
    :param rgb: rgb information of the points
    :return data: coordinates of the remaining points
    :return rgb: rgb of the remaining points
    :return idx: index of the remaining points
    """
    idx = [i for i,v in enumerate(data) if (v[0]-v[1]>0) and (v[0]+v[1]>0) and (v[0]-v[2]>0) and (v[0]+v[2]>0)]
    data = data[idx,:]
    rgb = rgb[idx, :]
    return data,rgb,idx

def scale_image(array, range = 2000):
    """
    Scale the projected points to fit the image resolution

    :param array: projected points
    :param range: image resolution (square image, only take one number)
    :return: scaled array
    """
    shifted = array - min(array)
    array = shifted/max(shifted) * range
    return array



inFile = laspy.read("C:/Users/96326/Desktop/HE-PHASE-2_A12_Area_561734_196448_subsampled10.las")
points_record = inFile.points
pointformat = inFile.point_format
specname = []
for spec in inFile.point_format:
    specname.append(spec.name)
#print(specname)

coordinates = np.vstack((scale_points(inFile.X,'X'), scale_points(inFile.Y,'Y'), scale_points(inFile.Z,'Z'))).transpose()
rgb = np.vstack((inFile.red, inFile.green, inFile.blue)).transpose()/100000
moved_data = coordinates - camera_position #shift the coordinate

direction = get_direction(pitch, heading) #calcualte the camera pose vector

#data from RW
# direction = np.array([0.81, 0.59, 0.04])

#rotate the coordinate system
degZ = angle_between(direction[:2],np.array([1,0]))
degY = angle_between(np.delete(direction,1), np.array([1,0]))

moved_z_data = coordinates_rotation_z(moved_data, degZ)
moved_y_data = coordinates_rotation_y(moved_z_data, degY)
moved_x_data = coordinates_rotation_x(moved_y_data, roll)

#discard unnecessary points
c_v2, rgb_v2, idx_v2 = discard_v2(moved_y_data, rgb)
c_v2_trans = c_v2.transpose()

#project the points 
y_image = np.divide(c_v2_trans[2], c_v2_trans[0])
x_image = np.divide(c_v2_trans[1], c_v2_trans[0])

x_image_scale = scale_image(-x_image,img.shape[0])
y_image_scale = img.shape[1]-scale_image(y_image,img.shape[1])

imgplot = plt.imshow(img)
plt.scatter(-x_image_scale,y_image_scale, c=rgb_v2, s=0.1, alpha = 0.25)
plt.scatter(x_image_scale,y_image_scale, c=rgb_v2, s=0.1, alpha = 0.25)
plt.show()