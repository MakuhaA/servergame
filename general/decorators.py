from functools import wraps
from PyQt5 import QtWidgets
from datetime import timedelta


def anti_spam(func):
    @wraps(func)
    def wrapper(win_obj, *args, **kwargs):
        if win_obj.current_time - win_obj.last_time <= timedelta(seconds=1):
            QtWidgets.QMessageBox.critical(
                win_obj, 'Error', 'Интервал нажатия на кнопку слишком быстрый'
            )
            return -1
        else:
            win_obj.last_time = win_obj.current_time
        return func(win_obj)

    return wrapper
