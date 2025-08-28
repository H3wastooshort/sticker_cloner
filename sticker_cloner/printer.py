import logging
logger = logging.getLogger(__name__)

from zebra import Zebra
from PIL import Image, Resampling, Dither

class ScannerInput:
    def __init__(self,printer:Zebra,dot_width:int,dot_height:int):
        self.__printer=printer
        self.__width=dot_width
        self.__height=dot_height
    @classmethod
    def from_config(c, config=dict()):      
        logger.debug("init Zebra...")
        z = Zebra()
        if not "label" in config:
            logger.fatal("No label config.")
            quit()
        if not config["label"].keys() & {"width","height","direct_thermal"}:
            logger.fatal("Label config missing parameters.")
            quit()
        dpu=float(config["label"]["dpu"]) #dots per unit
        h=int(float(config["label"]["height"])*dpu)
        w=int(float(config["label"]["width"])*dpu)
        z.setup(
            direct_thermal=config["label"]["direct_thermal"],
            label_height=h,
            label_width=w
            )
        if label.get("autosense",False):
            z.autosense()
        return c(z,w,h)
    
    def adjust_image(self,img:Image):
        #border removal done by scanner.py already

        #rotate for maximum sticker area
        printer_aspect = self.__width > self.__height
        img_aspect = img.width > img.height
        if img_aspect != printer_aspect:
            img.transpose()

        if img.width > img.height:
            nw = self.__width
            ratio = nw / img.width
            nh = img.height * ratio
        else:
            nh = self.__height
            ratio = nh / img.height
            nw = img.width * ratio
        img = img.resize((nw,nh),Resampling.BICUBIC)
        
        #adjust printer size to multiples of 8
        w8 = img.width + 8 - (img.width%8)
        h8 = img.height + 8 - (img.width%8)
        #make image of printer size
        img8 = Image((w8,h8))
        #paste scanned image centered
        wd = (w8 - img.width) / 2
        hd = (h8 - img.height) / 2
        img8.paste(img,(wd,hd))
        img=img8

        #convert to 1bit
        img=img.convert("1",Dither.FLOYDSTEINBERG)
        
        return img
    
    def print_image(self,img:Image,qty:int):
        assert img.width%8 == 0
        assert img.height%8 == 0
        assert qty < 100
        self.__printer.print_graphic(0, 0, img.width, img.height, img.tobytes(), qty)