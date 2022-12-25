from logging import INFO, Formatter, StreamHandler, getLogger

from PyQt5 import QtWidgets


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(
    Formatter('%(asctime)s - (%(name)s) - [%(levelname)s] - %(message)s')
)


def ponger(data, application_object):
    return 1


def get_teams_list(data, my_app):
    logger.info('Ready to update list')
    listed = data.data
    my_app.ui.listWidget.clear()
    dict_teams = {
        0: my_app.ui.label_15,
        1: my_app.ui.label_16,
        2: my_app.ui.label_18,
        3: my_app.ui.label_20,
        4: my_app.ui.label_22,
        5: my_app.ui.label_24,
    }
    for i, names in enumerate(listed):
        my_app.ui.listWidget.addItem(names)
        dict_teams[i].setText(names)
    return 1


def add_new_team(data, my_app):
    if data.data is False:
        logger.info('No more space to add new team')
        return -1
    logger.info('Team added')
    return 1


def change_timer(data, my_app):
    timer = int(data.data)
    my_app.timer_min = timer // 60
    my_app.timer_sec = timer - my_app.timer_min * 60
    my_app.init_timer()
    return 1


def change_current_task(data, my_app):
    my_app.current_task = int(data.data)
    my_app.change_current_task()
    return 1


def result_final(data, my_app):
    listed = data.data
    logger.info(f'Get final results: {listed}')
    # curr turn | name | stroke index | text | team number

    dict_tableWidgets = {
        '1': my_app.ui.tableWidget,
        '2': my_app.ui.tableWidget_2,
        '3': my_app.ui.tableWidget_3,
        '4': my_app.ui.tableWidget_4,
        '5': my_app.ui.tableWidget_5,
        '6': my_app.ui.tableWidget_6,
    }

    dict_tableWidgets[listed[4]].insertRow(int(listed[0]))
    dict_tableWidgets[listed[4]].setItem(
        int(listed[0]),
        0,
        QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)),
    )
    dict_tableWidgets[listed[4]].setItem(
        int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1])
    )
    times = f'{my_app.timer_min}:{my_app.timer_sec}'
    dict_tableWidgets[listed[4]].setItem(
        int(listed[0]), 2, QtWidgets.QTableWidgetItem(times)
    )
    dict_tableWidgets[listed[4]].setItem(
        int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2])
    )
    dict_tableWidgets[listed[4]].setItem(
        int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3])
    )
    return 1


def pushed_button_3(data, my_app):
    listed = data.data
    dict_labels = {
        '1': my_app.ui.label_26,
        '2': my_app.ui.label_27,
        '3': my_app.ui.label_28,
        '4': my_app.ui.label_29,
        '5': my_app.ui.label_30,
        '6': my_app.ui.label_31,
    }
    dict_labels[listed[2]].setText(f'Тестов: {listed[0]} из {listed[1]}')
    return 1


def stop_reset(data, my_app):
    my_app.stop_timer = 1
    return 1
