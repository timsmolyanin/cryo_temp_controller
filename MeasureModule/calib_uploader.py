#script to launch refrig application
import sys

from PySide6.QtWidgets import (QApplication, QMainWindow)
from PySide6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os
import paramiko

class UploaderMainWindow(object):

    controller_config_path = "wk/measure_module/Sensors/ConfigFolder"

    def __init__(self, MainWindow) -> None:
        try:
            self.mw = MainWindow
            self.get_dir()
            self.setupUi(MainWindow)
        except Exception as err:
            self.resolve_exception(err, 1)


    def get_dir(self):
        if getattr(sys, 'frozen', False):
            cur_path = os.path.dirname(sys.executable)
        elif __file__:
            cur_path = os.path.dirname(__file__)
        self.cur_path = str(cur_path.replace('\\', '/'))


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 130)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.infoLabel = QtWidgets.QLabel(parent=MainWindow)
        self.infoLabel.setGeometry(QtCore.QRect(10, 0, 300, 30))
        self.infoLabel.setText('Upload sensor calibration file to the cryo controller')

        self.ipLabel = QtWidgets.QLabel(parent=MainWindow)
        self.ipLabel.setGeometry(QtCore.QRect(10, 40, 80, 30))
        self.ipLabel.setText('Controller IP:')

        self.ipEdit = QtWidgets.QLineEdit(parent=MainWindow)
        self.ipEdit.setGeometry(QtCore.QRect(90, 40, 120, 30))
        self.ipEdit.setText("192.168.0.104")

        self.uploadButton = QtWidgets.QPushButton(parent=MainWindow)
        self.uploadButton.setGeometry(QtCore.QRect(10, 80, 75, 30))
        self.uploadButton.setText("Upload file")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.uploadButton.clicked.connect(self.choose_file)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("CalibrationUploader", "CalibrationUploader"))


    def choose_file(self):
        try:
            f_dialog = QtWidgets.QFileDialog(parent=self.mw)
            f_name = f_dialog.getOpenFileName(self.mw, f'Choose calib file...', f'{self.cur_path}', f'Calibration files (*.340 *.txt)')
            print(f_name[0])
            self.upload_file(str(f_name[0]))
        except Exception as err:
            self.resolve_exception(err)
    

    def upload_file(self, file_path):
        try:
            file_name = file_path.split('/')[-1]
            wb_ip = self.ipEdit.text()
            print(wb_ip, file_path)
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #auto add keys
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(wb_ip, username='root', password='wirenboard')
            sftp = ssh.open_sftp()
            sftp.put(file_path, f'{self.controller_config_path}/{file_name}')
            sftp.close()
            ssh.close()
            success_msg_box = QtWidgets.QMessageBox()
            success_msg_box.setText(f"Successfully uploaded file {file_name}")
            success_msg_box.exec()

        except Exception as err:
            self.resolve_exception(err)
        
    
    def resolve_exception(self, err, severity = 0):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(f'{err.__class__.__name__}:{err}')
        error_dialog.setWindowTitle("Error")
        error_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        error_dialog.exec()
        if severity>0:
            exit()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mw = QMainWindow()
    window = UploaderMainWindow(mw)
    mw.show()
    app.exec()
