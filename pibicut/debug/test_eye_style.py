# -*- coding: utf-8 -*-
"""Test eye style functionality"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer
)
from qrcode.image.styles.colormasks import SolidFillColorMask


def generate_qr(eye_style_class):
    """Generate QR with specific eye style"""
    qr = qrcode.QRCode(
        version=7,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=3
    )
    qr.add_data("https://test.com")
    qr.make(fit=True)
    color_mask = SolidFillColorMask(
        back_color=(255, 255, 255),
        front_color=(0, 0, 0)
    )
    img = qr.make_image(
        image_factory=StyledPilImage,
        color_mask=color_mask,
        module_drawer=SquareModuleDrawer(),  # Same body style
        eye_drawer=eye_style_class()  # Different eye style
    )
    return img.get_image()


def test_eye_styles():
    """Test that different eye styles produce different outputs"""
    print("Testing eye style functionality...")

    # Generate with different eye styles
    img_square = generate_qr(SquareModuleDrawer)
    img_circle = generate_qr(CircleModuleDrawer)
    img_rounded = generate_qr(RoundedModuleDrawer)

    # Convert to RGB
    img_square = img_square.convert('RGB')
    img_circle = img_circle.convert('RGB')
    img_rounded = img_rounded.convert('RGB')

    pixels_square = img_square.load()
    pixels_circle = img_circle.load()
    pixels_rounded = img_rounded.load()

    # Sample various points in the eye area
    differences_found = 0
    print("\nComparing eye pixels at different positions:")
    for pos in [(22, 22), (25, 25), (30, 30), (35, 35), (40, 40), (45, 45), (50, 50), (55, 55)]:
        sq = pixels_square[pos[0], pos[1]]
        ci = pixels_circle[pos[0], pos[1]]
        ro = pixels_rounded[pos[0], pos[1]]
        if sq != ci or sq != ro or ci != ro:
            print(f"  {pos}: Square={sq}, Circle={ci}, Rounded={ro} - DIFFERENT!")
            differences_found += 1
        else:
            print(f"  {pos}: All same ({sq})")

    if differences_found > 0:
        print(f"\nResult: Eye styles ARE working! Found {differences_found} different pixels.")
    else:
        print("\nResult: Eye styles may NOT be working - all pixels are the same.")

    return differences_found > 0


if __name__ == "__main__":
    test_eye_styles()
