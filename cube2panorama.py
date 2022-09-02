import os
import numpy as np

from equilib import cube2equi
from PIL import Image
from tqdm import tqdm



def read_image(img_path):
    """
    Read the image from directory and its orientation.

    :param img_path: location of the image
    :return img: image in a nparray 
    :return idx: index of image orientation
    """
    img = Image.open(img_path)
    name_list =  ['back','left','ront','ight','_top','down']
    for i in range(6):
        if img_path[-8:-4] == name_list[i]:
            idx = i #orientation
            break

    if isinstance(img, Image.Image):
        # Sometimes images are RGBA
        img = img.convert("RGB")
        img = np.asarray(img)
    assert len(img.shape) == 3, "input must be dim=3"
    assert img.shape[-1] == 3, "input must be HWC"
    img = np.transpose(img, (2, 0, 1)) #shape = (3, 2048, 2048)

    return img, idx


def load_cube(directory):
    """
    Read the cube map, convert it into structure that can be used by 'cube2equi' function.

    :param img: path of the folder that contains the 6 images
    :return: cupe map in a list
    """
    image_list = [[[],[],[],[],[],[]]]
    for file in os.listdir(directory):
        img_name = os.fsdecode(file)
        if img_name.endswith(".jpg"): 
            img_path = directory + '/' + img_name
            # print(img_path)
            
            img, idx = read_image(img_path)
            image_list[0][idx] = img
            continue
        else:
            continue

    return image_list


def cube2pano(cube_folder, filename):
    """
    Convert 6 planar images (cubemap) into a panoramic image (equirecctangular). 

    :param cube_folder: path of the folder that has the folders of cubemap
    :param filename: name of the panoramic image
    :return: a panoramic image in a nparray 
    """
    source_path = cube_folder + '/' + filename
    image_list = load_cube(source_path)

    rec_equi = cube2equi(
        cubemap = image_list,
        cube_format="list",
        height = 4000,
        width = 8000,
        mode="bilinear",
        # mode="bicubic",
        # mode="nearest",
    )
    rec_equi = np.transpose(rec_equi,(1,2,0)) #shape = (4000, 8000, 3)

    return rec_equi


def save(equi, pano_folder, filename):
    """
    Convert 6 planar images (cubemap) into a panoramic image (equirecctangular). 

    :param equi: a panoramic image in a nparray 
    :param pano_folder: path of the destination folder
    :param filename: name of the panoramic image
    :return: a panoramic image in a nparray 
    """
    im = Image.fromarray(equi)
    img_filename = pano_folder + '/' + filename + '_reconstructed' + '.jpg'
    im.save(img_filename)
    

if __name__ == '__main__':
    cube_folder = "C:/Users/96326/Desktop/result_folder"
    pano_folder = "C:/Users/96326/Desktop/pano_folder"
    if not os.path.exists(pano_folder):
        os.makedirs(pano_folder)

    for file in tqdm(os.listdir(cube_folder)):
        filename = os.fsdecode(file)
        
        rec_equi = cube2pano(cube_folder, filename)

        save(rec_equi, pano_folder, filename)
    
