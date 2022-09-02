import os
import numpy as np

from equilib import equi2cube
from PIL import Image
from tqdm import tqdm



def load_image(folder_path):
    """
    Load panoramic images from a folder, store as a dict: {img_name: Image}. 

    :param folder_path: the path of the folder that contains the panoramic images 
    :return: the dict of images
    """
    image_stack = {}
    for file in os.listdir(folder_path):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg"): 
            img_path = folder_path + '/' + filename
            # print(img_path)
            img = Image.open(img_path)
            image_stack[filename] = img
            continue
        else:
            continue
    return image_stack


def preprocess(img):
    """
    Process the Image object, convert it into suitable object that can be used by 'equi2cube' function.

    :param img: Image object
    :return: processed images
    """

    if isinstance(img, Image.Image):
        # Sometimes images are RGBA
        img = img.convert("RGB")
        img = np.asarray(img)
    assert len(img.shape) == 3, "input must be dim=3"
    assert img.shape[-1] == 3, "input must be HWC"
    img = np.transpose(img, (2, 0, 1))
    return img


def rearrange_list(img):
    """
    Convert the result into a nparray.

    :param img: resulting list from equi2cube
    :return: processed nparray
    """

    img = np.transpose(np.squeeze(np.array(img)),(0,2,3,1))
    return img


def pano2cube(img):
    """
    Convert a panoramic image (equirecctangular) into 6 planar images (cubemap). 

    :param img: a panoramic image (nparray)
    :return: a list of 6 images
    """

    img = preprocess(img) #shape = (3, row, column) = (3, 4000, 8000)

    cube = equi2cube(
            equi = img[None],
            rots = [{"roll": 0, "pitch": 0, "yaw": 0}],
            w_face = 2048,
            cube_format = "list",
            mode = "bilinear",
            #mode="bicubic",
            #mode="nearest",
        )

    result = rearrange_list(cube) #shape = (6, w_face, w_face, 3)

    return result


def save(result_folder, result, im_name, flag):
    """
    Save planar images into a folder with the name as the orignal panoramic image.

    :param result_folder: path of the destination folder
    :param result: a list of 6 images
    :param im_name: name of the original panoramic image
    :param flag: whether save all 6 images (flag == 'all') or only 4 side images (flag == 'side'). 
    :return: 
    """

    directory = result_folder + '/' + im_name
    directory = directory[:-4]
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    orientation = ['back','left','front','right','top','down']
    for i in range(6):
        if i >= 4 and flag == 'side':
            print("Warning! You will not be able to reconstruct the panoramic image with only side images. You may want to change the flag to 'all'.")
            break
        img_filename = directory + '/' + im_name[:-4]+ '_' + orientation[i] + '.jpg'
        im = Image.fromarray(result[i])
        im.save(img_filename)

    return


if __name__ == "__main__":
    image_folder = "C:/Users/96326/Desktop/test_folder"
    result_folder = "C:/Users/96326/Desktop/result_folder"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    image_stack = load_image(image_folder)

    for name in tqdm(image_stack):
        img = image_stack[name]
        result = pano2cube(img)
        
        save(result_folder, result, name,flag='all')
    