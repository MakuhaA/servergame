import os
import pickle
import re
import socket
import sys
from datetime import datetime
from logging import INFO, Formatter, StreamHandler, getLogger
from threading import Thread
from time import sleep

from PyQt5 import QtWidgets

from admin.core.admin_mapping import EndpointMapper
from admin.UI.admin_ui import Ui_MainWindow
from general.decorators import anti_spam
from general.enums import RequestData, ResponseData, ServerEndpoint


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(
    Formatter('%(asctime)s - (%(name)s) - [%(levelname)s] - %(message)s')
)


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, server_ip, server_port):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ip = server_ip
        self.port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

        self.current_time = datetime.now()
        self.last_time = datetime.now()
        self.stop_timer = 0
        self.timer_min = 0  # Timer
        self.timer_sec = 0  # Timer
        self.current_task = 1  # Current task for students

        # Здесь прописываем событие нажатия на кнопку
        self.ui.button_1.clicked.connect(self.connect_to_server)
        self.ui.button_4.clicked.connect(self.button_add_team)
        self.ui.button_3.clicked.connect(self.button_3)
        self.ui.button_13.clicked.connect(self.button_13)
        self.ui.button_5.clicked.connect(self.button_5)
        self.ui.button_6.clicked.connect(self.button_6)
        self.ui.button_7.clicked.connect(self.init_task)
        self.ui.button_8.clicked.connect(self.open_tasks_pdf)
        # --------------------------------------------------------
        self.ui.button_11.clicked.connect(self.team_spectating_1)
        self.ui.button_12.clicked.connect(self.back_to_edit_server)
        self.ui.button_17.clicked.connect(self.back_to_edit_server)
        self.ui.button_18.clicked.connect(self.back_to_edit_server)
        self.ui.button_21.clicked.connect(self.back_to_edit_server)
        self.ui.button_24.clicked.connect(self.back_to_edit_server)
        self.ui.button_27.clicked.connect(self.back_to_edit_server)
        self.ui.button_14.clicked.connect(self.team_spectating_2)
        self.ui.button_15.clicked.connect(self.team_spectating_1)
        self.ui.button_16.clicked.connect(self.team_spectating_3)
        self.ui.button_19.clicked.connect(self.team_spectating_2)
        self.ui.button_20.clicked.connect(self.team_spectating_4)
        self.ui.button_22.clicked.connect(self.team_spectating_3)
        self.ui.button_23.clicked.connect(self.team_spectating_5)
        self.ui.button_25.clicked.connect(self.team_spectating_4)
        self.ui.button_26.clicked.connect(self.team_spectating_6)
        self.ui.button_28.clicked.connect(self.team_spectating_5)
        # --------------------------------------------------------
        self.ui.button_9.clicked.connect(self.start_competition)
        self.ui.button_10.clicked.connect(self.stop_competition)

    def _connect(self):
        if self.connected:
            return True
        try:
            self.client.settimeout(15)
        except OSError:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(15)
        try:
            self.client.connect((self.ip, self.port))
            self.client.setblocking(True)
            self.connected = True
            Thread(target=server_check, daemon=True, args=(my_app,)).start()
        except OSError:
            logger.info('Подключение к серверу не удалось')
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Подключение к серверу не удалось',
            )
            return False
        return True

    def _send_to_serv(self, data, err_msg):
        try:
            self.client.send(data)
        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                f'{err_msg}\n{err}',
            )
            return False
        return True

    # Функции которые выполняются при нажатии на кнопки

    # BUTTON 1 - Sign in to server
    def connect_to_server(self):
        try:
            if not self._connect():
                return
        except ConnectionRefusedError:
            logger.info('Не удалось подключиться')
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Connection Refused Error'
            )
            return 0
        request = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminPermission,
            )
        )
        if not self._send_to_serv(
            request, 'Не получилось подключиться к консоли'
        ):
            return 0
        try:
            self.ui.window.setCurrentIndex(1)
            sleep(0.5)
            self.update_b29()
            logger.info('Received teams list')
        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self, 'Error', f'Не получилось подключиться к консоли\n{err}'
            )
        return 0

    # BUTTON 4 - Add new team
    @anti_spam
    def button_add_team(self):
        text = self.ui.lineEdit.text()
        self.ui.lineEdit.setText('')
        if re.search(r'[^a-z A-Z0-9]', text):
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Используйте латинские буквы в названии команды',
            )
            return -1
        if text == '':
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Пустое имя для команды'
            )
            return -1
        request = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminButtonAddNewTeam,
                data=[text],
            )
        )
        self._send_to_serv(request, 'Не получилось отправить данные на сервер')
        return 0

    # BUTTON 3 - Back to main menu
    def button_3(self):
        self.ui.window.setCurrentIndex(0)

    # ONLY Updates list of teams
    def update_b29(self):
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.GetTeamsList,
            )
        )
        self._send_to_serv(data, 'Не получилось отправить данные на сервер')
        return 0

    # BUTTON 13 - Delete selected team
    @anti_spam
    def button_13(self):
        row = self.ui.listWidget.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Сначала выберите команду для удаления'
            )
            return -1
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminDeleteTeam,
                data=[row],
            )
        )
        self._send_to_serv(data, 'Не получилось удалить команду')
        return 0

    # BUTTON 5 - Change team capacity
    @anti_spam
    def button_5(self):
        text = self.ui.lineEdit_2.text()
        if re.search(r'[^0-9]', text):
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Вводится только целое число'
            )
            return -1
        if text == '':
            QtWidgets.QMessageBox.critical(self, 'Error', 'Пустой ввод')
            return -1
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminChangeTeamCapacity,
                data=[text],
            )
        )
        self._send_to_serv(data, 'Не получилось изменить вместимость команды')

    # BUTTON 6 - CHANGE TIMER
    @anti_spam
    def button_6(self):
        text = self.ui.lineEdit_3.text()
        if re.search(r'[^0-9]', text):
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Вводится только целое число'
            )
            return -1
        if text == '':
            QtWidgets.QMessageBox.critical(self, 'Error', 'Пустой ввод')
            return -1
        capacity = str(int(text) * 60)
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminChangeTimer,
                data=[capacity],
            )
        )
        self._send_to_serv(data, 'Не получилось изменить таймер')
        return 0

    # Простая функция, отображающая введенное админом время на таймере
    def init_timer(self):
        self.ui.timer_min.display(self.timer_min)
        self.ui.timer_sec.display(self.timer_sec)

    # Функция записи текущего номера задания
    @anti_spam
    def init_task(self):
        text = self.ui.lineEdit_4.text()
        if re.search(r'[^0-9]', text):
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'Вводится только целое число'
            )
            return -1
        if text == '':
            QtWidgets.QMessageBox.critical(self, 'Error', 'Пустой ввод')
            return -1

        # todo: hardcoded if statement
        if int(text) != 1:
            QtWidgets.QMessageBox.critical(
                self, 'Error', 'NotImplementedError. Only task 1 is available'
            )
            return -1
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminChangeCurrentTask,
                data=[text],
            )
        )
        self._send_to_serv(data, 'Не получилось изменить номер задания')
        return 0

    # Простая функция для обновления текущего номера задания на экране
    def change_current_task(self):
        self.ui.label_10.setText(str(self.current_task))
        return 0

    # Функция открытия PDF файла с задачами
    @anti_spam
    def open_tasks_pdf(self):
        os.startfile('Tasks.pdf')  # windows only
        return 0

    # ------------------------------------------------------------------------------------------------------------
    def team_spectating_1(self):
        teams_count = self.ui.listWidget.count()
        if teams_count == 0:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Нет команд')
        else:
            self.ui.window.setCurrentIndex(2)

    def back_to_edit_server(self):
        self.ui.window.setCurrentIndex(1)

    def team_spectating_2(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 2:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Всего 1 команда')
        else:
            self.ui.window.setCurrentIndex(3)

    def team_spectating_3(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 3:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Всего 2 команды')
        else:
            self.ui.window.setCurrentIndex(4)

    def team_spectating_4(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 4:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Всего 3 команды')
        else:
            self.ui.window.setCurrentIndex(5)

    def team_spectating_5(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 5:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Всего 4 команды')
        else:
            self.ui.window.setCurrentIndex(6)

    def team_spectating_6(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 6:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Всего 5 команд')
        else:
            self.ui.window.setCurrentIndex(7)

    # ------------------------------------------------------------------------------------------------------------

    def _started_timer(self):
        Thread(target=started_timer2, daemon=True, args=(self,)).start()

    @anti_spam
    def start_competition(self):
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.AdminStartCompetition,
            )
        )
        if not self._send_to_serv(data, 'Не получилось начать соревнование'):
            return -1
        self.stop_timer = 0
        self._started_timer()
        self.ui.label_12.setText('ONLINE')
        return 0

    @anti_spam
    def stop_competition(self):
        for i in range(1, 7):
            if i == 1:
                self.ui.tableWidget.setRowCount(0)
                continue
            else:
                tableWidget = eval(f'self.ui.tableWidget_{i}')
                tableWidget.setRowCount(0)
            label = eval(f'self.ui.label_{i+25}')
            label.setText('...')
        self.ui.label_12.setText('OFFLINE')
        data = pickle.dumps(
            RequestData(
                endpoint=ServerEndpoint.StopResetButton,
            )
        )
        self._send_to_serv(data, 'Не получилось остановить соревнование')


# Распределитель (работает в треде отдельно)
def distributor(data: ResponseData, application_object: MyWin):
    if data.key_code not in EndpointMapper:
        return 0
    EndpointMapper[data.key_code](data, application_object)
    return 0


# Функция работает как ТРЕД и чекает подключение к серверу каждые 5 секунд
def server_check(application_object: MyWin):
    request = pickle.dumps(RequestData(ServerEndpoint.Ping))
    sleep(2)
    while True:
        try:
            application_object.client.send(request)
        except OSError:
            if application_object.ui.window.currentIndex() != 0:
                application_object.ui.window.setCurrentIndex(0)
                application_object.connected = False
                application_object.client.close()
            return 0
        finally:
            logger.info('Server checked for ping')
            sleep(5)


# Функция работает как ТРЕД и принимает сообщения от сервера каждую секунду
def server_receive_msg(application_object: MyWin):
    while True:
        try:
            data = application_object.client.recv(4096)
            if data == b'':
                continue
            data_obj: ResponseData = pickle.loads(data)
            logger.info(f'Получен ответ от сервера: {data_obj}')
            distributor(data_obj, application_object)
        except OSError:
            pass
        except Exception as err:
            logger.info('error in server_receive_msg', err)


def time_delay(application_object: MyWin):
    while True:
        sleep(1)
        application_object.current_time = datetime.now()


def started_timer2(application_object: MyWin):
    seconds = application_object.timer_min * 60 + application_object.timer_sec
    while seconds > 0:
        if application_object.stop_timer == 1:
            application_object.stop_timer = 0
            return 0
        if application_object.timer_sec == 0:
            application_object.timer_min -= 1
            application_object.timer_sec = 59
        else:
            application_object.timer_sec -= 1
        application_object.init_timer()
        seconds -= 1
        sleep(1)


if __name__ == '__main__':
    ip, port = '127.0.0.1', 9669
    app = QtWidgets.QApplication(sys.argv)
    my_app = MyWin(ip, port)
    my_app.show()

    Thread(target=server_receive_msg, daemon=True, args=(my_app,)).start()
    Thread(target=time_delay, daemon=True, args=(my_app,)).start()

    sys.exit(app.exec_())
