#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
信息文件输出

最后编辑日期：2020-5-14
'''

import numpy as np 
import count

def save_file(file_name_save, labels_surfaces, labels_body, circles):
    '''
    生成并保存“xxx_info.txt”文件

    参数：
        file_name_save：字符串，存储保存文件路径
        labels：二维np数组(n,m)，存储分割面的连通域情况
        labels_body：二维np数组(n,m)，存储堆石块体的连通域情况
        circles：二维列表，circles[i]存储外接圆的信息，第一个元素表示圆心横坐标，第二个元素表示圆心纵坐标，第三个元素表示最小外接圆的半径

    返回值：
        无
    '''
    #生成分割面与堆石体的对应关系
    relation = count.relation(labels_surfaces, labels_body)

    #生成需要打印的字符串
    text = file_name_save+'\n'+'#Relation(surfaces rock)\n'
    #按照“分割面标号 堆石体标号”的格式打印
    for i in range(relation.size):
        text += str(i)+' '+str(relation[i])+'\n'
    text += '#Circles(rock x y radius)\n'
    #按照“堆石体标号 圆心坐标 外接圆半径”的格式打印
    for i in range(len(circles)):
        if circles[i][2] >= (max(labels_surfaces.shape)/20):
            text += str(i+1)+' '+str(circles[i][0])+' '+str(circles[i][1])+' '+str(circles[i][2])+'\n'

    #打印字符串并保存相应文件
    file = open(file_name_save[:-4]+'_info.txt', 'w')
    file.write(text)
    file.close()
