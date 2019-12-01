import cv2
import numpy as np

def get_contours(image):
    imgray = cv2.cvtColor(image ,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,20,255,0)
    contours, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=lambda cnt: len(cnt))
    return contours[0]

def get_hor_edge(image):   
    ver, hor = image.shape
    arr = []
    for i in range(ver):
        x1, y1, x2, y2 = None, None, None, None
        for j in range(hor):
            if image[i][j] != 255: continue
            if  x1 is None:
                x1, y1 = i, j
                continue
            else:
                if j != hor - 1:
                    next_ = image[i][j+1]
                    if next_ != 255:
                        x2, y2 = i, j
                        if(y2 - y1) > 20:
                            arr.append((y1, x1, y2, x2))
                            x1, y1, x2, y2 = None, None, None, None
                        else:
                            x1, y1, x2, y2 = None, None, None, None
                else:
                    x2, y2 = i, j
                    if(y2 - y1) > 20:
                        arr.append((y1, x1, y2, x2))
                    x1, y1, x2, y2 = None, None, None, None
    return arr

def get_ver_edge(image):
    ver, hor = image.shape
    arr = []
    for i in range(hor):
        x1, y1, x2, y2 = None, None, None, None
        for j in range(ver):
            color = image[j][i]
            if color != 255: continue
            if  x1 is None:
                x1, y1 = i, j
                continue
            else:
                if j != ver - 1:
                    next_ = image[j+1][i]
                    if next_ != 255:
                        x2, y2 = i, j
                        if(y2 - y1) > 20:
                            arr.append((x1, y1, x2, y2))
                            x1, y1, x2, y2 = None, None, None, None
                        else:
                            x1, y1, x2, y2 = None, None, None, None
                else:
                    x2, y2 = i, j
                    if(y2 - y1) > 20:
                        arr.append((x1, y1, x2, y2))
                    x1, y1, x2, y2 = None, None, None, None
    return arr


def get_hor(horizontal):
    cols = horizontal.shape[1]
    horizontal_size = cols // 30
    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    return horizontal

def get_ver(vertical):
    rows = vertical.shape[0]
    verticalsize = rows // 30
    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)
    
    return vertical

def get_point_edge(contours, shape):
    contour_img = np.zeros(shape, np.uint8)
    cv2.drawContours(contour_img,contours,-1,(255),1)
    
    gray = cv2.bitwise_not(contour_img)
    bw = cv2.adaptiveThreshold(contour_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                cv2.THRESH_BINARY, 15, -2)
    
    horizontal = np.copy(bw)
    vertical = np.copy(bw)

    horizontal = get_hor(horizontal)
    vertical = get_ver(vertical)

    
    arr_hor = get_hor_edge(horizontal)
    arr_ver = get_ver_edge(vertical)
    
    return arr_hor, arr_ver
    # return sorted(arr_hor, key=lambda x: (arr_hor.index(x[2]-x[0]), x[0]), reverse=True), sorted(arr_ver, key=lambda x: (x[3]-x[1], x[1]), reverse=True)


def get_test_img(arr_hor, arr_ver, shape):
    blank_image = np.zeros(shape, np.uint8)
    for x1, y1, x2, y2 in arr_hor:
        cv2.line(blank_image, (x1, y1), (x2, y2), (255,0 ,0), 2)


    for x1, y1, x2, y2 in arr_ver:
        cv2.line(blank_image, (x1, y1), (x2, y2), (255,0 ,0), 2)
    cv2.imwrite("ahihi.png", blank_image)
    return blank_image

def test_4_edges(path, shape, sideUp, sideDown, sideRight, sideLeft):
    blank_image = np.zeros(shape, np.uint8)
    for i, j in sideUp:
        blank_image[j][i] = np.asarray([0, 0, 255])
    for i, j in sideDown:
        blank_image[j][i] = np.asarray([0, 255, 0])
    for i, j in sideLeft:
        blank_image[j][i] = np.asarray([255, 0, 0])
    for i, j in sideRight:
        blank_image[j][i] = np.asarray([0, 255, 255])
    cv2.imwrite(path, blank_image)

def create_array_from_2_points_hor(pts1, pts2, contour_arr, denta=2, denta2=24):
    temp = [ (i, pts1[1]) for i in range(pts1[0], pts1[2] - denta)]
    temp += [ (i, pts2[1]) for i in range(pts2[0] + denta, pts2[2])]

    for i in range(pts1[2] - denta, pts2[0] + denta):
        for j in range(pts2[1] - denta2, pts2[1] + denta): # hardcode cho nay cho phan duoi nhieu phan tren it
            temp.append((i, j))
    # return [item for item in temp if item  in contour_arr]
    return list(set(temp).intersection(contour_arr))
    
def create_array_from_2_points_ver(pts1, pts2, contour_arr, denta=2, denta2=24):
    temp = [ (pts1[0], i) for i in range(pts1[1], pts1[3] - denta)]
    temp += [ (pts2[0], i) for i in range(pts2[1] + denta, pts2[3])]

    for i in range(pts1[3] - denta, pts2[1] + denta):
        for j in range(pts2[2] - denta, pts2[2] + denta2): # hardcode cho nay cho phan duoi nhieu phan tren it
            temp.append((j, i))
    # return [item for item in temp if item  in contour_arr]
    return list(set(temp).intersection(contour_arr))