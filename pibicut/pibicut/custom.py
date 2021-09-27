# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt
import frappe

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SquareGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask, ImageColorMask

from PIL import Image
import base64, os
from io import BytesIO

def get_qrcode(input_data, logo):
  qr = qrcode.QRCode(
        version=7,
        box_size=6,
        border=3
  )
  qr.add_data(input_data)
  qr.make(fit=True)
  path = frappe.utils.get_bench_path()
  site_name = frappe.utils.get_url().replace("http://","").replace("https://","")
  if ":" in site_name:
    pos = site_name.find(":")
    site_name = site_name[:pos]
  
  if logo:
    embedded = os.path.join(path, "sites", site_name, 'public', logo[1:])
    img = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask(back_color = (255,255,255), center_color = (70,130,180), edge_color = (0,0,0)), module_drawer=GappedSquareModuleDrawer(), eye_drawer=SquareModuleDrawer(), embeded_image_path=embedded)
  else:
    img = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask(back_color = (255,255,255), center_color = (70,130,180), edge_color = (0, 0, 0)), module_drawer=GappedSquareModuleDrawer(), eye_drawer=SquareModuleDrawer())
  #qr = qrcode.make(input_str)
  temp = BytesIO()
  img.save(temp, "PNG")
  temp.seek(0)
  b64 = base64.b64encode(temp.read())
  return "data:image/png;base64,{0}".format(b64.decode("utf-8"))