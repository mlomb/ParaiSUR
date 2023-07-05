from deskew import determine_skew
from skimage.transform import rotate


def deskew_image(image):
    angle = determine_skew(image)  # type: ignore
    image_deskew = rotate(image, angle, resize=True)  # type: ignore
    return (image_deskew * 255).astype("uint8")  # volver a 0-255
