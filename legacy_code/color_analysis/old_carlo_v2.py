import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import imutils
import os

CLUSTERS = 3

org_img = cv2.imread('color_analysis/satellite_image.png')
satellite_img = org_img.copy()
print('Original image shape --> ',satellite_img.shape)

satellite_img = imutils.resize(satellite_img, height=200)
print('After resizing shape --> ',satellite_img.shape)

flat_satellite_img = np.reshape(satellite_img, (-1,3))
print('After Flattening shape --> ', flat_satellite_img.shape)

kmeans = KMeans(n_clusters=CLUSTERS, random_state=0)
kmeans.fit(flat_satellite_img)

dominant_colors = np.array(kmeans.cluster_centers_, dtype='uint')

percentages = (np.unique(kmeans.labels_, return_counts = True)[1])/flat_satellite_img.shape[0]
p_and_c = zip(percentages, dominant_colors)
p_and_c = sorted(p_and_c, reverse=True)

block = np.ones((50, 50, 3), dtype='uint')
plt.figure(figsize=(12, 8))
for i in range(CLUSTERS ):
    plt.subplot(1, CLUSTERS, i+1)
    block[:] = p_and_c[i][1][::-1] 
    plt.imshow(block)
    plt.xticks([])
    plt.yticks([])
    plt.xlabel(str(round(p_and_c[i][0]*100,2)) + '%')
    plt.savefig('color_analysis/final_v2/dominant_colors_%.png')

bar = np.ones((50, 500, 3), dtype='uint')
plt.figure(figsize=(12, 8))
plt.title('Proportions of colors in the image')
start = 0
i = 1
for p, c in p_and_c:
    end = start + int(p * bar.shape[1])
    if i == CLUSTERS:
        bar[:, start:] = c[::-1]
    else:
        bar[:, start:end] = c[::-1]
    start = end
    i += 1

plt.imshow(bar)
plt.xticks([])
plt.yticks([])

rows = org_img.shape[1]
cols = org_img.shape[0]

copy = org_img.copy()
cv2.rectangle(copy, (rows//2-250, cols//2-90), (rows//2+250, cols//2+110), (255,255,255), -1)

final = cv2.addWeighted(org_img, 0.1, copy, 0.9, 0)
cv2.putText(final, 'Most dominant colors in the satellite image', (rows//2-230, cols//2-40), cv2.FONT_HERSHEY_DUPLEX, 0.64, (0, 0, 0),1 ,cv2.LINE_AA)


start = rows//2-220
for i in range(CLUSTERS):
    end = start+135
    final[cols//2:cols//2+70, start:end] = p_and_c[i][1]
    cv2.putText(final, str(i+1), (start+55, cols//2+45), cv2.FONT_HERSHEY_DUPLEX, 1 , (0, 0, 0),1 , cv2.LINE_AA)
    start = end+20

plt.savefig('color_analysis/final_v2/dominant_colors.png')

cv2.imwrite('color_analysis/final_v2/output.png', final)

print('The RGB values for the 3 dominant colors are: ', os.linesep, dominant_colors[0], os.linesep, dominant_colors[1], os.linesep, dominant_colors[2])
