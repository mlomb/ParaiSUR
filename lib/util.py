from skimage.io import imshow
from matplotlib import pyplot as plt


def display_image(image):
    plt.figure(figsize=(12, 12))
    plt.axis("off")
    imshow(image)
