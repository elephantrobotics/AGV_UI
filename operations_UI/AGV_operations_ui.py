# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AGV_operations.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_myAGV(object):
    def setupUi(self, myAGV):
        if not myAGV.objectName():
            myAGV.setObjectName(u"myAGV")
        myAGV.resize(1072, 828)
        self.centralwidget = QWidget(myAGV)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_15 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(2, 0, 2, 2)
        self.menu_widget = QWidget(self.centralwidget)
        self.menu_widget.setObjectName(u"menu_widget")
        self.menu_widget.setMaximumSize(QSize(16777215, 50))
        self.menu_widget.setStyleSheet(u"background-color: rgb(52, 73, 94);")
        self.gridLayout = QGridLayout(self.menu_widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(10, 0, 0, 0)
        self.title = QLabel(self.menu_widget)
        self.title.setObjectName(u"title")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(18)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setStyleSheet(u"background-color: rgb(255, 255, 255\uff0c200);\n"
"color: rgb(255, 255, 255);")

        self.gridLayout.addWidget(self.title, 0, 1, 1, 1)

        self.logo_lab = QLabel(self.menu_widget)
        self.logo_lab.setObjectName(u"logo_lab")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo_lab.sizePolicy().hasHeightForWidth())
        self.logo_lab.setSizePolicy(sizePolicy)
        self.logo_lab.setMinimumSize(QSize(25, 25))
        self.logo_lab.setMaximumSize(QSize(30, 30))
        self.logo_lab.setStyleSheet(u"")
        self.logo_lab.setPixmap(QPixmap(u"operations_UI/img_UI/logo.ico"))
        self.logo_lab.setScaledContents(True)
        self.logo_lab.setMargin(0)

        self.gridLayout.addWidget(self.logo_lab, 0, 0, 1, 1)

        self.min_btn = QPushButton(self.menu_widget)
        self.min_btn.setObjectName(u"min_btn")
        self.min_btn.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.min_btn.sizePolicy().hasHeightForWidth())
        self.min_btn.setSizePolicy(sizePolicy1)
        self.min_btn.setMinimumSize(QSize(30, 30))
        self.min_btn.setMaximumSize(QSize(30, 30))
        self.min_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.min_btn.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u"operations_UI/img_UI/min.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.min_btn.setIcon(icon)
        self.min_btn.setIconSize(QSize(30, 30))

        self.gridLayout.addWidget(self.min_btn, 0, 2, 1, 1)

        self.max_btn = QPushButton(self.menu_widget)
        self.max_btn.setObjectName(u"max_btn")
        self.max_btn.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.max_btn.sizePolicy().hasHeightForWidth())
        self.max_btn.setSizePolicy(sizePolicy1)
        self.max_btn.setMinimumSize(QSize(30, 30))
        self.max_btn.setMaximumSize(QSize(30, 30))
        self.max_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.max_btn.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u"operations_UI/img_UI/max.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.max_btn.setIcon(icon1)
        self.max_btn.setIconSize(QSize(30, 30))

        self.gridLayout.addWidget(self.max_btn, 0, 3, 1, 1)

        self.close_btn = QPushButton(self.menu_widget)
        self.close_btn.setObjectName(u"close_btn")
        self.close_btn.setMinimumSize(QSize(30, 30))
        self.close_btn.setMaximumSize(QSize(30, 30))
        self.close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_btn.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u"operations_UI/img_UI/close.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.close_btn.setIcon(icon2)
        self.close_btn.setIconSize(QSize(30, 30))

        self.gridLayout.addWidget(self.close_btn, 0, 4, 1, 1)


        self.verticalLayout_15.addWidget(self.menu_widget)

        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"background-color: rgb(243, 243, 243);\n"
"border:None;")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1047, 792))
        self.horizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 8, 2, -1)
        self.widget_left = QWidget(self.scrollAreaWidgetContents)
        self.widget_left.setObjectName(u"widget_left")
        self.widget_left.setStyleSheet(u"background-color: rgb(218, 218, 218);")
        self.verticalLayout_3 = QVBoxLayout(self.widget_left)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(11, 11, -1, -1)
        self.widget = QWidget(self.widget_left)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_12 = QHBoxLayout(self.widget)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_language = QLabel(self.widget)
        self.label_language.setObjectName(u"label_language")
        self.label_language.setStyleSheet(u"background-color: rgb(255, 255, 255\uff0c200);\n"
"font: 75 14pt \"Arial\";")

        self.horizontalLayout_12.addWidget(self.label_language)

        self.comboBox_language_selection = QComboBox(self.widget)
        self.comboBox_language_selection.addItem("")
        self.comboBox_language_selection.addItem("")
        self.comboBox_language_selection.setObjectName(u"comboBox_language_selection")
        self.comboBox_language_selection.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_12.addWidget(self.comboBox_language_selection)


        self.verticalLayout_3.addWidget(self.widget)

        self.widget_5 = QWidget(self.widget_left)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_radar = QLabel(self.widget_5)
        self.label_radar.setObjectName(u"label_radar")
        self.label_radar.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_4.addWidget(self.label_radar)

        self.radar_button = QPushButton(self.widget_5)
        self.radar_button.setObjectName(u"radar_button")
        self.radar_button.setMinimumSize(QSize(0, 30))
        self.radar_button.setStyleSheet(u"background-color: rgb(39, 174, 96);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 7px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_4.addWidget(self.radar_button)


        self.verticalLayout_3.addWidget(self.widget_5)

        self.widget_6 = QWidget(self.widget_left)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.basic_control = QLabel(self.widget_6)
        self.basic_control.setObjectName(u"basic_control")
        self.basic_control.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_3.addWidget(self.basic_control)

        self.widget_7 = QWidget(self.widget_6)
        self.widget_7.setObjectName(u"widget_7")

        self.horizontalLayout_3.addWidget(self.widget_7)


        self.verticalLayout_3.addWidget(self.widget_6)

        self.widget_8 = QWidget(self.widget_left)
        self.widget_8.setObjectName(u"widget_8")
        self.widget_8.setStyleSheet(u"background-color: rgb(236, 240, 241);")
        self.horizontalLayout_13 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.basic_control_button = QPushButton(self.widget_8)
        self.basic_control_button.setObjectName(u"basic_control_button")
        self.basic_control_button.setMinimumSize(QSize(0, 30))
        self.basic_control_button.setStyleSheet(u"background-color: rgb(39, 174, 96);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_13.addWidget(self.basic_control_button)

        self.basic_control_selection = QComboBox(self.widget_8)
        self.basic_control_selection.addItem("")
        self.basic_control_selection.addItem("")
        self.basic_control_selection.addItem("")
        self.basic_control_selection.setObjectName(u"basic_control_selection")
        self.basic_control_selection.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_13.addWidget(self.basic_control_selection)


        self.verticalLayout_3.addWidget(self.widget_8)

        self.widget_9 = QWidget(self.widget_left)
        self.widget_9.setObjectName(u"widget_9")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_9)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_map_nav = QLabel(self.widget_9)
        self.label_map_nav.setObjectName(u"label_map_nav")
        self.label_map_nav.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_5.addWidget(self.label_map_nav)

        self.save_map_button = QPushButton(self.widget_9)
        self.save_map_button.setObjectName(u"save_map_button")
        self.save_map_button.setMinimumSize(QSize(0, 30))
        self.save_map_button.setStyleSheet(u"background-color: rgb(39, 174, 96);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 7px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_5.addWidget(self.save_map_button)


        self.verticalLayout_3.addWidget(self.widget_9)

        self.widget_13 = QWidget(self.widget_left)
        self.widget_13.setObjectName(u"widget_13")
        self.widget_13.setStyleSheet(u"background-color: rgb(236, 240, 241);")
        self.verticalLayout_2 = QVBoxLayout(self.widget_13)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget_10 = QWidget(self.widget_13)
        self.widget_10.setObjectName(u"widget_10")
        self.widget_10.setStyleSheet(u"")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.open_build_map = QPushButton(self.widget_10)
        self.open_build_map.setObjectName(u"open_build_map")
        self.open_build_map.setMinimumSize(QSize(0, 30))
        self.open_build_map.setStyleSheet(u"background-color:rgb(41, 128, 185);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_6.addWidget(self.open_build_map)

        self.build_map_selection = QComboBox(self.widget_10)
        self.build_map_selection.setObjectName(u"build_map_selection")
        self.build_map_selection.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_6.addWidget(self.build_map_selection)


        self.verticalLayout_2.addWidget(self.widget_10)

        self.widget_12 = QWidget(self.widget_13)
        self.widget_12.setObjectName(u"widget_12")
        self.widget_12.setStyleSheet(u"")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.navigation_3d_button = QPushButton(self.widget_12)
        self.navigation_3d_button.setObjectName(u"navigation_3d_button")
        self.navigation_3d_button.setMinimumSize(QSize(0, 30))
        self.navigation_3d_button.setStyleSheet(u"background-color:rgb(41, 128, 185);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_9.addWidget(self.navigation_3d_button)

        self.navigation_button = QPushButton(self.widget_12)
        self.navigation_button.setObjectName(u"navigation_button")
        self.navigation_button.setMinimumSize(QSize(0, 30))
        self.navigation_button.setStyleSheet(u"background-color:rgb(41, 128, 185);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_9.addWidget(self.navigation_button)


        self.verticalLayout_2.addWidget(self.widget_12)


        self.verticalLayout_3.addWidget(self.widget_13)

        self.widget_14 = QWidget(self.widget_left)
        self.widget_14.setObjectName(u"widget_14")
        self.horizontalLayout_17 = QHBoxLayout(self.widget_14)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_10 = QLabel(self.widget_14)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_17.addWidget(self.label_10)

        self.widget_15 = QWidget(self.widget_14)
        self.widget_15.setObjectName(u"widget_15")

        self.horizontalLayout_17.addWidget(self.widget_15)


        self.verticalLayout_3.addWidget(self.widget_14)

        self.horizontalLayout_palette = QHBoxLayout()
        self.horizontalLayout_palette.setObjectName(u"horizontalLayout_palette")
        self.color_palette = QWidget(self.widget_left)
        self.color_palette.setObjectName(u"color_palette")

        self.horizontalLayout_palette.addWidget(self.color_palette)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget_hex = QWidget(self.widget_left)
        self.widget_hex.setObjectName(u"widget_hex")
        self.horizontalLayout_29 = QHBoxLayout(self.widget_hex)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.label_11 = QLabel(self.widget_hex)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_29.addWidget(self.label_11)

        self.lineEdit_HEX = QLabel(self.widget_hex)
        self.lineEdit_HEX.setObjectName(u"lineEdit_HEX")
        self.lineEdit_HEX.setStyleSheet(u"background:white;")

        self.horizontalLayout_29.addWidget(self.lineEdit_HEX)


        self.verticalLayout_4.addWidget(self.widget_hex)

        self.widget_rgb = QWidget(self.widget_left)
        self.widget_rgb.setObjectName(u"widget_rgb")
        self.horizontalLayout_30 = QHBoxLayout(self.widget_rgb)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.label_12 = QLabel(self.widget_rgb)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_30.addWidget(self.label_12)

        self.lineEdit_RGB = QLabel(self.widget_rgb)
        self.lineEdit_RGB.setObjectName(u"lineEdit_RGB")
        self.lineEdit_RGB.setStyleSheet(u"background:white;")

        self.horizontalLayout_30.addWidget(self.lineEdit_RGB)


        self.verticalLayout_4.addWidget(self.widget_rgb)


        self.horizontalLayout_palette.addLayout(self.verticalLayout_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_palette)

        self.widget_19 = QWidget(self.widget_left)
        self.widget_19.setObjectName(u"widget_19")
        self.horizontalLayout_26 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_luminance = QLabel(self.widget_19)
        self.label_luminance.setObjectName(u"label_luminance")
        self.label_luminance.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_26.addWidget(self.label_luminance)

        self.horizontal_Slider = QSlider(self.widget_19)
        self.horizontal_Slider.setObjectName(u"horizontal_Slider")
        self.horizontal_Slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_26.addWidget(self.horizontal_Slider)

        self.label_value = QLabel(self.widget_19)
        self.label_value.setObjectName(u"label_value")

        self.horizontalLayout_26.addWidget(self.label_value)


        self.verticalLayout_3.addWidget(self.widget_19)

        self.widget_22 = QWidget(self.widget_left)
        self.widget_22.setObjectName(u"widget_22")
        self.horizontalLayout_27 = QHBoxLayout(self.widget_22)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.label_15 = QLabel(self.widget_22)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_27.addWidget(self.label_15)

        self.widget_23 = QWidget(self.widget_22)
        self.widget_23.setObjectName(u"widget_23")
        self.verticalLayout_8 = QVBoxLayout(self.widget_23)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.Restore_btn = QPushButton(self.widget_23)
        self.Restore_btn.setObjectName(u"Restore_btn")
        self.Restore_btn.setStyleSheet(u"background-color: rgb(39, 174, 96);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 7px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.verticalLayout_8.addWidget(self.Restore_btn)


        self.horizontalLayout_27.addWidget(self.widget_23)


        self.verticalLayout_3.addWidget(self.widget_22)

        self.widget_24 = QWidget(self.widget_left)
        self.widget_24.setObjectName(u"widget_24")
        self.widget_24.setStyleSheet(u"background-color: rgb(236, 240, 241);")
        self.horizontalLayout_10 = QHBoxLayout(self.widget_24)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.start_detection_button = QPushButton(self.widget_24)
        self.start_detection_button.setObjectName(u"start_detection_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(30)
        sizePolicy2.setHeightForWidth(self.start_detection_button.sizePolicy().hasHeightForWidth())
        self.start_detection_button.setSizePolicy(sizePolicy2)
        self.start_detection_button.setMinimumSize(QSize(0, 30))
        self.start_detection_button.setStyleSheet(u"background-color:rgb(41, 128, 185);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.horizontalLayout_10.addWidget(self.start_detection_button)

        self.comboBox_testing = QComboBox(self.widget_24)
        self.comboBox_testing.addItem("")
        self.comboBox_testing.addItem("")
        self.comboBox_testing.addItem("")
        self.comboBox_testing.addItem("")
        self.comboBox_testing.addItem("")
        self.comboBox_testing.setObjectName(u"comboBox_testing")

        self.horizontalLayout_10.addWidget(self.comboBox_testing)


        self.verticalLayout_3.addWidget(self.widget_24)


        self.horizontalLayout.addWidget(self.widget_left)

        self.widget_right = QWidget(self.scrollAreaWidgetContents)
        self.widget_right.setObjectName(u"widget_right")
        self.widget_right.setStyleSheet(u"")
        self.verticalLayout_6 = QVBoxLayout(self.widget_right)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 10, 0, 2)
        self.widget_3 = QWidget(self.widget_right)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 0, 5, 3)
        self.textBrowser = QTextBrowser(self.widget_3)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"border:2px solid #1D5D9B;")

        self.horizontalLayout_2.addWidget(self.textBrowser)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.log_clear = QPushButton(self.widget_3)
        self.log_clear.setObjectName(u"log_clear")
        self.log_clear.setMinimumSize(QSize(0, 30))
        self.log_clear.setStyleSheet(u"background-color: rgb(39, 174, 96);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 7px;\n"
"border: 2px groove gray;\n"
"border-style: outset;\n"
"font: 75 9pt \"Arial\";")

        self.verticalLayout.addWidget(self.log_clear)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_2.setStretch(0, 8)
        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout_6.addWidget(self.widget_3)

        self.widget_4 = QWidget(self.widget_right)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setStyleSheet(u"background-color:#EEEEEE;")
        self.verticalLayout_14 = QVBoxLayout(self.widget_4)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(5, 0, 5, 0)
        self.widget_11 = QWidget(self.widget_4)
        self.widget_11.setObjectName(u"widget_11")
        self.horizontalLayout_20 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, -1, 0, 8)
        self.IP_address = QLabel(self.widget_11)
        self.IP_address.setObjectName(u"IP_address")
        self.IP_address.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_20.addWidget(self.IP_address)

        self.lineEdit = QLineEdit(self.widget_11)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 20))
        self.lineEdit.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_20.addWidget(self.lineEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer)


        self.verticalLayout_14.addWidget(self.widget_11)

        self.widget_18 = QWidget(self.widget_4)
        self.widget_18.setObjectName(u"widget_18")
        self.widget_18.setStyleSheet(u"")
        self.horizontalLayout_8 = QHBoxLayout(self.widget_18)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.status_battery_main = QLabel(self.widget_18)
        self.status_battery_main.setObjectName(u"status_battery_main")
        self.status_battery_main.setMinimumSize(QSize(18, 18))
        self.status_battery_main.setMaximumSize(QSize(18, 18))
        self.status_battery_main.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_21.addWidget(self.status_battery_main)

        self.main_battery = QLabel(self.widget_18)
        self.main_battery.setObjectName(u"main_battery")
        self.main_battery.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_21.addWidget(self.main_battery)


        self.verticalLayout_5.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.electricity_main = QLabel(self.widget_18)
        self.electricity_main.setObjectName(u"electricity_main")
        self.electricity_main.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_22.addWidget(self.electricity_main)

        self.lineEdit_power = QLabel(self.widget_18)
        self.lineEdit_power.setObjectName(u"lineEdit_power")
        self.lineEdit_power.setStyleSheet(u"")

        self.horizontalLayout_22.addWidget(self.lineEdit_power)


        self.verticalLayout_5.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.voltage = QLabel(self.widget_18)
        self.voltage.setObjectName(u"voltage")
        self.voltage.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_23.addWidget(self.voltage)

        self.lineEdit_voltage = QLabel(self.widget_18)
        self.lineEdit_voltage.setObjectName(u"lineEdit_voltage")
        self.lineEdit_voltage.setStyleSheet(u"")

        self.horizontalLayout_23.addWidget(self.lineEdit_voltage)


        self.verticalLayout_5.addLayout(self.horizontalLayout_23)


        self.horizontalLayout_8.addLayout(self.verticalLayout_5)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.status_battery_backup_2 = QLabel(self.widget_18)
        self.status_battery_backup_2.setObjectName(u"status_battery_backup_2")
        self.status_battery_backup_2.setMinimumSize(QSize(18, 18))
        self.status_battery_backup_2.setMaximumSize(QSize(18, 18))
        self.status_battery_backup_2.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_31.addWidget(self.status_battery_backup_2)

        self.backup_battery = QLabel(self.widget_18)
        self.backup_battery.setObjectName(u"backup_battery")
        self.backup_battery.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_31.addWidget(self.backup_battery)


        self.verticalLayout_13.addLayout(self.horizontalLayout_31)

        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.power_backup = QLabel(self.widget_18)
        self.power_backup.setObjectName(u"power_backup")
        self.power_backup.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_32.addWidget(self.power_backup)

        self.lineEdit_power_backup = QLabel(self.widget_18)
        self.lineEdit_power_backup.setObjectName(u"lineEdit_power_backup")
        self.lineEdit_power_backup.setStyleSheet(u"")

        self.horizontalLayout_32.addWidget(self.lineEdit_power_backup)


        self.verticalLayout_13.addLayout(self.horizontalLayout_32)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.voltage_backup = QLabel(self.widget_18)
        self.voltage_backup.setObjectName(u"voltage_backup")
        self.voltage_backup.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_33.addWidget(self.voltage_backup)

        self.lineEdit_voltage_backup = QLabel(self.widget_18)
        self.lineEdit_voltage_backup.setObjectName(u"lineEdit_voltage_backup")
        self.lineEdit_voltage_backup.setStyleSheet(u"")

        self.horizontalLayout_33.addWidget(self.lineEdit_voltage_backup)


        self.verticalLayout_13.addLayout(self.horizontalLayout_33)


        self.horizontalLayout_8.addLayout(self.verticalLayout_13)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.status_motor_1 = QLabel(self.widget_18)
        self.status_motor_1.setObjectName(u"status_motor_1")
        self.status_motor_1.setMinimumSize(QSize(18, 18))
        self.status_motor_1.setMaximumSize(QSize(18, 18))
        self.status_motor_1.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_25.addWidget(self.status_motor_1)

        self.motor_1 = QLabel(self.widget_18)
        self.motor_1.setObjectName(u"motor_1")
        self.motor_1.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_25.addWidget(self.motor_1)


        self.verticalLayout_7.addLayout(self.horizontalLayout_25)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.electricity_name1 = QLabel(self.widget_18)
        self.electricity_name1.setObjectName(u"electricity_name1")
        self.electricity_name1.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_7.addWidget(self.electricity_name1)

        self.electricity_motor1 = QLabel(self.widget_18)
        self.electricity_motor1.setObjectName(u"electricity_motor1")

        self.horizontalLayout_7.addWidget(self.electricity_motor1)


        self.verticalLayout_7.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.electricity_name_2 = QLabel(self.widget_18)
        self.electricity_name_2.setObjectName(u"electricity_name_2")
        self.electricity_name_2.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_11.addWidget(self.electricity_name_2)

        self.electricity_motor2 = QLabel(self.widget_18)
        self.electricity_motor2.setObjectName(u"electricity_motor2")

        self.horizontalLayout_11.addWidget(self.electricity_motor2)


        self.verticalLayout_7.addLayout(self.horizontalLayout_11)


        self.horizontalLayout_8.addLayout(self.verticalLayout_7)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.status_radar = QLabel(self.widget_18)
        self.status_radar.setObjectName(u"status_radar")
        self.status_radar.setMinimumSize(QSize(18, 18))
        self.status_radar.setMaximumSize(QSize(18, 18))
        self.status_radar.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_24.addWidget(self.status_radar)

        self.Radar = QLabel(self.widget_18)
        self.Radar.setObjectName(u"Radar")
        self.Radar.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_24.addWidget(self.Radar)


        self.verticalLayout_12.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.electricity_name_3 = QLabel(self.widget_18)
        self.electricity_name_3.setObjectName(u"electricity_name_3")
        self.electricity_name_3.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_16.addWidget(self.electricity_name_3)

        self.electricity_motor3 = QLabel(self.widget_18)
        self.electricity_motor3.setObjectName(u"electricity_motor3")

        self.horizontalLayout_16.addWidget(self.electricity_motor3)


        self.verticalLayout_12.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.electricity_name_4 = QLabel(self.widget_18)
        self.electricity_name_4.setObjectName(u"electricity_name_4")
        self.electricity_name_4.setStyleSheet(u"font: 10pt \"Arial\";")

        self.horizontalLayout_18.addWidget(self.electricity_name_4)

        self.electricity_motor4 = QLabel(self.widget_18)
        self.electricity_motor4.setObjectName(u"electricity_motor4")

        self.horizontalLayout_18.addWidget(self.electricity_motor4)


        self.verticalLayout_12.addLayout(self.horizontalLayout_18)


        self.horizontalLayout_8.addLayout(self.verticalLayout_12)


        self.verticalLayout_14.addWidget(self.widget_18)

        self.verticalLayout_14.setStretch(0, 1)
        self.verticalLayout_14.setStretch(1, 3)

        self.verticalLayout_6.addWidget(self.widget_4)

        self.verticalLayout_6.setStretch(0, 2)
        self.verticalLayout_6.setStretch(1, 1)

        self.horizontalLayout.addWidget(self.widget_right)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_15.addWidget(self.scrollArea)

        myAGV.setCentralWidget(self.centralwidget)

        self.retranslateUi(myAGV)

        QMetaObject.connectSlotsByName(myAGV)
    # setupUi

    def retranslateUi(self, myAGV):
        myAGV.setWindowTitle(QCoreApplication.translate("myAGV", u"MainWindow", None))
        self.title.setText(QCoreApplication.translate("myAGV", u"myAGV", None))
        self.logo_lab.setText("")
        self.min_btn.setText("")
        self.max_btn.setText("")
        self.close_btn.setText("")
        self.label_language.setText(QCoreApplication.translate("myAGV", u"language", None))
        self.comboBox_language_selection.setItemText(0, QCoreApplication.translate("myAGV", u"English", None))
        self.comboBox_language_selection.setItemText(1, QCoreApplication.translate("myAGV", u"Chinese", None))

        self.label_radar.setText(QCoreApplication.translate("myAGV", u"Laser Radar", None))
        self.radar_button.setText(QCoreApplication.translate("myAGV", u"ON", None))
        self.basic_control.setText(QCoreApplication.translate("myAGV", u"Basic Control", None))
        self.basic_control_button.setText(QCoreApplication.translate("myAGV", u"ON", None))
        self.basic_control_selection.setItemText(0, QCoreApplication.translate("myAGV", u"Keyboard Control", None))
        self.basic_control_selection.setItemText(1, QCoreApplication.translate("myAGV", u"Joystick-Alphabet", None))
        self.basic_control_selection.setItemText(2, QCoreApplication.translate("myAGV", u"Joystick-Number", None))

        self.label_map_nav.setText(QCoreApplication.translate("myAGV", u"Map Navigation", None))
        self.save_map_button.setText(QCoreApplication.translate("myAGV", u"Save Map", None))
        self.open_build_map.setText(QCoreApplication.translate("myAGV", u"Open Build Map", None))
        self.navigation_3d_button.setText(QCoreApplication.translate("myAGV", u"3D Navigation", None))
        self.navigation_button.setText(QCoreApplication.translate("myAGV", u"Navigation", None))
        self.label_10.setText(QCoreApplication.translate("myAGV", u"LED Control", None))
        self.label_11.setText(QCoreApplication.translate("myAGV", u"HEX", None))
        self.lineEdit_HEX.setText("")
        self.label_12.setText(QCoreApplication.translate("myAGV", u"RGB", None))
        self.lineEdit_RGB.setText("")
        self.label_luminance.setText(QCoreApplication.translate("myAGV", u"Luminance", None))
        self.label_value.setText(QCoreApplication.translate("myAGV", u"value", None))
        self.label_15.setText(QCoreApplication.translate("myAGV", u"Test", None))
        self.Restore_btn.setText(QCoreApplication.translate("myAGV", u"Restore", None))
        self.start_detection_button.setText(QCoreApplication.translate("myAGV", u"Start Detection", None))
        self.comboBox_testing.setItemText(0, QCoreApplication.translate("myAGV", u"Motor", None))
        self.comboBox_testing.setItemText(1, QCoreApplication.translate("myAGV", u"LED", None))
        self.comboBox_testing.setItemText(2, QCoreApplication.translate("myAGV", u"2D Camera", None))
        self.comboBox_testing.setItemText(3, QCoreApplication.translate("myAGV", u"3D Camera", None))
        self.comboBox_testing.setItemText(4, QCoreApplication.translate("myAGV", u"Pump", None))

        self.log_clear.setText(QCoreApplication.translate("myAGV", u"clear", None))
        self.IP_address.setText(QCoreApplication.translate("myAGV", u"IP Address", None))
        self.status_battery_main.setText("")
        self.main_battery.setText(QCoreApplication.translate("myAGV", u"Main Battery", None))
        self.electricity_main.setText(QCoreApplication.translate("myAGV", u"Power", None))
        self.lineEdit_power.setText("")
        self.voltage.setText(QCoreApplication.translate("myAGV", u"Voltage", None))
        self.lineEdit_voltage.setText("")
        self.status_battery_backup_2.setText("")
        self.backup_battery.setText(QCoreApplication.translate("myAGV", u"Backup Battery", None))
        self.power_backup.setText(QCoreApplication.translate("myAGV", u"Power", None))
        self.lineEdit_power_backup.setText("")
        self.voltage_backup.setText(QCoreApplication.translate("myAGV", u"Voltage", None))
        self.lineEdit_voltage_backup.setText("")
        self.status_motor_1.setText("")
        self.motor_1.setText(QCoreApplication.translate("myAGV", u"Motor", None))
        self.electricity_name1.setText(QCoreApplication.translate("myAGV", u"Electricity1", None))
        self.electricity_motor1.setText("")
        self.electricity_name_2.setText(QCoreApplication.translate("myAGV", u"Electricity2", None))
        self.electricity_motor2.setText("")
        self.status_radar.setText("")
        self.Radar.setText(QCoreApplication.translate("myAGV", u"Radar", None))
        self.electricity_name_3.setText(QCoreApplication.translate("myAGV", u"Electricity3", None))
        self.electricity_motor3.setText("")
        self.electricity_name_4.setText(QCoreApplication.translate("myAGV", u"Electricity4", None))
        self.electricity_motor4.setText("")
    # retranslateUi

