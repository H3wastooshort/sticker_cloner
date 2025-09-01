import logging
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

from .scanner import ScannerInput
from .printer import ZebraOutput
from .crop import crop_image

from PIL import Image
import yaml
from sys import argv
config_filename = argv[1]
with open(config_filename,"r") as cf:
    config = yaml.safe_load(cf)
assert type(config) == dict

def from_file(path):
    po = ZebraOutput.from_config(config.get("printer",{}))
    img = Image.open(path)
    #img.show("Input Image")
    img = crop_image(config.get("scanner",{}),img)
    #img.show("Cropped Image")
    img = po.adjust_image(img)
    img.show("Processed Image")
    po.print_image(img,1)

def scanner_loop():
    si = ScannerInput.from_config(config.get("scanner",{}))
    po = ZebraOutput.from_config(config.get("printer",{}))
    while True:
        img=si.load_from_scanner(wait_for_document=True)
        img.show("Scanned Image")
        img = po.adjust_image(img)
        img.show("Processed Image")
        po.print_image(img,1)
if __name__ == "__main__":
    if len(argv) == 2:
        scanner_loop()
    elif len(argv) == 3:
        from_file(argv[2])
    else:
        print("arg?")