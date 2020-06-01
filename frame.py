#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
此项目为堆石混凝土图像识别数据预处理软件
此代码主要完成GUI界面的搭建工作

最后编辑日期：2020-5-14
'''

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from skimage import io
import numpy as np
import correct
import count
from segmentation import watershed
from label_show import MyLabel
from sub_window import SegWindow, CorrectWindow, BodyWindow
import file

class ImgSegmentation(QMainWindow):
    '''
    主窗口类
    '''
    def __init__(self):
        '''
        构造函数
        '''
        super().__init__()
        self.filepath = ''  #存储处理文件路径
        self.filetype = ''  #存储文件类型
        self.img = np.zeros(1)  #存储图片的原始信息

        self.labels = None  #存储分割面的标记信息
        self.surfaces = None  #存储每个分割面的信息，包括连通域以及轮廓，可以理解为每一个分割面为一个图层
        self.polygon = []  #存储分割后分割面的轮廓信息

        self.labels_body = None  #存储块体的标注信息
        self.polygon_body = []  #存储块体的轮廓信息
        self.surfaces_body = None  #存储每一个块体的信息，包括连通域以及轮廓，可以理解为一个块体为一个图层


        self.coordinate_label = None  #坐标，参考系为label
        self.coordinate_img = None  #坐标，参考系为图片
        self.body_process = False  #标记是否进入块体对应阶段的指示变量
        self.relation = None  #存储堆石面与堆石之间对应关系

        self.init_ui()

    def init_ui(self):
        '''
        这是主窗口的构造函数
        
        初始化模块：
        菜单栏
        状态栏
        图像显示区域
        '''

        self.setGeometry(0, 50, 900, 900)  #设置窗口大小及位置
        self.setWindowTitle('图像处理')  #设置窗口标题

        self.seg_window = SegWindow()  #定义分割工具栏
        self.correct_window = CorrectWindow()  #定义人工修正工具栏
        self.body_window = BodyWindow()  #定义块体对应工具栏

        #设置菜单栏
        open_act = QAction('打开图片', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('打开图片')
        open_act.triggered.connect(self.openimage)

        exit_act = QAction('退出', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('退出应用程序')
        exit_act.triggered.connect(self.close)

        seg_act = QAction('分割图片', self)
        seg_act.setShortcut('Ctrl+A')
        seg_act.setStatusTip('分割图片')
        seg_act.triggered.connect(self.seg_window.show)

        edit_act = QAction('修改结果', self)
        edit_act.setShortcut('Ctrl+E')
        edit_act.setStatusTip('再分割、合并过分割区域、背景删除')
        edit_act.triggered.connect(self.correct_window.show)

        body_act = QAction('块体对应', self)
        body_act.setShortcut('Ctrl+B')
        body_act.setStatusTip('堆石面与堆石体的对应')
        body_act.triggered.connect(self.body_window.show)

        save_act = QAction('输出结果', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('保存结果文件')
        save_act.triggered.connect(self.save_file)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        file_menu.addAction(open_act)
        file_menu.addAction(exit_act)
        tool_menu = menubar.addMenu('工具')
        tool_menu.addAction(seg_act)
        tool_menu.addAction(edit_act)
        tool_menu.addAction(body_act)
        tool_menu.addAction(save_act)

        #设置状态栏
        self.statusBar().showMessage('请选择图片')

        #设置图像显示区域
        self.label = MyLabel(self)
        self.label.setFixedSize(800, 800)
        self.label.move(50, 50)

        #操作
        self.seg_window.startbtn.clicked.connect(self.watershed)
        self.correct_window.mergebtn.clicked.connect(self.correct_merge)
        self.correct_window.splitbtn2.clicked.connect(self.correct_split)
        self.correct_window.deletebtn.clicked.connect(self.correct_delete)
        self.correct_window.splitbtn.clicked.connect(self.select_surface)
        self.body_window.bodybtn.clicked.connect(self.surfaces_to_body)

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
        img_name_open, img_type = QFileDialog.getOpenFileName(self, "打开图片", \
                                                           "", "*.jpg;;*.png;;All Files(*)")

        #显示图片
        jpg = QtGui.QPixmap(img_name_open).scaled(self.label.width(),\
                                               self.label.height(), Qt.KeepAspectRatio)
        self.filepath = img_name_open
        self.filetype = img_type
        self.label.setPixmap(jpg)

        self.statusBar().showMessage('请调整右侧参数')

        #指示变量修改
        self.label.show_body = False  #关闭块体轮廓显示
        self.label.show_contour = False  #关闭堆石面轮廓显示
        self.body_process = False  #关闭块体对应过程

    def watershed(self):
        '''
        分水岭分割流程的实现
        '''
        self.statusBar().showMessage('正在分割')  #状态栏提示

        #执行分水岭算法
        self.labels, self.img = watershed(self.filepath, self.seg_window.qle_median.text(),\
                  self.seg_window.local_th.isChecked(), self.seg_window.qle_thresh.text(),\
                  self.seg_window.qle_setoff.text(), self.seg_window.qle_erosion.text(),\
                  self.seg_window.qle_gradient.text())

        self.paint_contours()  #画边界框

        self.statusBar().showMessage('分水岭算法已完成！')  #更改状态栏

    def paint_contours(self):
        '''
        绘制由分水岭算法得到的边界框
        '''
        #分割面初始化
        self.surfaces = correct.surfaces_init(self.labels)

        #提取分割面信息中的轮廓信息
        self.polygon = [] #清空轮廓信息
        for surface in self.surfaces:
            for contour in surface[1:]:
                self.polygon.append(correct.coordinate_img_to_window(contour, self.img))

        self.label.polygon = self.polygon  #将主窗口中的轮廓数据传输至label中进行绘制工作

        self.label.show_contour = True  #打开label中的堆石面轮廓显示

    def correct_merge(self):
        '''
        进行过分割区域的合并
        '''
        #坐标
        coordinate_label = np.array(self.label.clk_pos)  #获得鼠标点击的label坐标
        coordinate_img = correct.coordinate_window_to_img(coordinate_label, \
                                                            self.img)  #将label坐标转换为图片坐标

        #进行分割面的合并
        self.labels, self.surfaces = correct.merge(coordinate_img, self.labels, self.surfaces)

        #提取分割面信息中的轮廓信息
        self.polygon = []
        for surface in self.surfaces:
            for contour in surface[1:]:
                self.polygon.append(correct.coordinate_img_to_window(contour, self.img))
        self.label.polygon = self.polygon  #将主窗口中的轮廓数据传输至label中进行绘制工作

        self.label.clk_pos = []  #清空鼠标点击位置

        #指示变量修改
        self.label.show_contour = True  #打开label中的堆石面轮廓显示
        self.label.point_isshow = False  #关闭鼠标点击位置显示

    def select_surface(self):
        '''
        进行欠分割区域的选择
        '''
        #坐标
        self.coordinate_label = np.array(self.label.clk_pos)  #获得鼠标点击的label坐标
        self.coordinate_img = correct.coordinate_window_to_img(self.coordinate_label, \
                                                                self.img)  #将label坐标转换为图片坐标

        #指示变量修改
        self.label.is_draw_line = True  #打开鼠标轨迹显示
        self.label.point_isshow = False  #关闭鼠标点击位置显示
        self.label.clk_pos = []  #清空鼠标点击位置

        self.correct_window.splitbtn2.setEnabled(True)  #激活“再分割”按钮

    def correct_split(self):
        '''
        进行欠分割区域的分割
        '''
        #判断鼠标轨迹是否存在，如果不存在将不进行任何操作，确保在忘记绘制曲线时，点击“再分割”按钮不会导致程序崩溃
        if self.label.pos_xy:
            #坐标
            pos = np.array(self.label.pos_xy)  #获得鼠标轨迹的label坐标
            line = correct.coordinate_window_to_img(pos, self.img)  #将鼠标轨迹label坐标转换为图片坐标

            #区域分割
            self.labels, self.surfaces = correct.split(self.coordinate_img, line, \
                                                       self.labels, self.surfaces)

            self.polygon = []  #清空轮廓信息
            #提取轮廓信息
            for surface in self.surfaces:
                for contour in surface[1:]:
                    self.polygon.append(correct.coordinate_img_to_window(contour, self.img))

            self.label.polygon = self.polygon  #将主窗口中的轮廓数据传输至label中进行绘制工作
            self.label.clk_pos = []  #清空鼠标点击位置
            self.label.pos_xy = []  #清空鼠标轨迹信息

            #指示变量修改
            self.label.show_contour = True  #打开label中的堆石面轮廓显示
            self.label.point_isshow = False  #关闭鼠标点击显示
            self.label.is_draw_line = False  #关闭鼠标轨迹显示
            self.correct_window.splitbtn2.setEnabled(False)  #失活再分割坐标

    def correct_delete(self):
        '''
        背景区域的删除
        '''
        #坐标
        self.coordinate_label = np.array(self.label.clk_pos)  #获得鼠标点击的label坐标
        self.coordinate_img = correct.coordinate_window_to_img(self.coordinate_label, \
                                                               self.img)  #将label坐标转换为图片坐标

        #区域删除
        self.labels, self.surfaces = correct.delete(self.coordinate_img, \
                                                    self.labels, self.surfaces)

        #提取轮廓信息
        self.polygon = []
        for surface in self.surfaces:
            for contour in surface[1:]:
                self.polygon.append(correct.coordinate_img_to_window(contour, self.img))
        self.label.polygon = self.polygon  #将主窗口中的轮廓数据传输至label中进行绘制工作

        self.label.clk_pos_delete += self.label.clk_pos  #将此次鼠标点击位置添加至删除位置记录中
        self.label.clk_pos = []  #清空鼠标点击位置

        #指示变量更改
        self.label.show_contour = True  #打开label中的堆石面轮廓显示
        self.label.point_isshow = False  #关闭鼠标点击显示
        self.label.point_delete = True  #打开删除位置记录显示

    def surfaces_to_body(self):
        '''
        块体和堆石面的对应
        '''
        #如果是第一次进行对应操作，应将原有的堆石分割面信息传递给堆石块体信息
        if not self.body_process:
            self.labels_body = np.array(self.labels, dtype=int)
            self.surfaces_body = list(self.surfaces)
            self.body_process = True

        #坐标
        coordinate_label = np.array(self.label.clk_pos)  #获得鼠标点击的label坐标
        coordinate_img = correct.coordinate_window_to_img(coordinate_label, \
                                                            self.img)  #将label坐标转换为图片坐标

        # 进行块体对应操作
        self.labels_body, self.surfaces_body = correct.body(coordinate_img, \
                                                            self.labels_body, self.surfaces_body)

        #轮廓信息提取
        self.polygon_body = []
        for surface_body in self.surfaces_body:
            for contour_body in surface_body[1:]:
                self.polygon_body.append(correct.coordinate_img_to_window(contour_body, self.img))
        self.label.polygon_body = self.polygon_body  #将主窗口中的轮廓数据传输至label中进行绘制工作

        self.label.clk_pos = []  #清空鼠标点击位置

        #指示变量更改
        self.label.show_contour = True  #打开label中的堆石面轮廓显示
        self.label.show_body = True  #打开label中的堆石体轮廓显示
        self.label.point_isshow = False  #关闭鼠标点击显示

    def save_file(self):
        '''
        保存输出文件
        '''
        #外切圆的计算
        circles, img = count.circle(self.surfaces_body, self.img)

        #确定文件输出位置
        img_name_s, img_type = QFileDialog.getSaveFileName(self, "保存图片", "",\
                                                            self.filetype)

        #文件保存
        io.imsave(img_name_s, img)  #外切圆绘制图片保存
        np.savetxt(img_name_s[:-3]+'txt', self.labels, fmt='%i')  #堆石面标记信息保存
        file.save_file(img_name_s, self.labels, self.labels_body, circles)  #堆石体对应信息和外接圆信息保存

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
    