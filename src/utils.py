from PIL import Image, ImageChops
import io

def generate_ela_in_memory(original_img, quality=90):
    """
    Help on function  generate_ela_in_memory in module utils:

    generate_ela_in_memory(original_img, quality=90):
        ELA calculations are performed on RAM without writing to disk.

        Parameters
        ----------
        original_img: {JPEG, PNG, GIF}
            pass

        quality: int
            pass
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