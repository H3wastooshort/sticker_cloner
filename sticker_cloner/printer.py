import logging
logger = logging.getLogger(__name__)

from zebra import Zebra
from PIL import Image

class ZebraOutput:
    def __init__(self,printer:Zebra,dot_width:int,dot_height:int):
        self.__printer=printer
        self.__width=dot_width
        self.__height=dot_height
    @classmethod
    def from_config(c, config=dict()):      
        logger.debug("init Zebra...")
        z = Zebra()
        qs = z.getqueues()
        logger.debug("Printqueues:\n"+str(qs))
        if "queue" not in config:
            logger.fatal("No printqueue selected!")
            quit()
        if config["queue"] not in qs:
            logger.fatal("Printqueue '%s' not found!"%config["queue"])
            quit()
        z.setqueue(config["queue"])

        if not "label" in config:
            logger.fatal("No label config.")
            quit()
        if not config["label"].keys() & {"width","height","direct_thermal"}:
            logger.fatal("Label config missing parameters.")
            quit()
        dpu=float(config["label"]["dpu"]) #dots per unit
        h=int(float(config["label"]["height"])*dpu)
        w=int(float(config["label"]["width"])*dpu)
        g=int(float(config["label"]["gap"])*dpu)
        z.setup(
            direct_thermal=config["label"]["direct_thermal"],
            label_height=(h,g),
            label_width=w
            )
        if config["label"].get("autosense",False):
            z.autosense()
        return c(z,w,h)
    
    def adjust_image(self,img:Image):
        #border removal done by scanner.py already

        #rotate for maximum sticker area
        printer_aspect = self.__width > self.__height
        img_aspect = img.width > img.height
        if img_aspect != printer_aspect:
            img.transpose(Image.Transpose.ROTATE_90)

        if img.width > img.height:
            nw = self.__width
            ratio = nw / img.width
            nh = int(img.height * ratio)
        else:
            nh = self.__height
            ratio = nh / img.height
            nw = int(img.width * ratio)
        img = img.resize((nw,nh),Image.Resampling.LANCZOS)
        
        #adjust printer size to multiples of 8
        w8 = img.width + 8 - (img.width%8)
        h8 = img.height
        #make image of printer size
        img8 = Image.Image((w8,h8))
        #paste scanned image centered
        wd = int((w8 - img.width) / 2)
        hd = int((h8 - img.height) / 2)
        img8.paste(img,(wd,hd))
        img=img8

        #convert to 1bit
        img=img.convert("1",Image.Dither.FLOYDSTEINBERG)
        
        return img
    
    def print_image(self,img:Image,qty:int):
        assert img.width%8 == 0
        assert img.height%8 == 0
        assert qty < 100
        self.__printer.print_graphic(0, 0, img.width, img.height, img.tobytes(), qty)