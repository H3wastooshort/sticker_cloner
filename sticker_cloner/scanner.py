import logging
logger = logging.getLogger(__name__)

import sane
from PIL import Image
from time import sleep

class ScannerInput:
    def __init__(self,scanner:sane.SaneDev):
        self.__scanner=scanner
    def load_from_scanner(self,wait_for_document=False):
        def scan_img():
            try:
                self.__scanner.cancel()
                self.__scanner.start()
                return self.__scanner.snap(False)
            except sane._sane.error as e:
                if str(e) == 'Document feeder out of documents':
                    return None
                #if str(e) == 'Device busy':
                #    logger.warn("Scanner busy! Cancling job and retrying!")
                #    self.__scanner.cancel()
                #    sleep(3)
                #    return scan_img()
                else:
                    self.__scanner.close()
                    raise
        
        img=scan_img()
        while img==None and wait_for_document:
            logger.info("no document in ADF, sleeping for 1s...")
            sleep(1)
            img=scan_img()
        if img:
            logger.info(f"aquired {img.mode} image of size {img.size}")
        else:
            logger.error("no document in ADF")
        return img
    @classmethod
    def from_config(c, config=dict()):
        dev=config.get("device", None)
        dpi=config.get("dpi",800)
        mode=config.get("mode","color")
        depth=config.get("depth",8)
        
        logger.debug("init SANE...")
        sane.init()
        if dev:
            dev=sane.open(dev)
        else:
            logger.warn(f"no scanner device specified, falling back to 1st available")
            logger.info("looking for scanners...")
            devices = sane.get_devices()
            logger.debug(str(devices))
            dev = sane.open(devices[0][0])
            logger.warn(f"selected {dev.sane_signature}")
        try:
            dev.mode=mode
            dev.depth=depth
        except:
            logger.warn(f"unsupported options")
        return c(dev)