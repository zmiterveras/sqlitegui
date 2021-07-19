#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
import sys,sqlite3, random, os, time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.win = None
        self.wp = os.path.dirname(os.path.abspath(__file__))
        text_ch = """<center>Откройте или создайте базу данных</center>\n
        <center>Используйте меню:</center>\n
        <center><b>"Файл"</b></center>"""
        self.greeting = QtWidgets.QLabel(text_ch)
        self.setCentralWidget(self.greeting)     
        menuBar = self.menuBar()
        myMenu = menuBar.addMenu('&Файл')
        action = myMenu.addAction('&Создать',  self.create_DB)
        action = myMenu.addAction('&Открыть', lambda: self.open_DB(myMenu))
        #action = myMenu.addAction('Test',  self.test)
        myDB = menuBar.addMenu('БД')
        action = myDB.addAction('Show table',  self.showT)
        action = myDB.addAction('Commit', self.commit_DB)
        action = myDB.addAction('Close DB',  self.close_DB)
        myAbout = menuBar.addMenu('О...')
        action = myAbout.addAction('О программе', self.aboutProgramm)
        action = myAbout.addAction('Обо мне', self.aboutMe)
        self.b_n = ''
        
    def create_DB(self):
        s, ok = QtWidgets.QInputDialog.getText(None, 'Имя БД', 'Введите имя БД')
        if not ok: return
        if ok and not s:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Не задано имя БД')
            return
        name_DB = s + '.sqlite'
        conn = sqlite3.connect(name_DB)
        conn.close()
        last_name = os.path.basename(name_DB)
        QtWidgets.QMessageBox.information(None,'Инфо', 'Создана БД: ' + last_name)
        
    def open_DB(self, myMenu):
        if not self.b_n:
            self.b_n, fil_ = QtWidgets.QFileDialog.getOpenFileName(None, caption='Открыть БД',
                                                                         directory=self.wp, filter='DB (*.sqlite)') 
            self.bd = sqlite3.connect(self.b_n)
            self.base_name = os.path.basename(self.b_n)
            self.curs = self.bd.cursor()
            self.win = MyWorkWindow(self.curs, self.base_name)
            action = myMenu.addAction('Сохранить',  self.win.save_DB)
            action = myMenu.addAction('&Закрыть',  self.close)
            self.win.btncl.clicked.connect(self.close)
            self.setCentralWidget(self.win)
        else:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'БД уже открыта')
            return
        
    def showT(self):
        if not self.win:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Отсутствует БД')
            return
        else:
            self.win.showTable()
        
    def commit_DB(self):
        self.bd.commit()
        
    def close_DB(self):
        result = QtWidgets.QMessageBox.question(None, 'Предупреждение',
                    'Вы действительно хотите закрыть текущую БД?\n',
                    buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    defaultButton=QtWidgets.QMessageBox.No)
        if result == 16384:
            self.bd.close()
            self.setCentralWidget(self.greeting)
        
    def aboutProgramm(self):
        pass
    
    def aboutMe(self):
        pass
        
    def closeEvent(self, e):
        if not self.win: return
        e.accept()
        QtWidgets.QWidget.closeEvent(self, e)
        

class MyWorkWindow(QtWidgets.QWidget):
    def __init__(self,curs, base_name, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.curs = curs
        self.base_name = base_name
        self.query = ''
        self.error = ''
        self.col = []
        self.query_sh_t = ''
        self.makeWidget()
        
    def makeWidget(self):
        self.box = QtWidgets.QVBoxLayout()
        self.vtop = QtWidgets.QVBoxLayout()
        self.vbottom = QtWidgets.QVBoxLayout()
        self.infobox =  QtWidgets.QHBoxLayout()
        self.box.addLayout(self.vtop)
        self.box.addLayout(self.vbottom)
        self.btncl = QtWidgets.QPushButton('Выход')
        self.infobox.addWidget(self.btncl)
        self.box.addLayout(self.infobox)
        self.setLayout(self.box)
        self.make_topframe()
        
    def make_topframe(self):
        self.clear_vtop()
        self.vtop.addWidget(QtWidgets.QLabel('Имя БД: '+self.base_name))
        self.vtop.addWidget(QtWidgets.QLabel('Введите SQL запрос: '))
        self.ent = QtWidgets.QLineEdit()
        self.vtop.addWidget(self.ent)
        btn = QtWidgets.QPushButton('Выполнить')
        btn.clicked.connect(self.execute_query)
        self.vtop.addWidget(btn)
        
    def make_bottomframe(self, response):
        self.clear_vbottom()
        if not self.query:
            self.query = self.query_sh_t
        text = 'Ответ:' if not self.error else self.error
        self.vbottom.addWidget(QtWidgets.QLabel('Запрос: '+ self.query))
        self.vbottom.addWidget(QtWidgets.QLabel(text))
        if self.col:
            col_name = ' | '.join(self.col)
            response.insert(0, col_name)
        self.lv = QtWidgets.QListView()
        slm = QtCore.QStringListModel(response)
        self.lv.setModel(slm)
        self.vbottom.addWidget(self.lv)
        self.query = ''
        self.error = ''
        self.col = []
        
        
    def clear_vtop(self):
        for i in reversed(range(self.vtop.count())):
            wt = self.vtop.itemAt(i).widget()
            wt.setParent(None)
            wt.deleteLater()
            
    def clear_vbottom(self):
        for i in reversed(range(self.vbottom.count())):
            wb = self.vbottom.itemAt(i).widget()
            wb.setParent(None)
            wb.deleteLater()
            
    def showTable(self):
        if self.base_name:
            self.query_sh_t = 'select name from sqlite_master where type="table"'
            tables = self.curs.execute(self.query_sh_t).fetchall()
            tables = [str(i) for i in tables] 
            self.make_bottomframe(tables)
        else:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Отсутствует БД')
            
    def execute_query(self):
        self.query = self.ent.text()
        if not self.query:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Не введен запрос')
            return
        try:
            response = self.curs.execute(self.query).fetchall()
            response = [str(i) for i in response]         
        except:
            response = sys.exc_info()[:2]
            response = [str(i) for i in response]
            self.error = 'ERROR'
        if not self.error: self.parse_query()
        self.make_bottomframe(response)
        self.ent.setText('')
        
    def parse_query(self):
        low = self.query.lower()
        if low.startswith('select'):
            st = self.query.find('from')
            if '*' in self.query:
                tab_n = self.query[st:].split()[1]
                col_cur = self.curs.execute('pragma table_info('+tab_n+')')
                for i in col_cur:
                    self.col.append(i[1])
            else:    
                st = self.query.find('from')
                self.col = self.query[6:st].split(',')
            
    def save_DB(self):
        pass
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('SQLITE3 GUI')
    # window.resize(350,200)
    # desktop = QtWidgets.QApplication.desktop()
    # x = (desktop.width() // 2) - window.width() 
    # window.move(x, 250)
    window.show()
    sys.exit(app.exec_())
        