#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
图像显示区域

最后编辑日期：2020-5-14
'''

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np

class MyLabel(QLabel):
    '''
    定义图像显示label
    '''
    def __init__(self, parent=None):
        super(MyLabel, self).__init__((parent))
        self.show_contour = False  #是否显示堆石面轮廓的指示变量
        self.point_isshow = False  #是否显示鼠标点击位置的指示变量
        self.point_delete = False  #是否显示删除位置的指示变量
        self.show_body = False  #是否显示堆石体轮廓的指示变量
        self.is_draw_line = False  #是否记录鼠标轨迹的控制变量

        self.clk_pos = []  #保存鼠标点击的位置
        self.clk_pos_delete = []  #保存删除的位置
        self.polygon = []  #保存分割面轮廓顶点坐标
        self.polygon_body = []  #保存堆石体轮廓顶点坐标
        self.pos_xy = []  #保存鼠标轨迹

        self.setMouseTracking(False)

    def mousePressEvent(self, event):
        '''
        鼠标按下事件：
        将鼠标点击的坐标放入clk_pos列表中
        '''
        QLabel.mousePressEvent(self, event)
        self.point_isshow = True
        self.clk_pos.append([event.x(), event.y()])

    def mouseMoveEvent(self, event):
        '''
            按住鼠标移动事件：
            将当前点添加到pos_xy列表中
        '''
        if self.is_draw_line:
            #中间变量pos_tmp提取当前点
            pos_tmp = (event.pos().x(), event.pos().y())
            #pos_tmp添加到self.pos_xy中
            self.pos_xy.append(pos_tmp)

    def paintEvent(self, event):
        '''
        绘制事件：
        鼠标点击位置
        分割面轮廓
        堆石体轮廓
        删除位置轮廓
        鼠标轨迹
        '''
        super().paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        #绘制分割面轮廓
        if self.show_contour:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            drawline(self.polygon, painter)

        #绘制鼠标点击位置
        if self.point_isshow:
            pen = QPen(Qt.blue, 8)
            painter.setPen(pen)
            for i in self.clk_pos:
                painter.drawPoint(i[0], i[1])

        #绘制鼠标轨迹
        if self.pos_xy:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            point_start = self.pos_xy[0]
            for pos_tmp in self.pos_xy:
                point_end = pos_tmp
                painter.drawLine(point_start[0], point_start[1], point_end[0], point_end[1])
                point_start = point_end

        #绘制删除位置
        if self.point_delete:
            pen = QPen(Qt.green, 8)
            painter.setPen(pen)
            for i in self.clk_pos_delete:
                painter.drawPoint(i[0],i[1])

        #绘制堆石体轮廓
        if self.show_body:
            pen = QPen(Qt.yellow, 2, Qt.SolidLine)
            painter.setPen(pen)
            drawline(self.polygon_body, painter)

        painter.end()
        self.update()

def drawline(polygon, painter):
    '''
    绘制线段语句
    参数：
        polygon：列表，存储需要绘制的多边形顶点坐标
        painter：pyqt5中定义的QPainter()

    返回值：
        无
    '''
    for i in polygon:
        for j in range(i.shape[0]-1):
            painter.drawLine(i[j, 0], i[j, 1], i[j+1, 0], i[j+1, 1])
            