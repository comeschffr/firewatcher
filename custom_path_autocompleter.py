import readline
import os


def completer(text: str, state: int) -> str:
    last_path = os.path.dirname(
        readline.get_line_buffer().split(' ')[-1]
    )
    direntry = os.scandir('./'+last_path)
    volcab = []
    for item in direntry:
        if item.is_dir():
            volcab.append(item.name+"/")
        else:
            volcab.append(item.name+" ")
    results = [x for x in volcab if x.lower().startswith(text.lower())] + [None]
    return results[state]


readline.parse_and_bind('tab: complete')
readline.set_completer(completer)


input('>>> ')

import matplotlib.image as img
import matplotlib.pyplot as plt
from scipy.cluster.vq import whiten
from scipy.cluster.vq import kmeans
import pandas as pd
 
# Convert the image to pixels
satellite_image = img.imread('satellite_image.jpg')
 
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
    for temp_r, temp_g, temp_b, temp in row:
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
sns.lineplot(x = 'num_clusters', y = 'distortions', data = elbow_plot)
plt.xticks(num_clusters)
plt.show()

print('Please enter the number of clusters.')
clusters = input('>>>')

cluster_centers, _ = kmeans(satellite_image_df[['scaled_color_red', 'scaled_color_blue', 'scaled_color_green']], clusters)
 
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
plt.show()

