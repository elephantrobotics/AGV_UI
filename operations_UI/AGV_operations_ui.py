# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AGV_operations.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QTextBrowser, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_myAGV(object):
    def setupUi(self, myAGV):
        if not myAGV.objectName():
            myAGV.setObjectName(u"myAGV")
        myAGV.resize(869, 656)
        self.verticalLayout_8 = QVBoxLayout(myAGV)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.widget = QWidget(myAGV)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_17 = QHBoxLayout(self.widget)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(2, 2, 2, 2)
        self.sidebar = QFrame(self.widget)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.sidebar)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_language = QVBoxLayout()
        self.verticalLayout_language.setObjectName(u"verticalLayout_language")
        self.horizontalLayout_language = QHBoxLayout()
        self.horizontalLayout_language.setObjectName(u"horizontalLayout_language")
        self.label_language = QLabel(self.sidebar)
        self.label_language.setObjectName(u"label_language")
        self.label_language.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_language.addWidget(self.label_language)

        self.comboBox_language_selection = QComboBox(self.sidebar)
        self.comboBox_language_selection.setObjectName(u"comboBox_language_selection")

        self.horizontalLayout_language.addWidget(self.comboBox_language_selection)


        self.verticalLayout_language.addLayout(self.horizontalLayout_language)

        self.horizontalLayout_radar = QHBoxLayout()
        self.horizontalLayout_radar.setObjectName(u"horizontalLayout_radar")
        self.label_radar = QLabel(self.sidebar)
        self.label_radar.setObjectName(u"label_radar")
        self.label_radar.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_radar.addWidget(self.label_radar)

        self.radar_button = QPushButton(self.sidebar)
        self.radar_button.setObjectName(u"radar_button")

        self.horizontalLayout_radar.addWidget(self.radar_button)


        self.verticalLayout_language.addLayout(self.horizontalLayout_radar)


        self.verticalLayout_11.addLayout(self.verticalLayout_language)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_5)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.basic_control = QLabel(self.sidebar)
        self.basic_control.setObjectName(u"basic_control")
        self.basic_control.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_3.addWidget(self.basic_control)

        self.widget_2 = QWidget(self.sidebar)
        self.widget_2.setObjectName(u"widget_2")

        self.horizontalLayout_3.addWidget(self.widget_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_basic = QHBoxLayout()
        self.horizontalLayout_basic.setObjectName(u"horizontalLayout_basic")
        self.basic_control_button = QPushButton(self.sidebar)
        self.basic_control_button.setObjectName(u"basic_control_button")

        self.horizontalLayout_basic.addWidget(self.basic_control_button)

        self.basic_control_selection = QComboBox(self.sidebar)
        self.basic_control_selection.setObjectName(u"basic_control_selection")

        self.horizontalLayout_basic.addWidget(self.basic_control_selection)


        self.verticalLayout_4.addLayout(self.horizontalLayout_basic)


        self.verticalLayout_11.addLayout(self.verticalLayout_4)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_6)

        self.verticalLayout_map = QVBoxLayout()
        self.verticalLayout_map.setObjectName(u"verticalLayout_map")
        self.horizontalLayout_map = QHBoxLayout()
        self.horizontalLayout_map.setObjectName(u"horizontalLayout_map")
        self.label_map_nav = QLabel(self.sidebar)
        self.label_map_nav.setObjectName(u"label_map_nav")
        self.label_map_nav.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_map.addWidget(self.label_map_nav)

        self.save_map_button = QPushButton(self.sidebar)
        self.save_map_button.setObjectName(u"save_map_button")

        self.horizontalLayout_map.addWidget(self.save_map_button)


        self.verticalLayout_map.addLayout(self.horizontalLayout_map)

        self.horizontalLayout_map_build = QHBoxLayout()
        self.horizontalLayout_map_build.setObjectName(u"horizontalLayout_map_build")
        self.open_build_map = QPushButton(self.sidebar)
        self.open_build_map.setObjectName(u"open_build_map")

        self.horizontalLayout_map_build.addWidget(self.open_build_map)

        self.build_map_selection = QComboBox(self.sidebar)
        self.build_map_selection.setObjectName(u"build_map_selection")

        self.horizontalLayout_map_build.addWidget(self.build_map_selection)


        self.verticalLayout_map.addLayout(self.horizontalLayout_map_build)

        self.horizontalLayout_nav = QHBoxLayout()
        self.horizontalLayout_nav.setObjectName(u"horizontalLayout_nav")
        self.navigation_3d_button = QPushButton(self.sidebar)
        self.navigation_3d_button.setObjectName(u"navigation_3d_button")

        self.horizontalLayout_nav.addWidget(self.navigation_3d_button)

        self.navigation_button = QPushButton(self.sidebar)
        self.navigation_button.setObjectName(u"navigation_button")

        self.horizontalLayout_nav.addWidget(self.navigation_button)


        self.verticalLayout_map.addLayout(self.horizontalLayout_nav)


        self.verticalLayout_11.addLayout(self.verticalLayout_map)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_4)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.sidebar)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.widget_3 = QWidget(self.sidebar)
        self.widget_3.setObjectName(u"widget_3")

        self.horizontalLayout_2.addWidget(self.widget_3)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_palette = QHBoxLayout()
        self.horizontalLayout_palette.setObjectName(u"horizontalLayout_palette")
        self.color_palette = QTextEdit(self.sidebar)
        self.color_palette.setObjectName(u"color_palette")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.color_palette.sizePolicy().hasHeightForWidth())
        self.color_palette.setSizePolicy(sizePolicy)

        self.horizontalLayout_palette.addWidget(self.color_palette)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.sidebar)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.lineEdit_HEX = QLineEdit(self.sidebar)
        self.lineEdit_HEX.setObjectName(u"lineEdit_HEX")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_HEX.sizePolicy().hasHeightForWidth())
        self.lineEdit_HEX.setSizePolicy(sizePolicy1)

        self.horizontalLayout_7.addWidget(self.lineEdit_HEX)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_6 = QLabel(self.sidebar)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.lineEdit_RGB = QLineEdit(self.sidebar)
        self.lineEdit_RGB.setObjectName(u"lineEdit_RGB")

        self.horizontalLayout_8.addWidget(self.lineEdit_RGB)


        self.verticalLayout.addLayout(self.horizontalLayout_8)


        self.horizontalLayout_palette.addLayout(self.verticalLayout)

        self.horizontalLayout_palette.setStretch(0, 1)
        self.horizontalLayout_palette.setStretch(1, 1)

        self.verticalLayout_9.addLayout(self.horizontalLayout_palette)

        self.horizontalLayout_slider = QHBoxLayout()
        self.horizontalLayout_slider.setObjectName(u"horizontalLayout_slider")
        self.label_7 = QLabel(self.sidebar)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_slider.addWidget(self.label_7)

        self.horizontal_Slider = QSlider(self.sidebar)
        self.horizontal_Slider.setObjectName(u"horizontal_Slider")
        self.horizontal_Slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_slider.addWidget(self.horizontal_Slider)

        self.label_8 = QLabel(self.sidebar)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_slider.addWidget(self.label_8)


        self.verticalLayout_9.addLayout(self.horizontalLayout_slider)


        self.verticalLayout_11.addLayout(self.verticalLayout_9)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_3)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_9 = QLabel(self.sidebar)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setStyleSheet(u"font: 13pt \"Arial\";")

        self.horizontalLayout.addWidget(self.label_9)

        self.widget_4 = QWidget(self.sidebar)
        self.widget_4.setObjectName(u"widget_4")

        self.horizontalLayout.addWidget(self.widget_4)


        self.verticalLayout_10.addLayout(self.horizontalLayout)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.start_detection_button = QPushButton(self.sidebar)
        self.start_detection_button.setObjectName(u"start_detection_button")

        self.horizontalLayout_11.addWidget(self.start_detection_button)

        self.comboBox_testing = QComboBox(self.sidebar)
        self.comboBox_testing.setObjectName(u"comboBox_testing")

        self.horizontalLayout_11.addWidget(self.comboBox_testing)


        self.verticalLayout_10.addLayout(self.horizontalLayout_11)


        self.verticalLayout_11.addLayout(self.verticalLayout_10)


        self.horizontalLayout_17.addWidget(self.sidebar)

        self.interface_2 = QFrame(self.widget)
        self.interface_2.setObjectName(u"interface_2")
        self.interface_2.setFrameShape(QFrame.StyledPanel)
        self.interface_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.interface_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(8, 0, 0, 2)
        self.area_log = QFrame(self.interface_2)
        self.area_log.setObjectName(u"area_log")
        self.area_log.setFrameShape(QFrame.StyledPanel)
        self.area_log.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.area_log)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(2, 2, 2, 2)
        self.textBrowser = QTextBrowser(self.area_log)
        self.textBrowser.setObjectName(u"textBrowser")

        self.horizontalLayout_20.addWidget(self.textBrowser)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.log_clear = QPushButton(self.area_log)
        self.log_clear.setObjectName(u"log_clear")

        self.verticalLayout_3.addWidget(self.log_clear)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout_20.addLayout(self.verticalLayout_3)


        self.verticalLayout_6.addWidget(self.area_log)

        self.area_display = QFrame(self.interface_2)
        self.area_display.setObjectName(u"area_display")
        self.area_display.setFrameShape(QFrame.StyledPanel)
        self.area_display.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.area_display)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, 8, 6, 7)
        self.horizontalLayout_ipAddress = QHBoxLayout()
        self.horizontalLayout_ipAddress.setObjectName(u"horizontalLayout_ipAddress")
        self.IP_address = QLabel(self.area_display)
        self.IP_address.setObjectName(u"IP_address")

        self.horizontalLayout_ipAddress.addWidget(self.IP_address)

        self.lineEdit_3 = QLineEdit(self.area_display)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.horizontalLayout_ipAddress.addWidget(self.lineEdit_3)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_ipAddress.addItem(self.horizontalSpacer_5)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_ipAddress.addItem(self.horizontalSpacer)


        self.verticalLayout_5.addLayout(self.horizontalLayout_ipAddress)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.verticalLayout_main = QVBoxLayout()
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.status_battery_main = QLabel(self.area_display)
        self.status_battery_main.setObjectName(u"status_battery_main")
        self.status_battery_main.setMinimumSize(QSize(18, 18))
        self.status_battery_main.setMaximumSize(QSize(18, 18))
        self.status_battery_main.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_13.addWidget(self.status_battery_main)

        self.main_battery = QLabel(self.area_display)
        self.main_battery.setObjectName(u"main_battery")

        self.horizontalLayout_13.addWidget(self.main_battery)


        self.verticalLayout_main.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.electricity_main = QLabel(self.area_display)
        self.electricity_main.setObjectName(u"electricity_main")

        self.horizontalLayout_9.addWidget(self.electricity_main)

        self.lineEdit_power = QLineEdit(self.area_display)
        self.lineEdit_power.setObjectName(u"lineEdit_power")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_power.sizePolicy().hasHeightForWidth())
        self.lineEdit_power.setSizePolicy(sizePolicy2)
        self.lineEdit_power.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_9.addWidget(self.lineEdit_power)


        self.verticalLayout_main.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.voltage = QLabel(self.area_display)
        self.voltage.setObjectName(u"voltage")

        self.horizontalLayout_21.addWidget(self.voltage)

        self.lineEdit_voltage = QLineEdit(self.area_display)
        self.lineEdit_voltage.setObjectName(u"lineEdit_voltage")
        self.lineEdit_voltage.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_21.addWidget(self.lineEdit_voltage)


        self.verticalLayout_main.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.eletricity = QLabel(self.area_display)
        self.eletricity.setObjectName(u"eletricity")

        self.horizontalLayout_22.addWidget(self.eletricity)

        self.lineEdit_electricity = QLineEdit(self.area_display)
        self.lineEdit_electricity.setObjectName(u"lineEdit_electricity")
        self.lineEdit_electricity.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_22.addWidget(self.lineEdit_electricity)


        self.verticalLayout_main.addLayout(self.horizontalLayout_22)


        self.horizontalLayout_27.addLayout(self.verticalLayout_main)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_2)

        self.verticalLayout_backup = QVBoxLayout()
        self.verticalLayout_backup.setObjectName(u"verticalLayout_backup")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.status_battery_backup = QLabel(self.area_display)
        self.status_battery_backup.setObjectName(u"status_battery_backup")
        self.status_battery_backup.setMinimumSize(QSize(18, 18))
        self.status_battery_backup.setMaximumSize(QSize(18, 18))
        self.status_battery_backup.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_12.addWidget(self.status_battery_backup)

        self.backup_battery = QLabel(self.area_display)
        self.backup_battery.setObjectName(u"backup_battery")

        self.horizontalLayout_12.addWidget(self.backup_battery)


        self.verticalLayout_backup.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.power_backup = QLabel(self.area_display)
        self.power_backup.setObjectName(u"power_backup")

        self.horizontalLayout_23.addWidget(self.power_backup)

        self.lineEdit_power_backup = QLineEdit(self.area_display)
        self.lineEdit_power_backup.setObjectName(u"lineEdit_power_backup")
        self.lineEdit_power_backup.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_23.addWidget(self.lineEdit_power_backup)


        self.verticalLayout_backup.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.voltage_backup = QLabel(self.area_display)
        self.voltage_backup.setObjectName(u"voltage_backup")

        self.horizontalLayout_24.addWidget(self.voltage_backup)

        self.lineEdit_voltage_backup = QLineEdit(self.area_display)
        self.lineEdit_voltage_backup.setObjectName(u"lineEdit_voltage_backup")
        self.lineEdit_voltage_backup.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_24.addWidget(self.lineEdit_voltage_backup)


        self.verticalLayout_backup.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.eletricity_backup = QLabel(self.area_display)
        self.eletricity_backup.setObjectName(u"eletricity_backup")

        self.horizontalLayout_25.addWidget(self.eletricity_backup)

        self.lineEdit_electricity_backup = QLineEdit(self.area_display)
        self.lineEdit_electricity_backup.setObjectName(u"lineEdit_electricity_backup")
        self.lineEdit_electricity_backup.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_25.addWidget(self.lineEdit_electricity_backup)


        self.verticalLayout_backup.addLayout(self.horizontalLayout_25)


        self.horizontalLayout_27.addLayout(self.verticalLayout_backup)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_3)

        self.verticalLayout_motor = QVBoxLayout()
        self.verticalLayout_motor.setObjectName(u"verticalLayout_motor")
        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.status_motor_1 = QLabel(self.area_display)
        self.status_motor_1.setObjectName(u"status_motor_1")
        self.status_motor_1.setMinimumSize(QSize(18, 18))
        self.status_motor_1.setMaximumSize(QSize(18, 18))
        self.status_motor_1.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_15.addWidget(self.status_motor_1)

        self.motor_1 = QLabel(self.area_display)
        self.motor_1.setObjectName(u"motor_1")

        self.horizontalLayout_15.addWidget(self.motor_1)


        self.verticalLayout_motor.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.status_motor_2 = QLabel(self.area_display)
        self.status_motor_2.setObjectName(u"status_motor_2")
        self.status_motor_2.setMinimumSize(QSize(18, 18))
        self.status_motor_2.setMaximumSize(QSize(18, 18))
        self.status_motor_2.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_18.addWidget(self.status_motor_2)

        self.motor_2 = QLabel(self.area_display)
        self.motor_2.setObjectName(u"motor_2")

        self.horizontalLayout_18.addWidget(self.motor_2)


        self.verticalLayout_motor.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.status_motor_3 = QLabel(self.area_display)
        self.status_motor_3.setObjectName(u"status_motor_3")
        self.status_motor_3.setMinimumSize(QSize(18, 18))
        self.status_motor_3.setMaximumSize(QSize(18, 18))
        self.status_motor_3.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_19.addWidget(self.status_motor_3)

        self.motor_3 = QLabel(self.area_display)
        self.motor_3.setObjectName(u"motor_3")

        self.horizontalLayout_19.addWidget(self.motor_3)


        self.verticalLayout_motor.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.status_motor_4 = QLabel(self.area_display)
        self.status_motor_4.setObjectName(u"status_motor_4")
        self.status_motor_4.setMinimumSize(QSize(18, 18))
        self.status_motor_4.setMaximumSize(QSize(18, 18))
        self.status_motor_4.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_16.addWidget(self.status_motor_4)

        self.motor_4 = QLabel(self.area_display)
        self.motor_4.setObjectName(u"motor_4")

        self.horizontalLayout_16.addWidget(self.motor_4)


        self.verticalLayout_motor.addLayout(self.horizontalLayout_16)


        self.horizontalLayout_27.addLayout(self.verticalLayout_motor)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_4)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.status_radar = QLabel(self.area_display)
        self.status_radar.setObjectName(u"status_radar")
        self.status_radar.setMinimumSize(QSize(18, 18))
        self.status_radar.setMaximumSize(QSize(18, 18))
        self.status_radar.setStyleSheet(u"border-radius: 9px;\n"
"border: 1px solid")

        self.horizontalLayout_14.addWidget(self.status_radar)

        self.Radar = QLabel(self.area_display)
        self.Radar.setObjectName(u"Radar")

        self.horizontalLayout_14.addWidget(self.Radar)


        self.verticalLayout_2.addLayout(self.horizontalLayout_14)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_27.addLayout(self.verticalLayout_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_27)


        self.verticalLayout_7.addLayout(self.verticalLayout_5)


        self.verticalLayout_6.addWidget(self.area_display)

        self.verticalLayout_6.setStretch(0, 2)
        self.verticalLayout_6.setStretch(1, 1)

        self.horizontalLayout_17.addWidget(self.interface_2)

        self.horizontalLayout_17.setStretch(0, 1)
        self.horizontalLayout_17.setStretch(1, 3)

        self.verticalLayout_8.addWidget(self.widget)


        self.retranslateUi(myAGV)

        QMetaObject.connectSlotsByName(myAGV)
    # setupUi

    def retranslateUi(self, myAGV):
        myAGV.setWindowTitle(QCoreApplication.translate("myAGV", u"Form", None))
        self.label_language.setText(QCoreApplication.translate("myAGV", u"language", None))
        self.label_radar.setText(QCoreApplication.translate("myAGV", u"Laser Radar", None))
        self.radar_button.setText(QCoreApplication.translate("myAGV", u"on", None))
        self.basic_control.setText(QCoreApplication.translate("myAGV", u"Basic Control", None))
        self.basic_control_button.setText(QCoreApplication.translate("myAGV", u"on", None))
        self.label_map_nav.setText(QCoreApplication.translate("myAGV", u"Map Navigation", None))
        self.save_map_button.setText(QCoreApplication.translate("myAGV", u"Save Map", None))
        self.open_build_map.setText(QCoreApplication.translate("myAGV", u"Open Build Map", None))
        self.navigation_3d_button.setText(QCoreApplication.translate("myAGV", u"3D Navigation", None))
        self.navigation_button.setText(QCoreApplication.translate("myAGV", u"Navigation", None))
        self.label_4.setText(QCoreApplication.translate("myAGV", u"LED Control", None))
        self.label_5.setText(QCoreApplication.translate("myAGV", u"HEX", None))
        self.label_6.setText(QCoreApplication.translate("myAGV", u"RGB", None))
        self.label_7.setText(QCoreApplication.translate("myAGV", u"Luminance", None))
        self.label_8.setText(QCoreApplication.translate("myAGV", u"value", None))
        self.label_9.setText(QCoreApplication.translate("myAGV", u"Test", None))
        self.start_detection_button.setText(QCoreApplication.translate("myAGV", u"Start Detection", None))
        self.log_clear.setText(QCoreApplication.translate("myAGV", u"clear", None))
        self.IP_address.setText(QCoreApplication.translate("myAGV", u"IP Address", None))
        self.status_battery_main.setText("")
        self.main_battery.setText(QCoreApplication.translate("myAGV", u"Main Battery", None))
        self.electricity_main.setText(QCoreApplication.translate("myAGV", u"Power", None))
        self.voltage.setText(QCoreApplication.translate("myAGV", u"Voltage", None))
        self.eletricity.setText(QCoreApplication.translate("myAGV", u"Electricity", None))
        self.status_battery_backup.setText("")
        self.backup_battery.setText(QCoreApplication.translate("myAGV", u"Backup Battery", None))
        self.power_backup.setText(QCoreApplication.translate("myAGV", u"Power", None))
        self.voltage_backup.setText(QCoreApplication.translate("myAGV", u"Voltage", None))
        self.eletricity_backup.setText(QCoreApplication.translate("myAGV", u"Electricity", None))
        self.status_motor_1.setText("")
        self.motor_1.setText(QCoreApplication.translate("myAGV", u"Motor 1", None))
        self.status_motor_2.setText("")
        self.motor_2.setText(QCoreApplication.translate("myAGV", u"Motor 2", None))
        self.status_motor_3.setText("")
        self.motor_3.setText(QCoreApplication.translate("myAGV", u"Motor 3", None))
        self.status_motor_4.setText("")
        self.motor_4.setText(QCoreApplication.translate("myAGV", u"motor 4", None))
        self.status_radar.setText("")
        self.Radar.setText(QCoreApplication.translate("myAGV", u"Radar", None))
    # retranslateUi

