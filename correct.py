#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
此代码主要负责合并、再分割、背景去除、块体对应的后台计算工作

最后编辑日期：2020-5-14
'''

import numpy as np 
from skimage import measure

def surfaces_init(labels):
    '''
    面列表初始化，将每一个连通域新建一个“图层”

    参数：
        labels：二维np数组(n,m)，存储分割面的连通域情况

    返回值：
        surfaces：二维列表surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
    '''
    surfaces = []

    #对每一个label进行分割面轮廓计算
    for i in range(1, labels.max()+1):
        surface = np.zeros(labels.shape)  #新建图层
        surface[labels == i] = 1  #图层中1表示该连通域覆盖的像素
        contour = measure.find_contours(surface, 0.5)  #计算轮廓
        contour.insert(0, surface)  #在列表头插入图层
        surfaces.append(contour)  #在surfaces列表尾部添加该图层的信息

    return surfaces

def coordinate_window_to_img(coordinate, img):
    '''
    将鼠标的点击坐标换算为图像像素的坐标，与函数 coordinate_img_to_window 互为逆运算

    参数：
        coordinate：二维np数组(n,2)，存储以label为参考系的坐标
        img：二维np数组(n,2)，存储原始图像

    返回值：
        position：二维np数组(n,2)，存储以图片为参考系的坐标
    '''
    position = np.zeros((coordinate.shape[0], coordinate.shape[1]))
    #对坐标进行变换，需要根据原始图片的长宽确定横向缩放还是纵向缩放
    if img.shape[1] >= img.shape[0]:
        #如果是横向缩放，则上下居中显示
        ratio = img.shape[1] / 800  #定义缩放比例
        height_white = img.shape[0]/img.shape[1]*800  #确定空白区域高度，上下对称

        #坐标变换
        position[:, 1] = np.around((coordinate[:, 0]) * ratio).astype(int)
        position[:, 0] = np.around((coordinate[:, 1]-(800-height_white)/2)*ratio).astype(int)
    else:
        #如果是纵向缩放，则图片左对齐显示，不需要确定空白区域高度
        ratio = img.shape[0] / 800  #定义缩放比例

        #坐标变换
        position[:, 0] = np.around((coordinate[:, 1]) * ratio).astype(int)
        position[:, 1] = np.around((coordinate[:, 0])*ratio).astype(int)

    return position

def coordinate_img_to_window(coordinate, img):
    '''
    将像素的坐标换算为label中的坐标，与函数 coordinate_window_to_img 互为逆运算

    参数：
        coordinate：二维np数组(n,2)，存储以图片为参考系的坐标
        img：二维np数组(n,2)，存储原始图像

    返回值：
        position：二维np数组(n,2)，存储以label为参考系的坐标
    '''
    position = np.zeros((coordinate.shape[0], coordinate.shape[1]))
    #对坐标进行变换，需要根据原始图片的长宽确定横向缩放还是纵向缩放
    if img.shape[1] >= img.shape[0]:
        #如果是横向缩放，则上下居中显示
        ratio = 800/img.shape[1]  #定义缩放比例
        height_white = img.shape[0]/img.shape[1]*800  #确定空白区域高度，上下对称

        #坐标变换
        position[:, 0] = coordinate[:, 1]*ratio
        position[:, 1] = coordinate[:, 0]*ratio+(800-height_white)/2
    else:
        #如果是纵向缩放，则图片左对齐显示，不需要确定空白区域高度
        ratio = 800/img.shape[0]  #定义缩放比例

        #坐标变换
        position[:, 1] = coordinate[:, 0]*ratio
        position[:, 0] = coordinate[:, 1]*ratio

    return position

def merge(position, labels, surfaces):
    '''
    合并分割区域，将使用鼠标选中的多个分割面合并成一个分割面

    参数：
        position：二维np数组(n,2)，以图片为参考系的坐标，存储鼠标点击的位置
        labels：二维np数组(n,m)，分割面的标注表示
        surfaces：二维列表surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标

    返回值：
        labels：二维np数组(n,m)，更新之后的分割面的标注表示
        surfaces：二维列表，surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
    '''
    value = []
    position = position.astype(int)
    #获得鼠标点击位置处分割面的标记值
    for i in position:
        if labels[i[0], i[1]] > 0:  #防止点进背景区域
            value.append(labels[i[0], i[1]])
    value = np.unique(np.array(value, dtype=int))  #防止两次点进同一个分割面造成的错误所以使用unique
    minimum = value.min()

    target_surface = np.zeros(labels.shape)
    #对value中的surfaces进行合并
    for i in value:
        target_surface += surfaces[i-1][0]  #将需要合并的分割面图层直接相加
        surfaces[i-1] = 'null'  #对被合并的面标记为'null'
    surfaces[minimum-1] = [target_surface]  #将合并后的分割面放入正确的位置中

    #移除被合并的分割面
    for i in range(value.size-1):
        surfaces.remove('null')

    #对合并之后的分割面进行轮廓计算
    contour = measure.find_contours(target_surface, 0.5)  #计算轮廓
    surfaces[minimum-1] += contour  #更新轮廓

    #对合并分割面标记值进行更新，根据surfaces对标记值进行重新赋值
    for i in range(minimum-1, len(surfaces)):
        labels[surfaces[i][0] == 1] = i+1

    return labels, surfaces

def split(position, line, labels, surfaces):
    '''
    分割欠分割区域，通过将鼠标轨迹覆盖的像素更改为0，从而实现对目标分割面的再分割

    参数：
        position：二维np数组(n,2)，以图片为参考系的坐标，存储鼠标点击的位置
        line：二维列表，记录了鼠标滑过的轨迹，以多个点表示
        labels：二维np数组(n,m)，分割面的标注表示
        surfaces：二维列表surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标

    返回值
        labels：二维np数组(n,m)，更新之后的分割面的标注表示
        surfaces：二维列表，surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
    '''
    line_img = []
    value = labels[position[0][0].astype(int), \
                    position[0][1].astype(int)].astype(int)-1  #获得需要分割的分割面的标记值
    target_surface = surfaces[value][0]  #提取目标分割面的信息
    line = np.array(line, dtype=int)

    #通过插值将line中的坐标连成连续的线段，然后进行再次分割
    for i in range(line.shape[0]-1):
        #在插值过程中，为了保证能够成功分割连通域，所以需要保证在横纵坐标上是整数层面的连续变化，因此需要判断每两个点之间横纵坐标变化的幅度
        if abs(line[i+1, 0]-line[i, 0]) > abs(line[i+1, 1]-line[i, 1]):
            #如果纵坐标的变化幅度更大，则将横坐标对纵坐标插值
            y = np.linspace(line[i,0],line[i+1,0],abs(line[i+1,0]-line[i,0])+1).astype(int)
            yp = line[i:i+2, 0]
            #因为np.interp()的限制，需要保证插值序列为严格递增，如果不是严格递增，需要将插值序列反序
            if line[i+1, 0] < line[i, 0]:
                yp = yp[::-1]
            x = np.around(np.interp(y, yp, line[i:i+2, 1])).astype(int)  #进行插值
            #如果原始序列不是严格递增的，需要将结果反序
            if line[i+1, 0] < line[i, 0]:
                x = x[::-1]
        else:
            #如果横坐标的变化幅度更大，则将纵坐标对横坐标插值
            x = np.linspace(line[i, 1], line[i+1, 1], abs(line[i+1, 1]-line[i, 1])+1).astype(int)
            xp = line[i:i+2, 1]
            #因为np.interp()的限制，需要保证插值序列为严格递增，如果不是严格递增，需要将插值序列反序
            if line[i+1, 1] < line[i, 1]:
                xp = xp[::-1]
            y = np.around(np.interp(x, xp, line[i:i+2, 0])).astype(int)  #进行插值
            #如果原始序列不是严格递增的，需要将结果反序
            if line[i+1, 1] < line[i, 1]:
                y = y[::-1]
        for j in range(x.size):
            #对插值之后的横纵坐标进行筛选，保证坐标在labels的索引范围之内
            if x[j] >= 0 and x[j] < labels.shape[1] and y[j] >= 0 and y[j] < labels.shape[0]:
                #将鼠标轨迹覆盖的像素更改为0
                if target_surface[y[j], x[j]] == 1:
                    line_img.append([y[j], x[j]])  #被更改的像素位置
                    target_surface[y[j], x[j]] = 0

    #对分割后的位置进行再次标记
    target_surface_labeled = measure.label(target_surface, connectivity=1)
    #将鼠标轨迹覆盖的像素更改回1
    for k in line_img:
        target_surface_labeled[k[0], k[1]] = 1

    #使用surface_init()对分割后的图层进行轮廓寻找
    surfaces_splited = surfaces_init(target_surface_labeled)

    #将第一个面放置在原来目标分割面的位置上
    surfaces[value] = surfaces_splited[0]

    #将第二个面放置在列表的最后
    if len(surfaces_splited) > 1:
        surfaces.append(surfaces_splited[1])
        labels_max = labels.max()+1
        labels[target_surface_labeled == 2] = labels_max

    return labels, surfaces

def delete(position, labels, surfaces):
    '''
    删除通过鼠标点击选择的分割面

    参数：
        position：二维np数组(n,2)，以图片为参考系的坐标，存储鼠标点击的位置
        labels：二维np数组(n,m)，分割面的标注表示
        surfaces：二维列表surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标

    返回值：
        labels：二维np数组(n,m)，更新之后的分割面的标注表示
        surfaces：二维列表，surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
    '''
    for i in position:
        value = labels[i[0].astype(int), i[1].astype(int)]-1  #提取鼠标点击位置处的标记值

        #删除标记值对应的目标面
        surfaces[value] = 'null'
        surfaces.remove('null')

        #更新labels中的标记值
        labels[labels == (value+1)] = 0
        labels[labels > (value+1)] = labels[labels > (value+1)]-1

    return labels, surfaces

def body(position, labels, surfaces):
    '''
    将通过鼠标点击选择的分割面合并为一个块体，和merge()相似

    参数：
        position：二维np数组(n,2)，以图片为参考系的坐标，存储鼠标点击的位置
        labels：二维np数组(n,m)，分割面的标注表示
        surfaces：二维列表surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标

    返回值：
        labels：二维np数组(n,m)，更新之后的分割面的标注表示
        surfaces：二维列表，surfaces[i]中代表存储标号为i+1的连通域的信息，surfaces[i][0]以二维0-1数组(n,m)存储连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
    '''
    value = []
    position = position.astype(int)
    #获得鼠标点击位置处分割面的标记值
    for i in position:
        if labels[i[0], i[1]] > 0:  #防止点进背景区域
            value.append(labels[i[0], i[1]])

    value = np.unique(np.array(value, dtype=int))  #防止两次点进同一个分割面造成的错误所以使用unique
    minimum = value.min()

    #对value中的surfaces进行合并
    target_surface = np.zeros(labels.shape)
    for i in value:
        target_surface += surfaces[i-1][0]  #将需要合并的分割面图层直接相加
        surfaces[i-1] = 'null'  #对被合并的面标记为'null'

    surfaces[minimum-1] = [target_surface]  #将合并后的分割面放入正确的位置中

    #移除被合并的分割面
    for i in range(value.size-1):
        surfaces.remove('null')

    #对合并之后的分割面进行轮廓计算
    contour = measure.find_contours(target_surface, 0.5)  #计算轮廓
    surfaces[minimum-1] += contour  #更新轮廓

    #对合并分割面标记值进行更新，根据surfaces对标记值进行重新赋值
    for i in range(minimum-1, len(surfaces)):
        labels[surfaces[i][0] == 1] = i+1

    return labels, surfaces
