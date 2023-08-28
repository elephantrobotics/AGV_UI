import subprocess
import sys
import threading
import time

from PySide6.QtCore import Signal,QCoreApplication,QObject
from PySide6.QtWidgets import QWidget,QApplication

from operations_UI.AGV_operations_ui import Ui_myAGV
from pymycobot.myagv import MyAgv

# MyAgv("com ")

# 继承QWidget类，以获取其属性和方法

lock=False
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_myAGV()
        self.ui.setupUi(self)
        self.agv=None #TODO use connect

        self.ui_set()


    def ui_set(self):

        def ui_params():

            language_params=[
                self.tr("English"),
                self.tr("Chinese")
            ]

            basic_control_params=[
                self.tr("Keyboard Control"),
                self.tr("Joystick Control")
            ]

            map_nav_params=[
                self.tr("Gmapping"),
                self.tr("Cartographer"),
                self.tr("3D Mapping")
            ]


            test_params=[
                self.tr("Motor"),
                self.tr("LED"),
                self.tr("3D Camera"),
                self.tr("Pump"),
                self.tr("Stop Testing")
            ]

            self.ui.comboBox_language_selection.addItems(language_params)
            self.ui.basic_control_selection.addItems(basic_control_params)
            self.ui.build_map_selection.addItems(map_nav_params)
            self.ui.comboBox_testing.addItems(test_params)

        def ui_buttons():
            self.ui.radar_button.setStyleSheet("background:red") #todo check
            self.ui.radar_button.setCheckable(True)
            self.ui.radar_button.toggle()

            self.ui.basic_control_button.setStyleSheet("background:red")
            self.ui.basic_control_button.setCheckable(True)
            self.ui.basic_control_button.toggle()



        def ui_functions():
            self.ui.radar_button.clicked.connect(self.radar_control)
            self.ui.basic_control_button.clicked.connect(self.basic_control)

            self.ui.save_map_button.clicked.connect(self.save_map)
            self.ui.open_build_map.clicked.connect(self.open_build_map)

            self.ui.navigation_3d_button.clicked.connect(self.navigation_3d)

            self.ui.navigation_button.clicked.connect(self.map_navigation)

            self.ui.log_clear.clicked.connect(self.clear_log)
            #todo led control;testing； only for radar_control;basic_control

            # todo ui-text broswer

        ui_params()
        ui_functions()
        ui_buttons()


    def get_current_time(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return current_time

    def language_selection(self):
        """
        根据选择语言切换
        :return:
        """
        lang=self.ui.comboBox_language_selection.currentText()

        if lang=="English" or lang=="英文":pass
        if lang=="Chinese" or lang=="中文":pass


    def button_status_switch(self,status):
        """
        set button logic
        :param status:button status
        :return:
        """
        button=[
            self.ui.basic_control_button,
            self.ui.save_map_button,
            self.ui.open_build_map,
            self.ui.navigation_button,
            self.ui.navigation_3d_button,
            self.ui.start_detection_button

        ]

        for btn in button:
            btn.setCheckable(status)

    def radar_control(self):
        if self.ui.radar_button.isChecked():
            self.ui.radar_button.setStyleSheet("background:green") #todo abstract
            self.ui.radar_button.setText(self.tr("on"))
            self.button_status_switch(False)

            print("open radar set")  #todo operation: open radar

            radar_open=threading.Thread(target=self.radar_open,daemon=True)
            radar_open.start()


        else:
            self.ui.radar_button.setStyleSheet("background:red")
            self.ui.radar_button.setText(self.tr("off"))
            self.button_status_switch(True)


            print("close radar set")
            #todo op:close radar

            #todo: how to close radar



    def basic_control(self):
        control_item_basic = self.ui.basic_control_selection.currentText()
        if self.ui.basic_control_button.isChecked():

            self.ui.basic_control_button.setText("on")


            #todo add error check
            if control_item_basic=="Keyboard Control" or control_item_basic=="键盘控制":
                print("open key") #todo op: open keyborad
                keyboard_open=threading.Thread(target=self.keyboard_open,daemon=True)
                keyboard_open.start()

            elif control_item_basic == "Joystick Control" or control_item_basic == "手柄控制":
                print("open joy")  # todo op: open joystick

                joystick_open=threading.Thread(target=self.joystick_open,daemon=True)
                joystick_open.start()
        else:
            self.ui.basic_control_button.setText("off")

            if control_item_basic == "Keyboard Control" or control_item_basic == "键盘控制":
                print("close key")  # todo op: close keyborad

            elif control_item_basic == "Joystick Control" or control_item_basic == "手柄控制":
                print("close joy")  # todo op: close joy

    # def basic_control(self):pass

    def clear_log(self):
        self.ui.textBrowser.clear()

    def map_navigation(self):pass



    def save_map(self):
        msg="save map"
        curren_time=self.get_current_time()
        self.ui.textBrowser.append('['+str(curren_time)+']'+' '+msg)


    def open_build_map(self):pass

    def navigation_3d(self):pass



    def radar_open(self):
        msg="radar_open"
        curren_time=self.get_current_time()
        self.ui.textBrowser.append('['+str(curren_time)+']'+' '+msg)
        launch_command="roslaunch ./src/myagv_odometry/launch/myagv_active.launch"
        exit_code=subprocess.call(launch_command,shell=True)

        # import subprocess
        #
        # launch_command = "roslaunch ~/myag... your_launch_file.launch"
        # exit_code = subprocess.call(launch_command, shell=True)
        #
        if exit_code == 0:
            print("Launch succeeded!")
        else:
            print("Launch failed with exit code:", exit_code)

    def radar_close(self):pass

    def keyboard_open(self):pass

    def joystick_open(self):pass

# 程序入口
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MyWidget()
    window.show()
    sys.exit(app.exec())
