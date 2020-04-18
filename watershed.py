import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as ndi
from skimage import morphology,color,data,filters,io,feature,exposure


img = io.imread('Image/011.png')


image =color.rgb2gray(img)
img_c = exposure.equalize_hist(image)

denoised = filters.rank.median(img_c, morphology.disk(5)) #过滤噪声
thresh = filters.threshold_li(denoised)

binary = denoised > thresh
for i in range(10):
    binary = morphology.binary_erosion(binary)

classes = ndi.label(binary)[0]
gradient = filters.rank.gradient(denoised, morphology.disk(5))
gradient_inv = gradient.max() - gradient 
local_min = feature.peak_local_max(gradient_inv, indices=False, min_distance=35, num_peaks_per_label=1,labels=classes)
gradient_selected = np.ones(np.shape(image)) * gradient.max()
gradient_selected[local_min==True] = gradient[local_min==True]
markers = ndi.label(local_min)[0]
labels =morphology.watershed(gradient, markers,watershed_line=True,compactness=0) #基于梯度的分水岭算法
img[labels==0] = [255,0,0,255]
img[markers!=0] = [0,255,0,255]