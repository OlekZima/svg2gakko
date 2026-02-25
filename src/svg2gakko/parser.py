import base64
import os
from io import BytesIO
from pathlib import Path
import cairosvg
from PIL import Image
from svg2gakko.constants import TEMP_DIR


def _svg2jpeg(file: Path) -> Path:
    """Convert SVG image to JPEG using `cairosvg.svg2png` function. Converted file is stored inside TEMP in directory with prefix 'svg2gakko_'

    Args:
        file (Path): Path to the SVG image

    Returns:
        Path: Path to the converted JPEG image inside TEMP directory
    """
    jpeg_name = os.path.splitext(file.name)[0] + ".jpeg"
    jpeg_path = TEMP_DIR / jpeg_name

    png_data = cairosvg.svg2png(url=str(file))

    jpeg_image = Image.open(BytesIO(png_data)).convert("RGB")
    jpeg_image.save(jpeg_path, "JPEG", quality=95)

    return jpeg_path


def _jpeg2base64gakko(file: Path) -> str:
    """Convert JPEG image to Base64 HTML `<img>` tag that Gakko accepts.
    At the end of the `<img>` `<br>` tag is added.

    By default Gakko inserts `<img>` tag into `<p>` tag, so output of this function should be placed into `<p>` tag with some content

    Args:
        file (Path): Path to the JPEG image

    Returns:
        str: Base64 string like `<img style="width: {width}px" src="data:image/jpeg;base64,{bytes}"><br>`
    """
    image_width = None
    with Image.open(file) as image:
        image_width = image.size[0]

    # Return Base64 image as HMTL <img> tag + <br>
    # By default Gakko inserts <img> tag into <p> tag, so this should be placed into <p> tag with some content
    with open(file, "rb") as jpeg_image:
        base64_bytes = str(base64.b64encode(jpeg_image.read()), "utf-8")
        return (
            f'<img style="width: {image_width}px" src="data:image/jpeg;base64,{base64_bytes}"><br>'
        )


# def svg2base64gakko(file: Path) -> str:
#     image_width = None
#     with Image.open(file) as image:
#         image_width = image.size[0]

#     with open(file, "rb") as jpeg_image:
#         base64_bytes = str(base64.b64encode(jpeg_image.read()), "utf-8")
#         return f'<img style="width: {image_width}px" src="data:image/svg+xml;base64,{base64_bytes}" data-filename="{file.name}"><br>'


def svg2base64gakko(file: Path) -> str:
    """Convert SVG image to Base64 HTML `<img>` tag that Gakko accepts.
    At the end of the `<img>` `<br>` tag is added.

    By default Gakko inserts `<img>` tag into `<p>` tag, so output of this function should be placed into `<p>` tag with some content

    Args:
        file (Path): Path to the JPEG image

    Returns:
        str: Base64 string like `<img style="width: {width}px" src="data:image/jpeg;base64,{bytes}"><br>`
    """
    return _jpeg2base64gakko(_svg2jpeg(file))
