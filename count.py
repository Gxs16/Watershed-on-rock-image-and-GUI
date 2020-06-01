#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
此代码主要负责外接圆的计算、绘制，以及分割面与堆石块体对应的输出

最后编辑日期：2020-5-14
'''

import numpy as np
from cv2 import cv2

def circle(surfaces_body, img):
    '''
    外接圆的计算、绘制

    参数：
        surfaces_body：二维列表surfaces_body[i]中代表存储标号为i+1的堆石块体的信息，surfaces_body[i][0]以二维0-1数组(n,m)存储堆石块体的连通域，surfaces[i][1:]存储该连通域的多个轮廓顶点坐标
        img：二维np数组(n,2)，存储原始图像

    返回值：
        circles：二维列表，circles[i]存储外接圆的信息，第一个元素表示圆心横坐标，第二个元素表示圆心纵坐标，第三个元素表示最小外接圆的半径
        img：二维np数组(n,2)，存储绘制有所有堆石最小外接圆的图像图像
    '''
    circles = []
    for i in range(len(surfaces_body)):
        radius_max = 0
        for j in surfaces_body[i][1:]:
            #计算外接圆
            (rx, ry), radius = cv2.minEnclosingCircle(np.float32(j))

            #保留半径最大的外接圆
            if radius_max == 0:
                circles.append([rx, ry, radius])
                radius_max = radius
            if radius_max <= radius and radius_max != 0:
                circles[i] = [rx, ry, radius]
                radius_max = radius

        center = (int(circles[i][1]), int(circles[i][0]))
        radius = int(circles[i][2])

        #筛选细碎分割面的外接圆
        if radius >= (max(img.shape)/20):
            img = cv2.circle(img, center, radius, (255, 0, 0), 2)  #绘制外接圆

    return circles, img

def relation(labels, labels_body):
    '''
    通过对比分割面的标注值与堆石块体的标注值，获得分割面与堆石块体的对应关系

    参数：
        labels：二维np数组(n,m)，存储分割面的连通域情况
        labels_body：二维np数组(n,m)，存储堆石块体的连通域情况

    返回值：
        relationship：一位np数组(n,1)，relationship[i]存储标记值为i的分割面对应的块体标记
    '''
    relationship = np.arange(labels.max()+1, dtype=int)
    #获得对应标记值
    for i in range(labels.max()+1):
        relationship[i] = np.unique(labels_body[labels == i])[0]

    return relationship
