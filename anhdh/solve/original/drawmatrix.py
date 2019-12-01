from PIL import Image
import numpy as np

def paste(background, image, position):
    x1, y1 = position
    width, height = image.size
    arr_background = np.array(background)       
    arr_image = np.array(image)      
    arr_background[ y1:y1+height, x1:x1+width ] += arr_image
    background = Image.fromarray(arr_background)
    return background

def draw_first_line(matrix, subimage):
    image = None
    current_width = 0
    special_width = 0
    for i in range(len(matrix[0]) - 1):
        idx = int(matrix[0][i])
        current_piece = subimage[idx]
        next_idx = int(matrix[0][i+1])
        current_width +=  current_piece.edge[1].points[0][0]
        next_piece = subimage[next_idx]
        if (i == 0):
            image = join_img_right(current_piece.image_pillow, next_piece.image_pillow, (current_width, 0))
        else:
            if i == len(matrix[0]) - 2: special_width = current_width
            image = join_img_right(image, next_piece.image_pillow, (current_width, 0))
    return image, special_width

def clean_img(img):
    hor, ver = img.size
    new_ver, new_hor = 0, 0
    for i in reversed(range(ver)):
        color = img.getpixel((0, i))
        if(color != (0, 0, 0, 0)):
            new_ver = i
            break

    for i in reversed(range(hor)):
        color = img.getpixel((i, 0))
        if(color != (0, 0, 0, 0)):
            new_hor = i
            break
    arr_img = np.array(img)
    arr_img = arr_img[:new_ver,:new_hor]
    img = Image.fromarray(arr_img)
    return img

def draw_matrix(matrix, subimage):
    # print(matrix)
    image, special_width = draw_first_line(matrix, subimage)
    ver, hor = matrix.shape
    temp = matrix[0][1]
    # witdth, height = subimage[0].image_pillow.size
    add_width = subimage[temp].edge[1].points[0][0]

    write_down = True
    current_height = 0
    current_width = 0
    for i in range(1, ver):
        for j in range(hor):
            if j == 0: 
                write_down = True
                current_width = 0
            idx = matrix[i][j]
            if idx ==  None: 
                current_width+= add_width
                continue
            current_piece = subimage[idx]
            if write_down:
                before_idx = matrix[i-1][j]
                before_piece = subimage[before_idx]
                current_height +=  before_piece.edge[2].points[0][1] -  current_piece.edge[0].points[0][1] 
                write_down = False               
            else:
                current_width +=  current_piece.edge[1].points[0][0]

            if j == hor - 1:
                current_width = special_width
            
            image = join_img_down(image, current_piece.image_pillow, (current_width, current_height))
            # image.show()
    image = clean_img(image)
    image.show()
    return image

def join_img_right(image1, image2, position):
    width1, height1 = image1.size
    width2, height2 = image2.size

    image = Image.new('RGBA', (width1 + width2, max(height1, height2)))
    image = paste(image, image1, (0, 0))
    image = paste(image, image2, position)
    return image

def join_img_down(image1, image2, position):
    width1, height1 = image1.size
    width2, height2 = image2.size

    image = Image.new('RGBA', (max(width1,width2), height1 + height2))
    image = paste(image, image1, (0, 0))
    image = paste(image, image2, position)
    return image