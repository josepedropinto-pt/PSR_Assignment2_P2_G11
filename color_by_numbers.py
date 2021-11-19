#!/usr/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import cv2
#

def main(path_to_color_by_number, no_colors):
    img = cv2.imread(path_to_color_by_number, 1)
    plt.imshow(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = img.reshape((img.shape[1] * img.shape[0], 3))
    kmeans = KMeans(n_clusters= no_colors)
    s = kmeans.fit(img)

    labels = kmeans.labels_
    labels = list(labels)
    labels = sorted(labels, reverse=False)

    centroid = kmeans.cluster_centers_

    percent = []
    for i in range(len(centroid)):
        j = labels.count(i)
        j = j / (len(labels))
        percent.append(j)
    percent = sorted(percent, reverse=True)

    plt.figure(facecolor='gray')
    plt.pie(percent, colors=np.array(centroid / 255), labels=np.arange(len(centroid)))
    plt.savefig('pie_chart.png')
    return centroid


if __name__ == "__main__":
    main()
