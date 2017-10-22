#!/usr/bin/env python3
# coding=utf-8
# by KBdancer@92ez.com

from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QGroupBox, QButtonGroup, QTextBrowser, QHBoxLayout, QComboBox
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QDialog, QTableWidgetItem, QAbstractItemView, QHeaderView, QRadioButton, QSpinBox, QFileDialog
from PyQt5.QtWidgets import QDesktopWidget, QLineEdit, QInputDialog, QGridLayout, QLabel, QPushButton, QFrame
from PyQt5.QtGui import QIcon, QCursor, QColor
from PyQt5.QtCore import Qt, QSize, QTimer
from pyexcel_xls import get_data
from pyexcel_xls import save_data
from sys import platform
import serial.tools.list_ports
import binascii
import sqlite3
import serial
import time
import sys
import os


class ToyMainWindow(QWidget):
    def __init__(self):
        super(ToyMainWindow, self).__init__()
        self.db_settings = get_settings_from_db()
        self.init_main_ui()

    def init_main_ui(self):
        print('Start time: '+get_current_time())
        # 设置主窗体
        self.setGeometry(300, 300, 700, 400)
        self.setObjectName("mainWindowBox")
        self.setWindowTitle("QR-DETECTOR Pro V4.0")
        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + "/resource/logo1.jpeg"))
        # self.setWindowOpacity(0.5)

        # 设置工具栏
        # 运行按钮
        self.menu_button_run = QPushButton('Run')
        self.menu_button_run.setObjectName('button_start')
        self.menu_button_run.clicked.connect(self.start_run_program)

        # 停止按钮
        self.menu_button_stop = QPushButton('Stop')
        self.menu_button_stop.setObjectName('button_stop')
        self.menu_button_stop.clicked.connect(self.stop_run_program)
        self.menu_button_stop.setDisabled(True)

        # 设置按钮
        self.menu_button_setting = QPushButton('Settings')
        self.menu_button_setting.setObjectName('button_setting')
        self.menu_button_setting.clicked.connect(self.setting_config)

        # 导出按钮
        self.menu_button_export = QPushButton('Export')
        self.menu_button_export.setObjectName('button_export')
        self.menu_button_export.clicked.connect(self.excel_export)

        # 导入按钮
        self.menu_button_import = QPushButton('Import')
        self.menu_button_import.setObjectName('button_import')
        self.menu_button_import.clicked.connect(self.excel_import)

        # 关于按钮
        self.menu_button_about = QPushButton('About')
        self.menu_button_about.setObjectName('button_about')
        self.menu_button_about.clicked.connect(self.show_about)

        # 设置数据表
        self.data_table = QTableWidget()
        self.data_table.setObjectName("table_dataList")
        self.data_table.setColumnCount(4)
        self.data_table.setRowCount(0)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.verticalHeader().setDefaultSectionSize(30)
        self.data_table.horizontalHeader().setVisible(False)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setFrameShape(QFrame.NoFrame)
        self.data_table.setAlternatingRowColors(True)

        self.query_data_from_db()

        # 设置菜单栏Layout
        menu_bar_layout = QHBoxLayout()
        menu_bar_layout.setContentsMargins(10, 8, 10, 0)
        menu_bar_layout.setObjectName("layout_menu")
        menu_bar_layout.addWidget(self.menu_button_run)
        menu_bar_layout.addWidget(self.menu_button_stop)
        menu_bar_layout.addWidget(self.menu_button_import)
        menu_bar_layout.addWidget(self.menu_button_export)
        menu_bar_layout.addWidget(self.menu_button_setting)
        menu_bar_layout.addWidget(self.menu_button_about)
        menu_bar_layout.addStretch(1)

        # 设置表格Layout
        table_layout = QVBoxLayout()
        table_layout.setObjectName("layout_dataList")
        table_layout.setSizeConstraint(table_layout.SetFixedSize)
        table_layout.addWidget(self.data_table)

        # 样式表
        self.style = '''
            #mainWindowBox{
                background-color:#ffffff;
                padding:0px;
            }
            #table_dataList{
                background-color:#eee
            }
        '''
        self.setStyleSheet(self.style)

        # 整体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(menu_bar_layout)
        main_layout.addLayout(table_layout)
        self.setLayout(main_layout)
        self.init_settings()

    def init_settings(self):
        self.serial_mcu = ''
        try:
            self.serial_name_mcu = self.db_settings['mcu_port']
            self.serial_mcu = serial.Serial(self.serial_name_mcu, 9600, timeout=0)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Can not open MCU port %s" % self.serial_name_mcu)
            self.menu_button_run.setDisabled(True)
            # self.setting_config()

    def query_data_from_db(self):
        # 初始化读取扫描数据
        record_list = get_records_from_db()
        self.data_table.setRowCount(len(record_list))
        for item in record_list:
            item_index = record_list.index(item)
            self.data_table.setItem(item_index, 0, QTableWidgetItem(str(item['id'])))
            self.data_table.setItem(item_index, 1, QTableWidgetItem(item['barcode']))
            self.data_table.setItem(item_index, 2, QTableWidgetItem(item['status']))
            self.data_table.setItem(item_index, 3, QTableWidgetItem(item['createtime']))

            self.data_table.item(item_index, 0).setTextAlignment(Qt.AlignCenter)
            self.data_table.item(item_index, 1).setTextAlignment(Qt.AlignCenter)
            self.data_table.item(item_index, 2).setTextAlignment(Qt.AlignCenter)
            self.data_table.item(item_index, 3).setTextAlignment(Qt.AlignCenter)

            self.data_table.horizontalHeader().resizeSection(0, 50)
            self.data_table.horizontalHeader().resizeSection(1, 350)
            self.data_table.horizontalHeader().resizeSection(2, 150)
            # self.data_table.horizontalHeader().resizeSection(3, 100)

            if item['status'] != "NORMAL":
                self.data_table.item(item_index, 0).setForeground(QColor(238, 21, 21))
                self.data_table.item(item_index, 1).setForeground(QColor(238, 21, 21))
                self.data_table.item(item_index, 2).setForeground(QColor(238, 21, 21))
                self.data_table.item(item_index, 3).setForeground(QColor(238, 21, 21))

    def start_run_program(self):
        try:
            # start motor run
            do_motor_run(self.serial_mcu)
            # make timer listen mcu port
            self.mcu_read_timer = QTimer(self)
            self.mcu_read_timer.timeout.connect(self.read_mcu_data)
            self.mcu_read_timer.setInterval(30)
            self.mcu_read_timer.start()

            self.menu_button_stop.setDisabled(False)
            self.menu_button_import.setDisabled(True)
            self.menu_button_export.setDisabled(True)
            self.menu_button_about.setDisabled(True)
            self.menu_button_setting.setDisabled(True)
            self.menu_button_run.setDisabled(True)

        except serial.SerialException as e:
            QMessageBox.critical(self, "Error", "Can not open port %s" % self.serial_name_mcu)

    def read_mcu_data(self):
        mcu_data_string = self.serial_mcu.readline()
        if len(mcu_data_string) > 0 and mcu_data_string == b'\xa1':
            try:
                do_motor_stop(self.serial_mcu)
                self.serial_scanner = self.db_settings['scanner_port']
                ser_scanner = serial.Serial(self.serial_scanner, 15200, timeout=0)
                # open scanner
                begin_bytes = []
                for i in "16540D".split():
                    begin_bytes.append(binascii.a2b_hex(i))
                ser_scanner.writelines(begin_bytes)

                time.sleep(self.db_settings['duration_read']/1000)
                read_scan_string = ''
                for x in range(0, 200):
                    this_byte = ser_scanner.read(1)
                    if this_byte != '\r':
                        read_scan_string += this_byte.decode('utf8')
                    else:
                        read_scan_string = ''
                stop_bytes = []
                for k in "16550D".split():
                    stop_bytes.append(binascii.a2b_hex(k))
                ser_scanner.writelines(stop_bytes)

                config_website = self.db_settings['website'] + self.db_settings['key_id']
                # read nothing
                if len(read_scan_string) < 1:
                    item_status = 'LOST BARCODE'
                    show_warning(self.serial_mcu)
                elif config_website in read_scan_string:
                    if config_website == read_scan_string:
                        if self.db_settings['repeat'] == 'pass':
                            item_status = 'NORMAL'
                        else:
                            item_status = 'BAD PATTERN'
                            show_warning(self.serial_mcu)
                    else:
                        item_status = 'NORMAL'
                else:
                    item_status = 'BAD PATTERN'
                    show_warning(self.serial_mcu)

                item_website = read_scan_string
                item_createtime = get_current_time()
                insert_item_sql = """INSERT INTO records(`barcode`,`status`,`createtime`) VALUES(?,?,?)"""
                try:
                    my_sqlite_db = Database()
                    my_sqlite_db.insert(insert_item_sql, [item_website, item_status, item_createtime])
                    print('save item ok')
                    self.query_data_from_db()
                    time.sleep(self.db_settings['duration_wait']/1000)
                    do_motor_run(self.serial_mcu)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

    def stop_run_program(self):
        try:
            do_motor_stop(self.serial_mcu)

            self.menu_button_stop.setDisabled(True)
            self.menu_button_import.setDisabled(False)
            self.menu_button_export.setDisabled(False)
            self.menu_button_about.setDisabled(False)
            self.menu_button_setting.setDisabled(False)
            self.menu_button_run.setDisabled(False)

        except serial.SerialException as e:
            QMessageBox.critical(self, "Error", "Can not open port %s" % self.serial_name_mcu)

    def excel_import(self):
        importFileName, importFileType = QFileDialog.getOpenFileName(self, 'Openfile', './', 'xls Files (*.xls)')
        if len(importFileName) < 1:
            print('no file found')
        else:
            xls_data = get_data(importFileName)
            xls_list = []
            for sheet_n in xls_data.keys():
                this_xls_item = xls_data[sheet_n]
                if len(this_xls_item) > 0:
                    xls_list.append(this_xls_item)
            if len(xls_list) < 1:
                print('xls is empty')
            else:
                print('xls is usable')
                for item in xls_list:

                    item_id = item[0][0]
                    item_website = item[0][1]
                    item_status = item[0][2]
                    item_createtime = item[0][3]
                    insert_item_sql = """INSERT INTO records(`barcode`,`status`,`createtime`) VALUES(?,?,?)"""
                    try:
                        my_sqlite_db = Database()
                        my_sqlite_db.insert(insert_item_sql, [item_website, item_status, item_createtime])
                        print('save item ok')
                        self.query_data_from_db()
                    except Exception as e:
                        print(e)

    def excel_export(self):
        fileSave = QFileDialog.getSaveFileName(self, 'Savefile', './', 'xls Files (*.xls)')

    def setting_config(self):
        configWindow = ToyConfigWindow()
        configWindow.exec_()

    def show_about(self):
        QMessageBox.about(self, "About", "Author: KBdancer\nEmail: non3gov@gmail.com\nBlog: www.92ez.com\nAll Right reserved.")

    def check_coms(self):
        global TOTALCOUNT

        serial_name = self.scannerport.currentText()
        ser = serial.Serial(serial_name, 15200, timeout=3)
        read_string = ''
        begin_bytes = []
        for i in "16540D".split():
            begin_bytes.append(binascii.a2b_hex(i))
        ser.writelines(begin_bytes)
        for x in range(0, 100):
            this_byte = ser.read(1)
            if this_byte != '\r':
                read_string += str.decode(this_byte)
            else:
                print("finish")
                self.readText.append(read_string)

                self.myTable.setRowCount(TOTALCOUNT + 1)
                self.myTable.setHorizontalHeaderLabels(['id', 'content', 'status', 'time'])

                newItem = QTableWidgetItem(str(TOTALCOUNT + 1))
                self.myTable.setItem(TOTALCOUNT, 0, newItem)
                newItem = QTableWidgetItem(read_string)
                self.myTable.setItem(TOTALCOUNT, 1, newItem)
                if len(read_string) < 1:
                    newItem = QTableWidgetItem('LOST BARCODE')
                elif read_string == self.defaultText.text():
                    newItem = QTableWidgetItem('NORMAL')
                else:
                    newItem = QTableWidgetItem('BAD PATTERN')
                self.myTable.setItem(TOTALCOUNT, 2, newItem)
                newItem = QTableWidgetItem(self.get_current_time())
                self.myTable.setItem(TOTALCOUNT, 3, newItem)
                TOTALCOUNT += 1

                stop_bytes = []
                for k in "16550D".split():
                    stop_bytes.append(binascii.a2b_hex(k))
                ser.writelines(stop_bytes)
                ser.close()
                break


class ToyConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(ToyConfigWindow, self).__init__(parent)
        self.db_settings = get_settings_from_db()
        self.port_list = get_coms()
        if len(self.port_list) < 1:
            QMessageBox.critical(self, "Error", "Can not find any port")
        self.set_config_ui()

    def set_config_ui(self):
        # Main window style
        if platform == "linux" or platform == "linux2":
            # linux
            self.setGeometry(350, 350, 450, 390)
        elif platform == "darwin":
            # OS X
            self.setGeometry(350, 350, 450, 330)
        elif platform == "win32":
            # Windows...
            self.setGeometry(350, 350, 450, 330)

        self.setObjectName("configWindowBox")
        self.setWindowTitle("Settings")
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + "/resource/icon-set.png"))
        self.setModal(True)

        # -----------------------------------------------------------------------------
        # Package group
        barCodeLabel = QLabel('Web site :')
        barCodeLabel.setFixedWidth(55)
        self.barCodeInput = QLineEdit()
        self.barCodeInput.setText(self.db_settings['website'])
        packageBarCodeHLayout = QHBoxLayout()
        packageBarCodeHLayout.addWidget(barCodeLabel)
        packageBarCodeHLayout.addWidget(self.barCodeInput)

        barIDLabel = QLabel('ID :')
        barIDLabel.setFixedWidth(55)
        self.barIDInput = QLineEdit()
        self.barIDInput.setText(self.db_settings['key_id'])
        self.barIDInput.setFixedWidth(100)
        barRepeatLabel = QLabel('Repeat :')
        barRepeatLabel.setFixedWidth(55)
        self.barRepeatPassRadio = QRadioButton('pass')
        self.barRepeatNgRadio = QRadioButton('NG')

        if self.db_settings['repeat'] == "pass":
            self.barRepeatPassRadio.setChecked(True)
        else:
            self.barRepeatNgRadio.setChecked(True)

        self.repeatCodeBtns = QButtonGroup()
        self.repeatCodeBtns.addButton(self.barRepeatPassRadio, 0)
        self.repeatCodeBtns.addButton(self.barRepeatNgRadio, 1)

        packageBarIDHLayout = QHBoxLayout()
        packageBarIDHLayout.addWidget(barIDLabel)
        packageBarIDHLayout.addWidget(self.barIDInput)
        packageBarIDHLayout.addStretch(100)
        packageBarIDHLayout.addWidget(barRepeatLabel)
        packageBarIDHLayout.addWidget(self.barRepeatPassRadio)
        packageBarIDHLayout.addWidget(self.barRepeatNgRadio)
        packageBarIDHLayout.addStretch(1)

        packageInnerVLayout = QVBoxLayout()
        packageInnerVLayout.addLayout(packageBarCodeHLayout)
        packageInnerVLayout.addLayout(packageBarIDHLayout)

        packageGroupBox = QGroupBox('Package')
        packageGroupBox.setLayout(packageInnerVLayout)

        packageLayout = QHBoxLayout()
        packageLayout.addWidget(packageGroupBox)

        # -----------------------------------------------------------------------------
        # MCU group
        mcuPortLabel = QLabel('Port :')
        self.mcuCombobox = QComboBox()
        self.mcuCombobox.setFixedWidth(85)
        self.mcuCombobox.addItems(self.port_list)
        self.mcuCombobox.setCurrentText(self.db_settings['mcu_port'])
        mcuPortHLayout = QHBoxLayout()
        mcuPortHLayout.addWidget(mcuPortLabel)
        mcuPortHLayout.addWidget(self.mcuCombobox)
        mcuPortHLayout.addStretch(1)

        self.motorRunButton = QPushButton('Motor Run')
        # self.motorRunButton.setFixedWidth(85)
        self.motorRunButton.clicked.connect(self.motorRun)
        self.motorStopButton = QPushButton('Motor Stop')
        # self.motorStopButton.setFixedWidth(85)
        self.motorStopButton.clicked.connect(self.motorStop)
        motorVLayout = QVBoxLayout()
        motorVLayout.addWidget(self.motorRunButton)
        motorVLayout.addWidget(self.motorStopButton)

        mcuVLayout = QVBoxLayout()
        mcuVLayout.addLayout(mcuPortHLayout)
        mcuVLayout.addLayout(motorVLayout)

        mcuGroupBox = QGroupBox('MCU')
        mcuGroupBox.setLayout(mcuVLayout)

        # -----------------------------------------------------------------------------
        # Scanner group
        scannerPortLabel = QLabel('Port :')
        self.readerButton = QPushButton('Read')
        self.readerButton.clicked.connect(self.testScanner)
        self.scannerCombobox = QComboBox()
        self.scannerCombobox.setFixedWidth(85)
        self.scannerCombobox.addItems(self.port_list)
        self.scannerCombobox.setCurrentText(self.db_settings['scanner_port'])
        scannerPortHLayout = QHBoxLayout()
        scannerPortHLayout.addWidget(scannerPortLabel)
        scannerPortHLayout.addWidget(self.scannerCombobox)
        scannerPortHLayout.addStretch(1)
        scannerPortHLayout.addWidget(self.readerButton)

        self.readerTextBox = QTextBrowser()
        # self.readerTextBox.setFixedHeight(0)
        readerHLayout = QHBoxLayout()
        readerHLayout.addWidget(self.readerTextBox)

        scannerVLayout = QVBoxLayout()
        scannerVLayout.addLayout(scannerPortHLayout)
        scannerVLayout.addLayout(readerHLayout)

        scannerGroupBox = QGroupBox('Scanner')
        scannerGroupBox.setLayout(scannerVLayout)

        comsLayout = QHBoxLayout()
        comsLayout.addWidget(mcuGroupBox)
        comsLayout.addWidget(scannerGroupBox)

        # -----------------------------------------------------------------------------
        # Duration group
        durationReadLabel = QLabel('How long for read a bar code(ms) :')
        durationReadLabel.setFixedWidth(280)
        self.durationReadSpinBox = QSpinBox()
        self.durationReadSpinBox.setMaximum(1000000)
        self.durationReadSpinBox.setValue(self.db_settings['duration_read'])
        durationReadHLayout = QHBoxLayout()
        durationReadHLayout.addWidget(durationReadLabel)
        durationReadHLayout.addWidget(self.durationReadSpinBox)

        durationWaitLabel = QLabel('How long for wait for next bar code(ms) :')
        durationWaitLabel.setFixedWidth(280)
        self.durationWaitSpinBox = QSpinBox()
        self.durationWaitSpinBox.setMaximum(1000000)
        self.durationWaitSpinBox.setValue(self.db_settings['duration_wait'])
        durationWaitHLayout = QHBoxLayout()
        durationWaitHLayout.addWidget(durationWaitLabel)
        durationWaitHLayout.addWidget(self.durationWaitSpinBox)

        durationInnerVLayout = QVBoxLayout()
        durationInnerVLayout.addLayout(durationReadHLayout)
        durationInnerVLayout.addLayout(durationWaitHLayout)

        durationGroupBox = QGroupBox('Duration')
        durationGroupBox.setLayout(durationInnerVLayout)

        durationLayout = QHBoxLayout()
        durationLayout.addWidget(durationGroupBox)

        # -----------------------------------------------------------------------------
        # Save button
        self.saveButton = QPushButton('Save')
        self.saveButton.setFixedWidth(80)
        self.saveButton.clicked.connect(self.saveSettings)

        saveSettingsHLayout = QHBoxLayout()
        saveSettingsHLayout.addWidget(self.saveButton)

        # Main window layout
        mainVLayout = QVBoxLayout()
        mainVLayout.addLayout(packageLayout)
        mainVLayout.addLayout(comsLayout)
        mainVLayout.addLayout(durationLayout)
        mainVLayout.addLayout(saveSettingsHLayout)

        # -----------------------------------------------------------------------------
        # exec
        self.style = '''
                    #configWindowBox{background-color:#f6f6f6}
                '''
        self.setStyleSheet(self.style)
        self.setLayout(mainVLayout)
        self.show()

    def saveSettings(self):
        cfg_website = self.barCodeInput.text()
        cfg_barcodeId = self.barIDInput.text()
        if self.repeatCodeBtns.checkedId() == 0:
            repeatHandel = 'pass'
        else:
            repeatHandel = 'NG'
        cfg_mcu_port = self.mcuCombobox.currentText()
        cfg_scanner_port = self.scannerCombobox.currentText()
        cfg_duration_read = self.durationReadSpinBox.text()
        cfg_duration_wait = self.durationWaitSpinBox.text()
        cfg_lasttime = get_current_time()

        if cfg_mcu_port == cfg_scanner_port:
            QMessageBox.critical(self, "Error", "MCU port can not be same as scanner port")
        else:
            if len(cfg_barcodeId) < 1:
                QMessageBox.critical(self, "Error", "ID can not be empty!")
            else:
                try:
                    my_sqlite_db = Database()
                    update_settings = """UPDATE settings SET website=?,key_id=?,repeat=?,mcu_port=?,scanner_port=?,duration_read=?,duration_wait=?,modify_time=? WHERE id = 1"""
                    my_sqlite_db.update(update_settings, [cfg_website, cfg_barcodeId, repeatHandel, cfg_mcu_port, cfg_scanner_port, cfg_duration_read, cfg_duration_wait, cfg_lasttime])
                    print('save settings ok')
                    self.close()
                except Exception as e:
                    print(e)

    def testScanner(self):
        self.serial_name_scanner = self.scannerCombobox.currentText()
        self.readerButton.setDisabled(True)
        self.readerTextBox.setText('Scanner reading...')
        try:
            self.ser_scanner = serial.Serial(self.serial_name_scanner, 15200, timeout=0)
            begin_bytes = []
            for i in "16540D".split():
                begin_bytes.append(binascii.a2b_hex(i))
            self.ser_scanner.writelines(begin_bytes)

            # wait 2s for reading
            time.sleep(0.8)
            read_string = ''
            for x in range(0, 100):
                this_byte = self.ser_scanner.read(1)
                if this_byte != '\r':
                    read_string += this_byte.decode('utf8')
                else:
                    print("finish")

            if len(read_string) < 1:
                self.readerTextBox.setText('Can not to read')
            else:
                self.readerTextBox.setText('OK: ' + read_string)
            stop_bytes = []
            for k in "16550D".split():
                stop_bytes.append(binascii.a2b_hex(k))
            self.ser_scanner.writelines(stop_bytes)
            self.ser_scanner.close()
            self.readerButton.setDisabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Can not open port %s" % self.serial_name_scanner)
            self.readerTextBox.setText('Can not to read')
            self.readerButton.setDisabled(False)

    def motorRun(self):
        serial_name = self.mcuCombobox.currentText()
        ser = serial.Serial(serial_name, 9600, timeout=0)
        do_motor_run(ser)

    def motorStop(self):
        serial_name = self.mcuCombobox.currentText()
        ser = serial.Serial(serial_name, 9600, timeout=0)
        do_motor_stop(ser)


def show_warning(ser):
    warning_bytes = []
    for x in "5757a4a4".split():
        warning_bytes.append(binascii.a2b_hex(x))
        ser.writelines(warning_bytes)


def do_motor_run(ser):
    run_bytes = []
    for i in "56".split():
        run_bytes.append(binascii.a2b_hex(i))
    ser.writelines(run_bytes)


def do_motor_stop(ser):
    stop_bytes = []
    for i in "57".split():
        stop_bytes.append(binascii.a2b_hex(i))
    ser.writelines(stop_bytes)


def get_records_from_db():
    my_sqlite_db = Database()
    records = []
    try:
        query_by_sql = 'SELECT * FROM records order by id desc'
        query_list = my_sqlite_db.query(query_by_sql, '')

        for item in query_list:
            item_data = {
                "id": item[0],
                "barcode": item[1],
                "status": item[2],
                "createtime": item[3]
            }
            records.append(item_data)
        return records
    except Exception as e:
        print(e)


def get_settings_from_db():
    my_sqlite_db = Database()
    try:
        query_by_sql = 'SELECT * FROM settings'
        query_list = my_sqlite_db.query(query_by_sql, '')

        db_config = {
            "id": query_list[0][0],
            "website": query_list[0][1],
            "key_id": query_list[0][2],
            "repeat": query_list[0][3],
            "mcu_port": query_list[0][4],
            "scanner_port": query_list[0][5],
            "duration_read": query_list[0][6],
            "duration_wait": query_list[0][7],
            "modify_time": query_list[0][8]
        }

        return db_config
    except Exception as e:
        print(e)


def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def get_coms():
    port_list = list(serial.tools.list_ports.comports())
    port_name_list = []
    if len(port_list) < 1:
        print("The Serial port can't find!")
    else:
        for port in port_list:
            port_name_list.append(list(port)[0])
    return port_name_list


class Database:
    db = os.path.dirname(os.path.realpath(__file__)) + "/scanner.db"
    charset = 'utf8'

    def __init__(self):
        self.connection = sqlite3.connect(self.db)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except:
            self.connection.rollback()

    def update(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except:
            self.connection.rollback()

    def query(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def __del__(self):
        self.connection.close()


if __name__=="__main__":
    RUN_STATUS = 0
    app = QApplication(sys.argv)
    # toyMainView = ToyConfigWindow()
    toyMainView = ToyMainWindow()
    toyMainView.show()
    sys.exit(app.exec_())