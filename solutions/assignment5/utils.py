import numpy as np
import cv2

""" transform the image using the homography H 
    the size of the final image is decide using
    the bounds -> (left, top, right, bottom)
    The left, top of the input image is translated 
    to (0,0).
"""
def warp_image_with_bounds(img, H, bounds):
    
    # translation of left, top to (0,0)
    t = [-bounds[0],-bounds[1]]
    Ht = np.array([[1,0,t[0]],[0,1,t[1]],[0,0,1]]) # translation transform
    
    result = cv2.warpPerspective(img, Ht.dot(H), 
                                 (bounds[2]-bounds[0], bounds[3]-bounds[1]))
    
    return result
