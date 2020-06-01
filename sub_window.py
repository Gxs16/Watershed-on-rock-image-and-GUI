#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
窗口定义

最后编辑日期：2020-5-14
'''

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SegWindow(QWidget):
    '''
    分割窗口定义
    '''
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        '''
        分割窗口初始化函数
        初始化内容：
            参数输入区域的label和输入框
            “开始分割”按钮
        '''
        self.setGeometry(900, 50, 300, 800)#设置窗口大小及位置
        self.setWindowTitle('图像分割')#设置窗口标题

        #设置图像降噪核半径输入区域
        self.lbl_median = QLabel(self)
        self.lbl_median.setText('噪声过滤核半径：')
        self.lbl_median.move(50, 50)
        self.lbl_median.adjustSize()

        intvalidator_median = QIntValidator(self)
        intvalidator_median.setRange(1, 30)
        self.qle_median = QLineEdit(self)
        self.qle_median.move(50, 100)
        self.qle_median.setText('7')
        self.qle_median.setValidator(intvalidator_median)

        #设置图像阈值分割参数选择区域
        self.local_th = QCheckBox('局部阈值选取', self)
        self.local_th.move(50, 150)
        self.local_th.toggle()
        self.local_th.adjustSize()

        self.lbl_thresh = QLabel(self)
        self.lbl_thresh.setText('局部阈值分割核半径：')
        self.lbl_thresh.move(50, 250)
        self.lbl_thresh.adjustSize()
        intvalidator_thresh = QIntValidator(self)
        intvalidator_thresh.setRange(1, 2000)
        self.qle_thresh = QLineEdit(self)
        self.qle_thresh.move(50, 300)
        self.qle_thresh.setText('501')
        self.qle_thresh.setValidator(intvalidator_thresh)

        self.lbl_setoff = QLabel(self)
        self.lbl_setoff.setText('偏移量：')
        self.lbl_setoff.move(50, 350)
        self.lbl_setoff.adjustSize()
        intvalidator_setoff = QIntValidator(self)
        intvalidator_setoff.setRange(0, 255)
        self.qle_setoff = QLineEdit(self)
        self.qle_setoff.move(50, 400)
        self.qle_setoff.setText('30')
        self.qle_setoff.setValidator(intvalidator_setoff)

        self.local_th.stateChanged.connect(self.change_thresh)
        self.local_th.setChecked(False)
        #设置形态学侵蚀迭代次数
        self.lbl_erosion = QLabel(self)
        self.lbl_erosion.setText('形态学侵蚀迭代次数：')
        self.lbl_erosion.move(50, 450)
        self.lbl_erosion.adjustSize()
        intvalidator_erosion = QIntValidator(self)
        intvalidator_erosion.setRange(0, 25)
        self.qle_erosion = QLineEdit(self)
        self.qle_erosion.move(50, 500)
        self.qle_erosion.setText('10')
        self.qle_erosion.setValidator(intvalidator_erosion)

        #设置梯度运算核半径
        self.lbl_gradient = QLabel(self)
        self.lbl_gradient.setText('梯度运算核半径：')
        self.lbl_gradient.move(50, 550)
        self.lbl_gradient.adjustSize()
        intvalidator_gradient = QIntValidator(self)
        intvalidator_gradient.setRange(0, 10)
        self.qle_gradient = QLineEdit(self)
        self.qle_gradient.move(50, 600)
        self.qle_gradient.setText('5')
        self.qle_gradient.setValidator(intvalidator_gradient)

        #设置开始运算按钮
        self.startbtn = QPushButton('开始分割', self)
        self.startbtn.setCheckable(False)
        self.startbtn.move(50, 700)
        self.startbtn.toggle()
        #self

    def change_thresh(self, state):
        '''
        此函数通过判定local_th的勾选状态判断是否将对应输入框设为只读状态
        '''
        if state == Qt.Unchecked:
            self.qle_thresh.setReadOnly(True)
            self.qle_setoff.setReadOnly(True)
        else:
            self.qle_thresh.setReadOnly(False)
            self.qle_setoff.setReadOnly(False)

class CorrectWindow(QWidget):
    '''
    人工修正窗口类
    '''
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        '''
        人工修正窗口初始化函数
        初始化内容：
            “合并”按钮
            “选择分割面”按钮
            “再分割”按钮
            “删除”按钮
        '''
        self.setGeometry(900, 50, 300, 300)#设置窗口大小及位置
        self.setWindowTitle('结果修改')#设置窗口标题

        #设置合并按钮
        self.mergebtn = QPushButton('合并', self)
        self.mergebtn.setCheckable(False)
        self.mergebtn.move(50, 50)
        self.mergebtn.toggle()


        #设置再分割按钮
        self.splitbtn = QPushButton('选择分割面', self)
        self.splitbtn.setCheckable(False)
        self.splitbtn.move(50, 100)
        self.splitbtn.toggle()

        self.splitbtn2 = QPushButton('再分割', self)
        self.splitbtn2.setCheckable(False)
        self.splitbtn2.move(50, 150)
        self.splitbtn2.toggle()
        self.splitbtn2.setEnabled(False)

        #设置删除背景按钮
        self.deletebtn = QPushButton('删除', self)
        self.deletebtn.setCheckable(False)
        self.deletebtn.move(50, 200)
        self.deletebtn.toggle()
        

class BodyWindow(QWidget):
    '''
    块体对应窗口类
    '''
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        '''
        块体对应窗口初始化函数
        初始化内容：
            “块体”按钮
        '''
        self.setGeometry(900, 50, 300, 300)#设置窗口大小及位置
        self.setWindowTitle('块体对应')#设置窗口标题

        #设置块体按钮
        self.bodybtn = QPushButton('块体', self)
        self.bodybtn.setCheckable(False)
        self.bodybtn.move(50, 50)
        self.bodybtn.toggle()
