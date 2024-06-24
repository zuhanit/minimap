import mpqapi
import logging
import cv2
import graphic
import os

from chk import CHK


logging.getLogger().setLevel(logging.INFO)

MPQ = mpqapi.MPQ()

path = input("Drop Starcraft map here or put path.\n")

if not os.path.isfile(path):
    raise WindowsError("Cannot find file.")

r = MPQ.Open(path)
scenario = MPQ.Get("staredit\\scenario.chk")

chk = CHK()
chk.loadchk(scenario)

renderer = graphic.Renderer("platform")
map_img = renderer.render_map(chk)

output_path = input("Please enter the file name to save.\n")

cv2.imwrite(f"{output_path}.png", map_img)
