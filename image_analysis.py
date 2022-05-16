import logging
from datetime import datetime

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


class SatelliteImage():
    def __init__(self, np_arr_filename: str, date: datetime, id: str, resources_folder: str) -> None:
        self.NB_CLUSTERS = 3
        self.np_arr_filename = np_arr_filename
        self.date = date
        self.id = id
        self._resources_folder = resources_folder
        self.np_arr = self.__to_np_arr()
        self.rgb_img = self.__to_rgb_img()
        self.rgb_img_filename = self.np_arr_filename.replace("arr", "png")
        self.rgb_save()

    def __to_np_arr(self) -> np.ndarray:
        """
        Reads np array from disk and transforms data with max/min according to the dataset rules
        """
        logging.info("Creating numpy array from bytes response...")
        with open(self.np_arr_filename, "rb") as f:
            arr = np.lib.format.read_array(f)
        arr = np.array(arr.tolist())

        arr[arr < 0] = 0
        arr[arr > 0.3] = 0.3
        arr = (255 * (arr / 0.3)).astype('uint8')

        return arr

    def __to_rgb_img(self) -> Image:
        img = Image.fromarray(self.np_arr, 'RGB')
        return img
    
    def rgb_save(self) -> None:
        self.rgb_img.save(self.rgb_img_filename)

    def run_color_analysis(self) -> None:
        self.prepare()
        self.p_and_c_analysis()
        self.make_bar_chart()
        self.make_final_output()

    def prepare(self) -> np.ndarray:
        """
        Reduce image size and reshape data to make it analyzable
        """
        tmp_arr = self.np_arr.copy()
        logging.info(f"Original image shape: {tmp_arr.shape}")

        tmp_arr = cv2.resize(tmp_arr, (200, 200), interpolation=cv2.INTER_AREA)
        logging.info(f"After resizing image: {tmp_arr.shape}")

        self.flat_arr = np.reshape(tmp_arr, (-1, 3))
        logging.info(f"After Flattening array: {self.flat_arr.shape}")

        return self.flat_arr

    def p_and_c_analysis(self) -> list[dict]:
        """
        Perform a cluster analysis to find the 3 dominant colors in the sat img,
        along with their percentage presence 
        """
        kmeans = KMeans(n_clusters=self.NB_CLUSTERS, random_state=0)
        kmeans.fit(self.flat_arr)

        percentages = np.unique(kmeans.labels_, return_counts = True)[1] / self.flat_arr.shape[0]
        dominant_colors = np.array(kmeans.cluster_centers_, dtype="uint")

        self.p_and_c = [
            {
                'percent': percent,
                'rgb': rgb,
            } for percent, rgb in sorted(zip(percentages, dominant_colors), reverse=True)
        ]

        return self.p_and_c

    def make_block_graph(self) -> str:
        """
        Make plot containing the RGB colors of the 3 dominant colors along with their percentage
        """
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        file_name_box = f"{self._resources_folder}/dominant_colors_percent_{curr_date}_{self.id}.svg"

        block = np.ones((50, 50, self.NB_CLUSTERS), dtype="uint")
        plt.figure(figsize=(18, 9))

        for i, color in enumerate(self.p_and_c):
            block[:] = color['rgb']

            plt.subplot(1, self.NB_CLUSTERS, i+1)
            plt.imshow(block)
            plt.xticks([])
            plt.xlabel(
                str(round(color['percent']*100, 2))+"%",
                fontsize=50
            )
            plt.yticks([])

        plt.savefig(file_name_box)
        plt.clf()

        return file_name_box

    def make_bar_chart(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        file_name_bar = f"{self._resources_folder}/dominant_colors_bar_{curr_date}_{self.id}.svg"

        bar = np.ones((50, 500, self.NB_CLUSTERS), dtype="uint")
        plt.figure(figsize=(12, 9))
        plt.title("Proportions of colors in the image")

        start = 0
        for color in self.p_and_c:
            end = start + (color['percent'] * bar.shape[1])
            bar[:, round(start):round(end)] = color['rgb']
            start = end

        plt.imshow(bar)
        plt.xticks([])
        plt.yticks([])

        plt.savefig(file_name_bar)
        plt.clf()

        return file_name_bar

    def make_final_output(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        file_name_final = f"{self._resources_folder}/image_with_blocks_{curr_date}_{self.id}.png"

        tmp_arr = self.np_arr.copy()
        rows = tmp_arr.shape[1]
        cols = tmp_arr.shape[0]

        cv2.rectangle(
            tmp_arr,
            (rows//2-250, cols//2-90),
            (rows//2+250, cols//2+110),
            (255, 255, 255),
            -1
        )
        cv2.putText(
            tmp_arr,
            "Most dominant colors in the satellite image",
            (rows//2-230, cols//2-40),
            cv2.FONT_HERSHEY_DUPLEX,
            0.64,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )

        start = rows//2-220
        for i, color in enumerate(self.p_and_c):
            end = start + 135
            tmp_arr[cols//2:cols//2+70, start:end] = color['rgb']
            cv2.putText(
                tmp_arr,
                str(i+1),
                (start+55, cols//2+45),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (0, 0, 0),
                1,
                cv2.LINE_AA
            )
            start = end + 20

        Image.fromarray(tmp_arr, 'RGB').save(file_name_final)

        return file_name_final
