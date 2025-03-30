from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_data(image_path):
    """
    Extracts EXIF metadata from an image and returns it in a dictionary.
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            metadata = {}
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                metadata[tag_name] = value
            return metadata
        return None
    except (AttributeError, KeyError, IndexError) as e:
        # If there are no EXIF data or any other errors
        return None