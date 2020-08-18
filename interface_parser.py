def_directory = "d:\\Преподавание\\_Бюрократия\\Планы\\2019-2020_2сем\\"
# def_directory = "d:\\Programs\\rating_parser\\"
def_id_point = "1"

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import sys
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Рейтинг")
web = QtWebEngineWidgets.QWebEngineView()

btn = QtWidgets.QPushButton("Заполнить")
vbox = QtWidgets.QVBoxLayout()
vbox.addWidget(web)
vbox.addWidget(btn)
window.setLayout(vbox)



def on_get_html(data):
    number, ok = QtWidgets.QInputDialog.getText(window, "Рейтинг", "Номер контрольной точки (от 1 до 8)", QtWidgets.QLineEdit.Normal, def_id_point)
    try:
        number = int(number)
        if 1 <= number <= 8:
            FileName = QtWidgets.QFileDialog.getOpenFileName(window, "БД", directory=def_directory, filter="db (*.db)")
            if FileName:
                FileName = FileName[0]
                from parserHTML import parseHTML
                parseHTML(data, web, FileName, number)
    except ValueError:
        print("Error of number")

def btnFill():
    page = web.page()
    page.toHtml(on_get_html)
btn.clicked.connect(btnFill)


def on_load_finished():
    print("Url loaded: " + web.url().toString())
web.loadFinished.connect(on_load_finished)


web.load(QtCore.QUrl("http://studentrating.dvgups.ru"))
# file_html = open("example.html", encoding="utf-8")
# web.setHtml(file_html.read())




sys.__excepthook__ = sys.excepthook
def my_exception_hook(exctype, value, tb):
    sys.__excepthook__(exctype, value, tb)
sys.excepthook = my_exception_hook

window.show()
sys.exit(app.exec_())




