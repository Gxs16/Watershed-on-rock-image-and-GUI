#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
此项目为堆石混凝土图像识别数据预处理软件
此代码主要完成GUI界面的搭建工作

作者：郭欣晟
最后编辑日期：2020年4月13日
'''
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as ndi
from skimage import morphology, color, data, filters, io, feature, exposure

class ImgSegmentation(QMainWindow):
    '''
    主窗口类
    '''
    def __init__(self):
        super().__init__()

        self.init_ui()


    def init_ui(self):
        '''
        这是主窗口的构造函数
        初始化模块：
        菜单栏
        状态栏
        图像显示区域
        参数输入区域
        按钮
        '''

        self.setGeometry(50, 50, 1450, 950)#设置窗口大小及位置
        self.setWindowTitle('图像分割')#设置窗口标题

        #设置菜单栏
        openAct = QAction('打开图片', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('打开图片')
        openAct.triggered.connect(self.openimage)
        filepath = ''

        exitAct = QAction('退出', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('退出应用程序')
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')
        fileMenu.addAction(openAct)
        fileMenu.addAction(exitAct)

        #设置状态栏
        self.statusBar().showMessage('请选择图片')

        #设置图像显示区域
        self.label = QLabel(self)
        self.label.setFixedSize(1000, 800)
        self.label.move(20, 50)

        #设置图像降噪核半径输入区域
        self.lbl_median = QLabel(self)
        self.lbl_median.setText('噪声过滤核半径：')
        self.lbl_median.move(1040, 50)
        self.lbl_median.adjustSize()

        pIntvalidator_median = QIntValidator(self)
        pIntvalidator_median.setRange(1, 30)
        self.qle_median = QLineEdit(self)
        self.qle_median.move(1040, 100)
        self.qle_median.setText('7')
        self.qle_median.setValidator(pIntvalidator_median)

        #设置图像阈值分割参数选择区域
        self.local_th = QCheckBox('局部阈值选取', self)
        self.local_th.move(1040, 150)
        self.local_th.toggle()
        self.local_th.adjustSize()

        self.lbl_thresh = QLabel(self)
        self.lbl_thresh.setText('局部阈值分割核半径：')
        self.lbl_thresh.move(1040, 250)
        self.lbl_thresh.adjustSize()
        pIntvalidator_thresh = QIntValidator(self)
        pIntvalidator_thresh.setRange(1, 2000)
        self.qle_thresh = QLineEdit(self)
        self.qle_thresh.move(1040, 300)
        self.qle_thresh.setText('501')
        self.qle_thresh.setValidator(pIntvalidator_thresh)

        self.lbl_setoff = QLabel(self)
        self.lbl_setoff.setText('偏移量：')
        self.lbl_setoff.move(1040, 350)
        self.lbl_setoff.adjustSize()
        pIntvalidator_setoff = QIntValidator(self)
        pIntvalidator_setoff.setRange(0, 255)
        self.qle_setoff = QLineEdit(self)
        self.qle_setoff.move(1040, 400)
        self.qle_setoff.setText('30')
        self.qle_setoff.setValidator(pIntvalidator_setoff)

        self.local_th.stateChanged.connect(self.change_thresh)
        self.local_th.setChecked(False)
        #设置形态学侵蚀迭代次数
        self.lbl_erosion = QLabel(self)
        self.lbl_erosion.setText('形态学侵蚀迭代次数：')
        self.lbl_erosion.move(1040, 450)
        self.lbl_erosion.adjustSize()
        pIntvalidator_erosion = QIntValidator(self)
        pIntvalidator_erosion.setRange(0, 25)
        self.qle_erosion = QLineEdit(self)
        self.qle_erosion.move(1040, 500)
        self.qle_erosion.setText('10')
        self.qle_erosion.setValidator(pIntvalidator_erosion)

        #设置梯度运算核半径
        self.lbl_gradient = QLabel(self)
        self.lbl_gradient.setText('梯度运算核半径：')
        self.lbl_gradient.move(1040, 550)
        self.lbl_gradient.adjustSize()
        pIntvalidator_gradient = QIntValidator(self)
        pIntvalidator_gradient.setRange(0, 10)
        self.qle_gradient = QLineEdit(self)
        self.qle_gradient.move(1040, 600)
        self.qle_gradient.setText('5')
        self.qle_gradient.setValidator(pIntvalidator_gradient)

        #设置开始运算按钮
        self.startbtn = QPushButton('开始分割', self)
        self.startbtn.setCheckable(False)
        self.startbtn.move(1040, 700)
        self.startbtn.toggle()
        self.startbtn.clicked.connect(self.watershed)
        self.show()

    def openimage(self):
        '''
        这是打开文件的函数
        调用文件对话框
        显示图片
        更新状态栏显示文字
        '''
        #打开图片
        self.statusBar().showMessage('打开图片')
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", \
                                                       "", "*.jpg;;*.png;;All Files(*)")
        jpg = QtGui.QPixmap(imgName).scaled(self.label.width(), \
                                            self.label.height(), Qt.KeepAspectRatio)
        self.filepath = imgName
        self.label.setPixmap(jpg)
        self.statusBar().showMessage('请调整右侧参数')

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

    def watershed(self):
        '''
        分水岭分割流程的实现
        '''
        #状态栏提示
        self.statusBar().showMessage('正在分割')

        #读取图像
        img = io.imread(self.filepath)

        #图像二值化
        image = color.rgb2gray(img)

        #图像直方图均衡
        img_c = exposure.equalize_hist(image)

        #过滤噪声
        denoised = filters.rank.median(img_c, morphology.disk(int(self.qle_median.text())))

        #阈值选取
        if self.local_th.isChecked() == True:
            thresh = filters.threshold_local(denoised, block_size=int(self.qle_thresh.text()), \
                                             offset=int(self.qle_setoff.text()))
        else:
            thresh = filters.threshold_li(denoised)
        #阈值分割
        binary = denoised > thresh

        #形态学侵蚀
        for i in range(int(self.qle_erosion.text())):
            binary = morphology.binary_erosion(binary)

        #连通区域标记
        classes = ndi.label(binary)[0]

        #计算图像梯度
        gradient = filters.rank.gradient(denoised, morphology.disk(int(self.qle_gradient.text())))
        gradient_inv = gradient.max() - gradient

        #寻找梯度最小值
        local_min = feature.peak_local_max(gradient_inv, indices=False, min_distance=35, \
                                           num_peaks_per_label=1, labels=classes)
        gradient_selected = np.ones(np.shape(image)) * gradient.max()
        gradient_selected[local_min == True] = gradient[local_min == True]

        #标记注水点
        markers = ndi.label(local_min)[0]

        #基于梯度的分水岭算法
        labels = morphology.watershed(gradient, markers, watershed_line=True, compactness=0)

        #保存图像
        if self.filepath[-3:] == 'png':
            img[labels == 0] = [255, 0, 0, 255]
            img[markers != 0] = [0, 255, 0, 255]
        else:
            img[labels == 0] = [255, 0, 0]
            img[markers != 0] = [0, 255, 0]
        imgName_s, imgType = QFileDialog.getSaveFileName(self, "保存图片", \
                                                          "", "*.jpg;;*.png;;All Files(*)")
        io.imsave(imgName_s, img)

        #图像显示
        jpg = QtGui.QPixmap(imgName_s).scaled(self.label.width(), \
                                              self.label.height(), Qt.KeepAspectRatio)
        self.label.setPixmap(jpg)
        #更改状态栏
        self.statusBar().showMessage('已完成！')

    def closeEvent(self, event):
        '''
        关闭应用程序时弹出消息框
        '''
        reply = QMessageBox.question(self, 'Message',
                                     "确定要退出吗？", QMessageBox.Yes|
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':

    APP = QApplication(sys.argv)
    ex = ImgSegmentation()
    sys.exit(APP.exec_())
    