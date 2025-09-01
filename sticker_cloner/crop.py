import logging
logger = logging.getLogger(__name__)

from PIL import Image, ImageFilter
import numpy as np

def crop_image(config:dict, img:Image):
    thresh = config.get("threshold",10)

    oimg = img
    img = img.convert("L")
    bimg = img.filter(ImageFilter.GaussianBlur(5))
    #bimg.show("Blurred Image for Cropping")
    mat = np.array(bimg)
    
    #get brightest pixel per row/col
    max_x = np.max(mat,axis=0)
    max_y = np.max(mat,axis=1)

    left=None
    right=None
    top=None
    bot=None

    for i,x in enumerate(max_x):
        if x > thresh:
            left=i
            break
    for i,y in enumerate(max_y):
        if y > thresh:
            top=i
            break
    for i,x in enumerate(reversed(max_x)):
        if x > thresh:
            right=len(max_x)-1-i
            break
    for i,y in enumerate(reversed(max_y)):
        if y > thresh:
            bot=len(max_y)-1-i
            break
    
    croptup = (left,top,right,bot)
    logger.debug(croptup)

    if None in croptup:
        logger.warn("could not find thresh")
        return oimg
    if right <= left or bot <= top:
        logger.warn("invalid edges")
        return oimg
    
    return oimg.crop(croptup)


