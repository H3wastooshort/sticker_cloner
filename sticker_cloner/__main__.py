import logging
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

from .scanner import ScannerInput
from .printer import ZebraOutput

import yaml
from sys import argv
config_filename = argv[1]
with open(config_filename,"r") as cf:
    config = yaml.safe_load(cf)
assert type(config) == dict

def main():
    si = ScannerInput.from_config(config.get("scanner",{}))
    po = ZebraOutput.from_config(config.get("printer",{}))
    while True:
        img=si.load_from_scanner(wait_for_document=True)
        img.show("Scanned Image")
        img = po.adjust_image(img)
        img.show("Processed Image")
        po.print_image(img,1)
if __name__ == "__main__":
    main()