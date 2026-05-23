from PIL import Image, ImageChops
import io


def generate_ela_in_memory(original_img, quality=90):
    """
    Calculates the Error Level Analysis (ELA) matrix in-memory without writing to disk.

    Parameters
    ----------
    original_img : PIL.Image.Image
        The original image object to be processed. Expected to be in RGB format.
    quality : int, optional
        The JPEG compression quality level. Default is 90.

    Returns
    -------
    PIL.Image.Image
        The visual representation of the calculated ELA difference matrix.
    """
    buffer = io.BytesIO()
    original_img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    compressed_img = Image.open(buffer)

    ela_image = ImageChops.difference(original_img, compressed_img)

    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema]) if extrema else 1
    if max_diff == 0: max_diff = 1

    scale = 255.0 / max_diff
    ela_image = Image.eval(ela_image, lambda x: x * scale)

    return ela_image