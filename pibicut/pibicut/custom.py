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
    ImageColorMask,
    SolidFillColorMask
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

# Module drawer mapping
MODULE_DRAWERS = {
    "Square": SquareModuleDrawer,
    "Gapped Square": GappedSquareModuleDrawer,
    "Circle": CircleModuleDrawer,
    "Rounded": RoundedModuleDrawer,
    "Vertical Bars": VerticalBarsDrawer,
    "Horizontal Bars": HorizontalBarsDrawer,
}


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    if not hex_color:
        return None
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return None


def get_qrcode(input_data, logo=None, size="Medium", module_style="Gapped Square",
               eye_style="Square", module_color="#4682B4", eye_color="#000000"):
    """
    Generate a styled QR code with customizable options.

    Args:
        input_data: The data to encode in the QR code
        logo: Optional path to logo image to embed
        size: Size option - "Small", "Medium", or "Large"
        module_style: Style for body dots - "Square", "Gapped Square", "Circle", etc.
        eye_style: Style for corner eyes - "Square", "Gapped Square", "Circle", etc.
        module_color: Hex color for body dots (e.g., "#4682B4")
        eye_color: Hex color for corner eyes (e.g., "#000000")

    Returns:
        Base64 encoded PNG image as data URL
    """
    # Get size configuration
    config = SIZE_CONFIG.get(size, SIZE_CONFIG["Medium"])

    qr = qrcode.QRCode(
        version=config["version"],
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=config["box_size"],
        border=3
    )
    qr.add_data(input_data)
    qr.make(fit=True)

    # Get matrix size after make() is called
    matrix_size = qr.modules_count
    border = 3

    # Get module and eye drawers
    module_drawer_class = MODULE_DRAWERS.get(module_style, GappedSquareModuleDrawer)
    eye_drawer_class = MODULE_DRAWERS.get(eye_style, SquareModuleDrawer)

    # Parse colors
    mod_rgb = hex_to_rgb(module_color) or (70, 130, 180)  # Default steelblue
    eye_rgb = hex_to_rgb(eye_color) or (0, 0, 0)  # Default black

    # Color mask with solid fill for body
    color_mask = SolidFillColorMask(
        back_color=(255, 255, 255),
        front_color=mod_rgb
    )

    if logo:
        img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=color_mask,
            module_drawer=module_drawer_class(),
            eye_drawer=eye_drawer_class(),
            embeded_image_path=logo
        )
    else:
        img = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=color_mask,
            module_drawer=module_drawer_class(),
            eye_drawer=eye_drawer_class()
        )

    # Get the actual PIL image from the StyledPilImage object
    pil_img = img.get_image() if hasattr(img, 'get_image') else img

    # Apply eye color if different from module color
    if eye_rgb != mod_rgb:
        pil_img = _apply_eye_color(
            pil_img, eye_rgb, config["box_size"], border, matrix_size, mod_rgb
        )

    temp = BytesIO()
    pil_img.save(temp, "PNG")
    temp.seek(0)
    b64 = base64.b64encode(temp.read())
    return "data:image/png;base64,{0}".format(b64.decode("utf-8"))


def _apply_eye_color(img, eye_rgb, box_size, border, matrix_size, module_rgb):
    """
    Apply a different color to the QR code eyes (finder patterns).

    Args:
        img: PIL Image of the QR code
        eye_rgb: RGB tuple for eye color
        box_size: Pixels per module
        border: Border size in modules
        matrix_size: QR matrix size in modules
        module_rgb: RGB tuple for module color (to identify which pixels to change)
    """
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    width, height = img.size

    # Finder pattern positions (in modules, 7x7 each)
    # Top-left, Top-right, Bottom-left
    finder_positions = [
        (border, border),  # Top-left
        (border + matrix_size - 7, border),  # Top-right
        (border, border + matrix_size - 7),  # Bottom-left
    ]

    # For each finder pattern, recolor pixels from module_rgb to eye_rgb
    for (fx, fy) in finder_positions:
        # Calculate pixel boundaries for this 7x7 finder pattern
        px_start = fx * box_size
        py_start = fy * box_size
        px_end = (fx + 7) * box_size
        py_end = (fy + 7) * box_size

        # Ensure we don't go out of bounds
        px_end = min(px_end, width)
        py_end = min(py_end, height)

        for x in range(px_start, px_end):
            for y in range(py_start, py_end):
                if x < width and y < height:
                    current_color = pixels[x, y]
                    # Check if this pixel is the module color (with some tolerance)
                    if _color_close(current_color, module_rgb, tolerance=30):
                        pixels[x, y] = eye_rgb

    return img


def _color_close(c1, c2, tolerance=30):
    """Check if two RGB colors are close within tolerance."""
    return all(abs(c1[i] - c2[i]) <= tolerance for i in range(3))


def get_qrcode_binary(input_data, logo=None, size="Medium"):
    """
    Generate a styled QR code and return as binary PNG data.

    Args:
        input_data: The data to encode in the QR code
        logo: Optional path to logo image to embed
        size: Size option - "Small", "Medium", or "Large"

    Returns:
        Binary PNG image data
    """
    # Get size configuration
    config = SIZE_CONFIG.get(size, SIZE_CONFIG["Medium"])

    qr = qrcode.QRCode(
        version=config["version"],
        error_correction=qrcode.constants.ERROR_CORRECT_H,
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
    return temp.read()
