import numpy as np
import cv2


def loadMask(path):
    img = cv2.imread(path, 0)
    print(img)
    mask = img != 0
    return mask + 0


def crescentMask(center, area, outer_radius, pixel_angle, border):

    # Minimum inner pixel radius of the crescent
    min_inner_radius = (1 - 2 * area) * outer_radius

    # Define indices relative to center
    y, x = np.indices((512, 512))
    y = y - center[0]
    x = x - center[1]

    # Define angle array
    angle = np.arctan2(y, x)
    angle -= np.radians(pixel_angle)
    angle[angle < -np.pi / 2] += 2 * np.pi

    # Define distance array
    dist = np.sqrt(x ** 2 + y ** 2)

    # Define crescent relative to angle and dist arrays
    crescent = (
        (angle > 0)
        & (angle < np.pi)
        & (
            dist
            > (
                (min_inner_radius * outer_radius)
                / np.sqrt(
                    (min_inner_radius * np.cos(angle)) ** 2
                    + (outer_radius * np.sin(angle)) ** 2
                )
            )
        )
        & (dist < outer_radius)
    )

    # Add a border around the mask to show more
    if border > 0:
        y, x = np.indices((border * 2 - 1, border * 2 - 1))
        kernel = np.array(
            np.sqrt((y - border + 1) ** 2 + (x - border + 1) ** 2) < border,
            dtype=np.uint8,
        )

        crescent = cv2.dilate(np.array(crescent, dtype=np.uint8), kernel)

    return 1 - crescent


def outerMask(center, outer_radius, border):

    # Define indices relative to center
    y, x = np.indices((512, 512))
    y = y - center[0]
    x = x - center[1]

    # Define mask by distance to center
    mask = np.sqrt(y ** 2 + x ** 2) < (outer_radius + border)

    return mask


def cloudMask(center, area, radius, angle):

    # Cloud mask is a combination of crescent and outer mask with fixed borders
    mask = crescentMask(center, area, radius, angle, 35) * outerMask(center, radius, 20)
    return mask
