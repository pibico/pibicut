# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt
import frappe

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask,
    ImageColorMask
)

from PIL import Image
import base64
import os
from io import BytesIO


# QR code size configurations
SIZE_CONFIG = {
    "Small": {"box_size": 4, "version": 5},
    "Medium": {"box_size": 6, "version": 7},
    "Large": {"box_size": 10, "version": 7},
}


def get_qrcode(input_data, logo=None, size="Medium"):
    """
    Generate a styled QR code with optional logo and size options.

    Args:
        input_data: The data to encode in the QR code
        logo: Optional path to logo image to embed
        size: Size option - "Small", "Medium", or "Large"

    Returns:
        Base64 encoded PNG image as data URL
    """
    # Get size configuration
    config = SIZE_CONFIG.get(size, SIZE_CONFIG["Medium"])

    qr = qrcode.QRCode(
        version=config["version"],
        box_size=config["box_size"],
        border=3
    )
    qr.add_data(input_data)
    qr.make(fit=True)

    # Color mask settings
    color_mask = RadialGradiantColorMask(
        back_color=(255, 255, 255),
        center_color=(70, 130, 180),
        edge_color=(0, 0, 0)
    )

    if logo:
        img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=color_mask,
            module_drawer=GappedSquareModuleDrawer(),
            eye_drawer=SquareModuleDrawer(),
            embeded_image_path=logo
        )
    else:
        img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=color_mask,
            module_drawer=GappedSquareModuleDrawer(),
            eye_drawer=SquareModuleDrawer()
        )

    temp = BytesIO()
    img.save(temp, "PNG")
    temp.seek(0)
    b64 = base64.b64encode(temp.read())
    return "data:image/png;base64,{0}".format(b64.decode("utf-8"))
