#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Created on 21-01-2021 09:35:27

 [Description]
"""
__author__ ="Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ ="Development"

import cv2
import numpy as np
import skimage.transform

from types import SimpleNamespace

'''
All transformations assume HWC float32 image format (following the opencv convention).
'''

interpolation = SimpleNamespace(nearest=0, bilinear=1, biquadratic=2, bicubic=3, biquartic=4, biquintic=5)
mode = SimpleNamespace(HWC="HWC", CHW="CHW")

def resize(image, size, sizeh=None, interpolation=interpolation.nearest, mode=mode.CHW):
    """ Resize image(s)

    Args:
        image (numpy.ndarray): image(s) to scale
        size (int, float): new size of the image
        sizeh (int, float) new height of the image, if given size will be used as the new width.
    Returns:
        np.ndarray: scaled image(s)
    """
    size = [size, sizeh]
    if sizeh is None:
        size[1] = size[0]

    shape = list(image.shape)
    N = len(shape) - 3
    shape[mode.index("H") + N], shape[mode.index("W") + N] = size[1], size[0]
    return skimage.transform.resize(image, shape, order=interpolation)

def scale(image, scale, scaleh=None, interpolation=interpolation.nearest, mode=mode.CHW):
    """ Scale image(s)

    Args:
        image (numpy.ndarray): image(s) to scale
        scale (int, float): scale of the image
        scaleh (int, float, optional) height scale of the image, if given scale will be used as the width scale.
    Returns:
        np.ndarray: scaled image(s)
    """
    scale = [scale, scaleh]
    if scaleh is None:
        scale[1] = scale[0]

    size = list(image.shape)
    N = len(size) - 3
    hi, wi = mode.index("H") + N, mode.index("W") + N
    size[hi], size[wi] = int(size[hi] * scale[1]), int(size[wi] * scale[0])
    return skimage.transform.resize(image, size, order=interpolation)

def colour(image, cmap=None, mode=mode.CHW):

    ci = mode.index("C") + len(image.shape) - 3

    if image.shape[ci] == 1:
        if cmap is None:
            return np.repeat(image, 3, axis=ci)
        else:
            raise NotImplementedError("TODO")
   
    return image # already colour? 

def grey(image, components=(1/3,1/3,1/3), mode=mode.CHW): #(N)HWC format
    """
        TODO Docstring
    """
    ci = mode.index("C") + len(image.shape) - 3
    assert image.shape[ci] in [1,3,4]           # wrong mode?
    assert image.shape[ci] == len(components)   # wrong components?

    z = np.array(components, dtype=np.float32)
    assert len(z.shape) == 1

    shape = [1] * len(image.shape)
    shape[ci] = z.shape[0]
    z = z.reshape(shape)

    return (image * z).sum(ci, keepdims=True)
 

'''
def crop(image, xsize=None, ysize=None, copy=True):
    """ Crop image(s).

    Args:
        image ([numpy.ndarray]): image to crop in (N)HW(C) format
        xsize ([tuple], optional): crop width (lower, upper) index. Defaults to None.
        ysize ([tuple], optional): crop height (lower, upper) index. Defaults to None.
        copy (bool, optional): Create a new array or not. Defaults to True.

    Returns:
        numpy.ndarray: cropped image(s)
    """
    image, r = nform(image)

    if xsize is None:
        xsize = (0, image.shape[2])
    if ysize is None:
        ysize = (0, image.shape[1])

    assert isinstance(xsize, tuple) and len(xsize) == 2
    assert isinstance(ysize, tuple) and len(ysize) == 2

    image = image[:,ysize[0]:ysize[1], xsize[0]:xsize[1],:]
    if copy:
        image = np.copy(image)
    return r(image)

### BELOW ONLY WORK FOR A SINGLE IMAGE - TODO

def translate(image, x, y):
    M = np.array([[1,0,x],[0,1,y]], dtype=np.float32)
    return cv2.warpAffine(image, M, (image.shape[0], image.shape[1]))

def rotate(image, theta, point=(0,0)):
    M = cv2.getRotationMatrix2D((point[1], point[0]), theta, 1)
    return cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

def affine(image, p1, p2):
    assert p1.shape == p2.shape == (2,3)
    M = cv2.getAffineTransform(p1,p2)
    return cv2.warpAffine(image ,M, (image.shape[1], image.shape[0]))

def perspective(image, p1, p2):
    assert p1.shape == p2.shape == (2,4)
    M = cv2.getPerspectiveTransform(p1, p2)
    dst = cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))


     


def binary(image, threshold=0.5, **kwargs):
    i = (int(is_integer(image)))
    m = (1.,255)[i]
    t = (threshold, 255 * threshold)[i]
    indx = image > t
    image[indx] = m
    image[np.logical_not(indx)] = 0
    return image

def to_bytes(image, ext='.png'):
    if ext is not None:
        success, image = cv2.imencode(ext, image)
        if success:
            return image.tobytes()
        else:
            raise ValueError("failed to convert image to bytes in format: {0}".format(ext))
    else:
        return image.tobytes() #just use numpy...?

#---------------- BATCH_TRANSFORMATIONS

#TODO others?

def binary_all(images, threshold=0.5):
    return binary(images, threshold=threshold)

def gray_all(image, components=(0.299, 0.587, 0.114)): #(N)HWC format
    return gray(image, components=components)

def crop_all(images, xsize=None, ysize=None, copy=False):
    if not len(images.shape) == 4 or not isHWC(images):
         raise ValueError("invalid image format: {0}, images must be in NHWC format.".format(images.shape))
    if xsize is None:
        xsize = (0,images.shape[2])
    if ysize is None:
        ysize = (0,images.shape[1])

    assert isinstance(xsize, tuple) and len(xsize) == 2
    assert isinstance(ysize, tuple) and len(ysize) == 2

    image_c = images[:,ysize[0]:ysize[1], xsize[0]:xsize[1]]
    if copy:
        return np.copy(image_c)
    return image_c





def __format_to_index__(format): # default format is HWC
    (format.index("H"), format.index("W"), format.index("C"))

'''


    
def CHW(image): #TORCH FORMAT
    '''
        Converts an image (or collection of images) from HWC to CHW format.
        CHW format is the image format used by PyTorch.
    '''
    if len(image.shape) == 2: #assume HW format
        return image[np.newaxis,:,:]
    elif len(image.shape) == 3:    
        return image.transpose((2,0,1))
    elif len(image.shape) == 4:
        return image.transpose((0,3,1,2))
    else:
        raise ValueError("invalid dimension: " + str(len(image.shape)))
    
def HWC(image): #CV2 FORMAT
    '''
        Converts an image (or collection of images) from CHW to HWC format.
        HWC format is the image format used by PIL and opencv.
    '''
    if len(image.shape) == 2:
        return image[:,:,np.newaxis]
    if len(image.shape) == 3:    
        return image.transpose((1,2,0))
    elif len(image.shape) == 4:
        return image.transpose((0,2,3,1))
    else:
        raise ValueError("invalid dimension: " + str(len(image.shape)))

def BGR(image):
    raise NotImplementedError("TODO")
    #return np.flip(image, 2) #flip around channel axis

def RGB(image):
    raise NotImplementedError("TODO") #flip around channel axis

def is_integer(image):
    return issubclass(image.dtype.type, np.integer)

def is_float(image):
    return issubclass(image.dtype.type, np.floating)

def to_float(image):
    if is_float(image):
        return image.astype(np.float32)
    elif is_integer(image):
        return image.astype(np.float32) / 255.
    else:
        return TypeError("Invalid array type: {0} for float32 conversion.".format(image.dtype))

def to_integer(image):
    if is_integer(image):
        return image.astype(np.uint8) #check overflow?
    elif is_float(image):
        return (image * 255.).astype(np.uint8) 
    else:
        return TypeError("Invalid array type: {0} for uint8 conversion.".format(image.dtype))

if __name__ == "__main__":
    def test_isHWC():
        a = np.random.randint(0,255,size=(10,10))
        assert not isHWC(a)
        a = np.random.randint(0,255,size=(10,10,1))
        assert isHWC(a)
        a = np.random.randint(0,255,size=(100,10,10,1))
        assert isHWC(a)
    test_isHWC()

