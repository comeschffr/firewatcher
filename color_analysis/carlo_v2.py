import logging
from typing import Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans


DominantColorsType = list[Tuple[np.float64, np.ndarray]]


def image_prep(img_filepath: str) -> np.ndarray:
    org_img = cv2.imread(img_filepath)
    satellite_img = org_img.copy()
    print(f"Original image shape --> {satellite_img.shape}")

    satellite_img = cv2.resize(satellite_img, (200, 200), interpolation=cv2.INTER_AREA)
    print(f"After resizing shape --> {satellite_img.shape}")

    flat_satellite_img = np.reshape(satellite_img, (-1, 3))
    print(f"After Flattening shape --> {flat_satellite_img.shape}")

    return flat_satellite_img


def p_and_c_analysis(flat_satellite_img: np.ndarray, CLUSTERS: int) -> DominantColorsType:
    kmeans = KMeans(n_clusters=CLUSTERS, random_state=0)
    kmeans.fit(flat_satellite_img)

    dominant_colors = np.array(kmeans.cluster_centers_, dtype="uint")

    percentages = np.unique(kmeans.labels_, return_counts = True)[1] / flat_satellite_img.shape[0]

    p_and_c = [
        {
            'percent': percent,
            'rgb': rgb,
        } for percent, rgb in sorted(zip(percentages, dominant_colors), reverse=True)
    ]
    print(p_and_c)
    p_and_c = zip(percentages, dominant_colors)
    p_and_c = sorted(p_and_c, reverse=True)

    # print(p_and_c)
    return p_and_c


def block_graph(p_and_c: DominantColorsType, CLUSTERS: int) -> str:
    file_name_box = "color_analysis/final_v2/dominant_colors_p.eps"
   
    block = np.ones((50, 50, CLUSTERS), dtype="uint")
    plt.figure(figsize=(16, 8))

    for i in range(CLUSTERS):
        block[:] = p_and_c[i][1][::-1]

        plt.subplot(1, CLUSTERS, i+1)
        plt.imshow(block)
        plt.xticks([])
        plt.xlabel(
            str(round(p_and_c[i][0]*100, 2)) + "%", fontsize = 20
        )
        plt.yticks([])

    plt.savefig(file_name_box, format = 'eps')

    return file_name_box


def bar_chart(p_and_c: DominantColorsType, CLUSTERS: int) -> str:
    file_name_bar = "color_analysis/final_v2/dominant_colors.eps"
    

    bar = np.ones((50, 500, CLUSTERS), dtype="uint")
    plt.figure(figsize=(12, 9))
    plt.title("Proportions of colors in the image")

    start = 0
    for p, c in p_and_c:
        end = start + (p * bar.shape[1])
        bar[:, round(start):round(end)] = c[::-1]
        start = end

    plt.imshow(bar)
    plt.xticks([])
    plt.yticks([])

    plt.savefig(file_name_bar, format = 'eps')

    return file_name_bar


def final_output(img_filepath: str, CLUSTERS: int):
    file_name_final = "color_analysis/final_v2/output.png"

    org_img = cv2.imread(img_filepath)
    rows = org_img.shape[1]
    cols = org_img.shape[0]

    final = org_img.copy()
    cv2.rectangle(
        final,
        (rows//2-250, cols//2-90),
        (rows//2+250, cols//2+110),
        (255, 255, 255),
        -1
    )

    # final = cv2.addWeighted(org_img, 0.1, copy, 0.9, 0)
    cv2.putText(
        final,
        "Most dominant colors in the satellite image",
        (rows//2-230, cols//2-40),
        cv2.FONT_HERSHEY_DUPLEX,
        0.64,
        (0, 0, 0),
        1,
        cv2.LINE_AA
    )

    start = rows//2-220
    for i in range(CLUSTERS):
        end = start + 135
        final[cols//2:cols//2+70, start:end] = p_and_c[i][1]
        cv2.putText(
            final,
            str(i+1),
            (start+55, cols//2+45),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )
        start = end + 20

    cv2.imwrite(file_name_final, final)

    return file_name_final


def rgb_values(dominant_colors: DominantColorsType) -> str:
    return (
        "The RGB values for the 3 dominant colors are: \n" +
        str(dominant_colors[0]) + "\n" + str(dominant_colors[1]) + "\n" + str(dominant_colors[2])
    )


####################################################################################################

img_filepath = "color_analysis/satellite_image.png"
# img_filepath = "satellite_image.png"
flat_satellite_img = image_prep(img_filepath)

CLUSTERS = 3

p_and_c = p_and_c_analysis(flat_satellite_img, CLUSTERS)

file_name_box = block_graph(p_and_c, CLUSTERS)

file_name_bar = bar_chart(p_and_c, CLUSTERS)

file_name_final = final_output(img_filepath, CLUSTERS)

col_rgb = rgb_values(p_and_c)
# print(col_rgb)

