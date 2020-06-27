"""The program is used to draw real-time graphs of the
load and effort of an athlete training on the simulator."""

import sys
import glob
import serial

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QStackedLayout

import pyqtgraph as pg

class MainCode(QMainWindow):
    """MainCode of program"""
    def __init__(self, parent=None):
        super(MainCode, self).__init__(parent)

        self.resize(1700, 900)
        self.setWindowTitle('Графики для Тренажёра')

        self.stages = QStackedLayout()

        self.main_stage = QWidget()
        self.main_stage.resize(1700, 900)
        self.graph_stage = QWidget()
        self.graph_stage.resize(1700, 900)
        self.settings_stage = QWidget()
        self.settings_stage.resize(1700, 900)

        self.create_main_stage()
        self.create_graph_stage()
        self.create_settings_stage()

        self.stages.addWidget(self.main_stage)
        self.stages.addWidget(self.graph_stage)
        self.stages.addWidget(self.settings_stage)
        self.stages.setCurrentIndex(0)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.stages)

        self.setCentralWidget(self.main_widget)


        #self.setLayout(self.stages)
        #self.main_vbox.addLayout(self.stages)

        self.show()

    def create_main_stage(self):
        """constructor main stage"""
        font_obj_for_label = QtGui.QFont('Segoe UI', pointSize=50)
        alignment_params_top = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        alignment_params_bottom = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter

        self.main_hbox = QtWidgets.QHBoxLayout()
        self.vbox_for_first_column = QtWidgets.QVBoxLayout()
        self.vbox_for_second_column = QtWidgets.QVBoxLayout()
        self.vbox_for_third_column = QtWidgets.QVBoxLayout()

        self.port_label = QtWidgets.QLabel("Порт")
        self.port_label.setFont(font_obj_for_label)
        self.vbox_for_first_column.addWidget(self.port_label, alignment=alignment_params_bottom)

        self.port_combobox = QtWidgets.QComboBox()
        self.port_combobox.setStyleSheet("font: bold;font-size:40px;")
        self.vbox_for_first_column.addWidget(self.port_combobox, alignment=alignment_params_top)

        self.find_and_put_com_port_in_combobox()

        self.update_btn = QtWidgets.QPushButton('Обновить порт')
        self.update_btn.setStyleSheet("font: bold;font-size:40px;")
        self.update_btn.setFixedSize(300, 90)
        self.update_btn.clicked.connect(self.find_and_put_com_port_in_combobox)
        self.vbox_for_first_column.addWidget(self.update_btn, alignment=alignment_params_top)

        self.speed_label = QtWidgets.QLabel("Скорость")
        self.speed_label.setFont(font_obj_for_label)
        self.vbox_for_first_column.addWidget(self.speed_label, alignment=alignment_params_top)

        self.speed_combobox = QtWidgets.QComboBox()
        self.speed_combobox.setStyleSheet("font: bold;font-size:40px;")
        self.speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        for item in self.speeds:
            self.speed_combobox.addItem(item)
        self.speed_combobox.setCurrentText('115200')
        self.vbox_for_first_column.addWidget(self.speed_combobox, alignment=alignment_params_top)

        self.connect_com_port_btn = QtWidgets.QPushButton('Подключить')
        self.connect_com_port_btn.setStyleSheet("font: bold;font-size:70px;")
        self.connect_com_port_btn.setFixedSize(500, 100)
        self.connect_com_port_btn.clicked.connect(self.try_to_connect_com_port)
        self.vbox_for_second_column.addWidget(self.connect_com_port_btn, alignment=alignment_params_bottom)

        self.vbox_for_second_column.addSpacing(100)

        self.start_btn = QtWidgets.QPushButton('Старт')
        self.start_btn.setStyleSheet("font: bold;font-size:70px;")
        self.start_btn.setFixedSize(500, 100)
        self.start_btn.clicked.connect(self.go_to_graph_stage)
        self.vbox_for_second_column.addWidget(self.start_btn, alignment=alignment_params_top)

        self.settings_btn = QtWidgets.QPushButton('Настройки')
        self.settings_btn.setStyleSheet("font: bold;font-size:70px;")
        self.settings_btn.setFixedSize(500, 100)
        self.settings_btn.clicked.connect(self.go_to_setting_stage)
        self.vbox_for_third_column.addWidget(self.settings_btn, alignment=alignment_params_top)

        self.main_hbox.addLayout(self.vbox_for_first_column)
        self.main_hbox.addLayout(self.vbox_for_second_column)
        self.main_hbox.addLayout(self.vbox_for_third_column)
        self.main_stage.setLayout(self.main_hbox)

    def create_graph_stage(self):
        """constructor graph stage"""
        self.hbox_for_first_graph = QtWidgets.QHBoxLayout()
        self.hbox_for_second_grahp = QtWidgets.QHBoxLayout()
        self.main_graph_vbox = QtWidgets.QVBoxLayout()

        self.line_color_force_time = 'red'
        self.line_color_amplitude_time = 'red'

        alignment_params_top = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter

        self.back_to_main_stage = QtWidgets.QPushButton('Назад')
        self.back_to_main_stage.setStyleSheet("font-size:35px;")
        self.back_to_main_stage.setFixedSize(100, 50)
        self.back_to_main_stage.clicked.connect(self.go_to_main_stage)
        self.main_graph_vbox.addWidget(self.back_to_main_stage, alignment=alignment_params_top)

        self.plot_force_time = pg.PlotWidget()
        self.plot_force_time.showGrid(x=True, y=True)
        self.hbox_for_first_graph.addWidget(self.plot_force_time)
        self.main_graph_vbox.addLayout(self.hbox_for_first_graph)

        self.plot_amplitude_time = pg.PlotWidget()
        self.plot_amplitude_time.showGrid(x=True, y=True)
        self.hbox_for_second_grahp.addWidget(self.plot_amplitude_time)
        self.main_graph_vbox.addLayout(self.hbox_for_second_grahp)

        self.graph_stage.setLayout(self.main_graph_vbox)

    def create_settings_stage(self):
        """constructor settings stage"""
        self.main_vbox = QtWidgets.QVBoxLayout()
        self.hbox_for_groupbox = QtWidgets.QHBoxLayout()
        self.vbox_for_hbox_for_force_time_box = QtWidgets.QVBoxLayout()
        self.vbox_for_hbox_for_amplitude_time_box = QtWidgets.QVBoxLayout()
        self.vbox_for_force_time_box = QtWidgets.QVBoxLayout()
        self.vbox_for_amplitude_time_box = QtWidgets.QVBoxLayout()
        self.hbox_for_force_time_box = QtWidgets.QHBoxLayout()
        self.hbox_for_amplitude_time_box = QtWidgets.QHBoxLayout()
        self.hbox_for_force_time_show_or_no_gragh = QtWidgets.QHBoxLayout()
        self.hbox_for_amplitude_time_show_or_no_gragh = QtWidgets.QHBoxLayout()


        alignment_params_top = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        alignment_params_bottom = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter

        font_obj_for_label = QtGui.QFont('Segoe UI', pointSize=30)

        self.box_for_force_time_graph = QtWidgets.QGroupBox()
        self.box_for_amplitude_time_graph = QtWidgets.QGroupBox()

        self.settings_label = QtWidgets.QLabel("Настройки")
        self.settings_label.setStyleSheet("font: bold;font-size:70px;")
        self.settings_label.setFont(font_obj_for_label)

        self.main_vbox.addWidget(self.settings_label, alignment = alignment_params_top)

        self.force_time_label = QtWidgets.QLabel("График усилие-время")
        self.force_time_label.setStyleSheet("font: bold;font-size:70px;")
        self.force_time_label.setFont(font_obj_for_label)
        self.vbox_for_force_time_box.addWidget(self.force_time_label, alignment=QtCore.Qt.AlignTop)

        self.force_time_show_or_not_label = QtWidgets.QLabel("Показывать?")
        self.force_time_show_or_not_label.setStyleSheet("font-size:40px;")
        self.force_time_show_or_not_label.setFont(font_obj_for_label)
        self.hbox_for_force_time_show_or_no_gragh.addWidget(self.force_time_show_or_not_label, alignment=QtCore.Qt.AlignRight)

        self.checkbox_force_time = QtWidgets.QCheckBox(self)
        self.checkbox_force_time.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
        self.checkbox_force_time.resize(100, 100)
        self.checkbox_force_time.setChecked(True)
        self.hbox_for_force_time_show_or_no_gragh.addWidget(self.checkbox_force_time)

        self.vbox_for_force_time_box.addLayout(self.hbox_for_force_time_show_or_no_gragh)

        self.time_units_show_time_label = QtWidgets.QLabel("Единицы измерения времени")
        self.time_units_show_time_label.setFont(font_obj_for_label)
        self.vbox_for_force_time_box.addWidget(self.time_units_show_time_label)

        self.time_unit_force_time_combobox = QtWidgets.QComboBox()
        self.time_unit_force_time_combobox.setStyleSheet("font: bold;font-size:40px;")
        self.time_units = ['Миллисекунда', 'Секунда', 'Минута', 'Час']
        for item in self.time_units:
            self.time_unit_force_time_combobox.addItem(item)
        self.time_unit_force_time_combobox.setCurrentText('Миллисекуда')
        self.vbox_for_force_time_box.addWidget(self.time_unit_force_time_combobox)

        self.line_color_force_time_btn = QtWidgets.QPushButton('Выбрать цвет линии', self)
        self.line_color_force_time_btn.setStyleSheet("font-size:30px;")
        self.line_color_force_time_btn.setFixedSize(300, 100)
        self.line_color_force_time_btn.clicked.connect(self.background_color_window_force_time)
        self.vbox_for_force_time_box.addWidget(self.line_color_force_time_btn, alignment=QtCore.Qt.AlignCenter)

        self.box_for_force_time_graph.setLayout(self.vbox_for_force_time_box)

        self.vbox_for_hbox_for_force_time_box.addWidget(self.box_for_force_time_graph, alignment=QtCore.Qt.AlignJustify)
        self.hbox_for_groupbox.addLayout(self.vbox_for_hbox_for_force_time_box)

        self.hbox_for_groupbox.addSpacing(200)

        self.amplitude_time_label = QtWidgets.QLabel("График амплитуда-время")
        self.amplitude_time_label.setStyleSheet("font: bold;font-size:70px;")
        self.amplitude_time_label.setFont(font_obj_for_label)
        self.vbox_for_amplitude_time_box.addWidget(self.amplitude_time_label, alignment=QtCore.Qt.AlignTop)

        self.amplitude_time_show_or_not_label = QtWidgets.QLabel("Показывать?")
        self.amplitude_time_show_or_not_label.setStyleSheet("font-size:40px;")
        self.amplitude_time_show_or_not_label.setFont(font_obj_for_label)
        self.hbox_for_amplitude_time_show_or_no_gragh.addWidget(self.amplitude_time_show_or_not_label, alignment=QtCore.Qt.AlignRight)

        self.checkbox_amplitude_time = QtWidgets.QCheckBox(self)
        self.checkbox_amplitude_time.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
        self.checkbox_amplitude_time.resize(100, 100)
        self.checkbox_amplitude_time.setChecked(True)
        self.hbox_for_amplitude_time_show_or_no_gragh.addWidget(self.checkbox_amplitude_time)

        self.vbox_for_amplitude_time_box.addLayout(self.hbox_for_amplitude_time_show_or_no_gragh)

        self.time_units_show_time_label = QtWidgets.QLabel("Единицы измерения времени")
        self.time_units_show_time_label.setFont(font_obj_for_label)
        self.vbox_for_amplitude_time_box.addWidget(self.time_units_show_time_label)

        self.time_unit_amplitude_time_combobox = QtWidgets.QComboBox()
        self.time_unit_amplitude_time_combobox.setStyleSheet("font: bold;font-size:40px;")
        self.time_units = ['Миллисекунда', 'Секунда', 'Минута', 'Час']
        for item in self.time_units:
            self.time_unit_amplitude_time_combobox.addItem(item)
        self.time_unit_amplitude_time_combobox.setCurrentText('Миллисекуда')
        self.vbox_for_amplitude_time_box.addWidget(self.time_unit_amplitude_time_combobox)

        self.amplitude_units_show_time_label = QtWidgets.QLabel("Единицы измерения амплитуды")
        self.amplitude_units_show_time_label.setFont(font_obj_for_label)
        self.vbox_for_amplitude_time_box.addWidget(self.amplitude_units_show_time_label)

        self.amplitude_unit_amplitude_time_combobox = QtWidgets.QComboBox()
        self.amplitude_unit_amplitude_time_combobox.setStyleSheet("font: bold;font-size:40px;")
        self.amplitude_units = ['Миллиметр', 'Сантиметр', 'Метр']
        for item in self.amplitude_units:
            self.amplitude_unit_amplitude_time_combobox.addItem(item)
        self.amplitude_unit_amplitude_time_combobox.setCurrentText('Метр')
        self.vbox_for_amplitude_time_box.addWidget(self.amplitude_unit_amplitude_time_combobox)

        self.line_color_amplitude_time_btn = QtWidgets.QPushButton('Выбрать цвет линии', self)
        self.line_color_amplitude_time_btn.setStyleSheet("font-size:30px;")
        self.line_color_amplitude_time_btn.setFixedSize(300, 100)
        self.line_color_amplitude_time_btn.clicked.connect(self.background_color_window_amplitude_time)
        self.vbox_for_amplitude_time_box.addWidget(self.line_color_amplitude_time_btn, alignment=QtCore.Qt.AlignCenter)

        self.box_for_amplitude_time_graph.setLayout(self.vbox_for_amplitude_time_box)

        self.hbox_for_groupbox.addWidget(self.box_for_amplitude_time_graph, alignment=QtCore.Qt.AlignJustify)

        self.main_vbox.addLayout(self.hbox_for_groupbox)

        self.save_settings_and_to_to_main_stage = QtWidgets.QPushButton('Сохранить и выйти')
        self.save_settings_and_to_to_main_stage.setStyleSheet("font-size:20px;")
        self.save_settings_and_to_to_main_stage.setFixedSize(300, 100)
        self.save_settings_and_to_to_main_stage.clicked.connect(self.go_to_main_stage)
        self.main_vbox.addWidget(self.save_settings_and_to_to_main_stage, alignment=alignment_params_bottom)

        self.settings_stage.setLayout(self.main_vbox)

    def try_to_connect_com_port(self):
        #что-то типа такого 
        self.ser = serial.Serial()
        self.ser.port = self.port_combobox.currentData()
        self.ser.baudrate = self.speed_combobox.currentData()
        self.ser.open()

        #что-то из этого 
        self.ser.readline()
        self.ser.readlines()
        self.ser.read()
        self.ser.read_until()

    def background_color_window_force_time(self):
        """creata window to choose color"""
        background_color = QtWidgets.QColorDialog.getColor(parent=self, title='Выбор цвета фона')
        if background_color.isValid():
            self.line_color_force_time = background_color

    def background_color_window_amplitude_time(self):
        """creata window to choose color"""
        background_color = QtWidgets.QColorDialog.getColor(parent=self, title='Выбор цвета фона')
        if background_color.isValid():
            self.line_color_amplitude_time = background_color

    def find_and_put_com_port_in_combobox(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        if len(result) > 0:
            for element in result:
                self.port_combobox.addItem(str(element))

    def go_to_main_stage(self):
        """set main stage"""
        self.stages.setCurrentIndex(0)

    def go_to_graph_stage(self):
        """set graph stage"""


        a = [1, 1, 2, 3, 5, 8, 13]
        b = [2, 3, 5, 8, 13, 21, 34]
        self.plot_force_time.plot(a, b, pen=self.line_color_force_time)
        
        
        self.stages.setCurrentIndex(1)

    def go_to_setting_stage(self):
        """set setting stage"""
        self.stages.setCurrentIndex(2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainCode()
    sys.exit(app.exec_())
