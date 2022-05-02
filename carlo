
# I selected Python 3.9.7 ('base') as environment and imported all of the modules that were missing

import matplotlib.image as img
import matplotlib.pyplot as plt
from scipy.cluster.vq import whiten, kmeans
import pandas as pd
 
# Convert the image to pixels
satellite_image = img.imread('satellite_image.jpeg')
 
'''
We are collectively looking at all of the pixels and extracting the RGB values and store them in them
in their corresponding list; these are then stored onto the padas df. The df is then scaled in order
to get standardized values.
'''

# Store RGB values of all pixels in lists r, g and b
r = []
g = []
b = []
for row in satellite_image:
    for temp_r, temp_g, temp_b in row:
        r.append(temp_r)
        g.append(temp_g)
        b.append(temp_b)

# Saving as DataFrame  
satellite_image_df = pd.DataFrame({'red' : r, 'green' : g, 'blue' : b})
 
# Scaling the values
satellite_image_df['scaled_color_red'] = whiten(satellite_image_df['red'])
satellite_image_df['scaled_color_blue'] = whiten(satellite_image_df['blue'])
satellite_image_df['scaled_color_green'] = whiten(satellite_image_df['green'])

'''
These next few lines of code are to find the number of clusters in the images that will be later be the
the input fot the last step where we create a plot representing the dominant colors
'''

# Preparing data to construct elbow plot.
distortions = []
num_clusters = range(1, 10)  #range of cluster sizes
 
# Create a list of distortions from the kmeans function
for i in num_clusters:
    cluster_centers, distortion = kmeans(satellite_image_df[['scaled_color_red', 'scaled_color_blue', 'scaled_color_green']], i)
    distortions.append(distortion)
     
# Create a data frame with two lists, num_clusters and distortions
elbow_plot = pd.DataFrame({'num_clusters' : num_clusters, 'distortions' : distortions})
 
# Create a line plot of num_clusters and distortions
data = elbow_plot
df = pd.DataFrame(data ,columns=['num_clusters','distortions'])
df.plot(x = 'num_clusters', y = 'distortions', kind = 'line')
plt.xticks(num_clusters)
plt.savefig('elbow_plot_clusters.png')
plt.clf()


# print('Please enter the number of clusters.')
# clusters = int(input('>>> '))

cluster_centers, _ = kmeans(satellite_image_df[['scaled_color_red', 'scaled_color_blue', 'scaled_color_green']], 3)
 
'''
Last step is to find the dominant colors and stardardize their values.
'''

dominant_colors = []
 
# Get standard deviations of each color
red_std, green_std, blue_std = satellite_image_df[['red', 'green', 'blue']].std()
 

for cluster_center in cluster_centers:
    red_scaled, green_scaled, blue_scaled = cluster_center
    # Convert each standardized value to scaled value
    dominant_colors.append((
        red_scaled * red_std / 255,
        green_scaled * green_std / 255,
        blue_scaled * blue_std / 255
    ))
 
plt.imshow([dominant_colors])
plt.axis('off')
plt.title('Dominant colors')
plt.savefig('dominant_colors.png')
plt.show()

dominant_colors_rgb = tuple(tuple(round(255 * i) for i in elem) for elem in dominant_colors)

print(dominant_colors_rgb)


'''
Creation of color database and retrieve the dominant color names.
'''

# import sqlite3

# with sqlite3.connect('color_database.db') as conn:
#     c = conn.cursor()

# c.execute("CREATE TABLE IF NOT EXISTS color_database([r] INTEGER, [g] INTEGER, [b] INTEGER)")
# conn.commit()

# c.execute('INSERT INTO color_database (r, g, b) VALUES ({}, {}, {})'.format(r, g, b)

