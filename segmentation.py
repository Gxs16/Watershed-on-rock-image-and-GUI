#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
分水岭分割算法

最后编辑日期：2020-4-20
'''
import numpy as np
from scipy import ndimage as ndi
from skimage import morphology, color, filters, io, feature, exposure

def watershed(filepath, median_r, islocal, localsize,\
              local_offset, ite_erosion, gradient_r, savefilepath):
    '''
    执行分水岭图像分割算法

    param:
    filepath：目标文件的文件路径
    median_r：中值滤波核半径
    islocal：判断是否使用局部阈值选取
    localsize：局部阈值选取核半径
    local_offset：局部阈值偏移量
    ite_erosion：形态学侵蚀迭代次数
    gradient_r：图像梯度计算核半径
    savefilepath：文件保存路径

    '''
    #读取图像
    img = io.imread(filepath)

    #图像二值化
    image = color.rgb2gray(img)

    #图像直方图均衡
    img_c = exposure.equalize_hist(image)

    #过滤噪声
    denoised = filters.rank.median(img_c, morphology.disk(int(median_r)))

    #阈值选取
    if islocal == True:
        thresh = filters.threshold_local(denoised, block_size=int(localsize),\
                                         offset=int(local_offset))
    else:
        thresh = filters.threshold_li(denoised)
    #阈值分割
    binary = denoised > thresh

    #形态学侵蚀
    for i in range(int(ite_erosion)):
        binary = morphology.binary_erosion(binary)

    #连通区域标记
    classes = ndi.label(binary)[0]

    #计算图像梯度
    gradient = filters.rank.gradient(denoised, morphology.disk(int(gradient_r)))
    gradient_inv = gradient.max() - gradient

    #寻找梯度最小值
    local_min = feature.peak_local_max(gradient_inv, indices=False,\
                                       min_distance=35, num_peaks_per_label=1, labels=classes)
    gradient_selected = np.ones(np.shape(image)) * gradient.max()
    gradient_selected[local_min == True] = gradient[local_min == True]

    #标记注水点
    markers = ndi.label(local_min)[0]

    #基于梯度的分水岭算法
    labels = morphology.watershed(gradient, markers, watershed_line=True, compactness=0)

    #保存图像
    if filepath[-3:] == 'png':
        img[labels == 0] = [255, 0, 0, 255]
        img[markers != 0] = [0, 255, 0, 255]
    else:
        img[labels == 0] = [255, 0, 0]
        img[markers != 0] = [0, 255, 0]

    io.imsave(savefilepath, img)
