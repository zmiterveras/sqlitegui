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
        self.w = self.size().width()
        self.makeWidget()
        
    def makeWidget(self):
        self.box = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.infobox =  QtWidgets.QHBoxLayout()
        self.box.addLayout(self.hbox)
        self.box.addLayout(self.infobox)
        self.leftframe = QtWidgets.QFrame()
        self.leftframe.setFixedWidth(0.25*self.w)
        self.leftframe.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
        self.rightframe = QtWidgets.QFrame()
        self.rightframe.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
        self.querybox = QtWidgets.QVBoxLayout()
        self.basebox = QtWidgets.QVBoxLayout()
        self.vtop = QtWidgets.QVBoxLayout()
        self.vbottom = QtWidgets.QVBoxLayout()
        #####
        self.hbox.addWidget(self.leftframe)
        self.hbox.addWidget(self.rightframe)
        self.leftframe.setLayout(self.basebox)
        self.rightframe.setLayout(self.querybox)
        ####
        self.querybox.addLayout(self.vtop)
        self.querybox.addLayout(self.vbottom)
        self.btncl = QtWidgets.QPushButton('Выход')
        self.infobox.addWidget(self.btncl)
        self.setLayout(self.box)
        self.make_baseframe()
        self.make_topframe()
        
    def make_baseframe(self):
        def rootit_new(dic, rootitem, lr):
            if type(dic) == dict:
                sequence = dic.keys()
            else:
                sequence = dic
            for name in sequence:
                item1 = QtGui.QStandardItem(name)
                lr.append(item1)
                rootitem.appendRow([item1])
                
        self.showTable()
        tv = QtWidgets.QTreeView()
        sti = QtGui.QStandardItemModel()
        rootitem1 = QtGui.QStandardItem('Таблицы: ')
        rootitem2 = []
        rootitem3=[]
        rootit_new(self.table_info, rootitem1, rootitem2)
        tables_rootitem = [] 
        key_list = list(self.table_info.keys())
        for i in range(self.len_tabels):
            rootit_new(self.table_info[key_list[i]], rootitem2[i], tables_rootitem)
        p = 0
        for nt in self.table_info.keys():
            for tn in self.table_info[nt].keys():
                rootit_new(self.table_info[nt][tn], tables_rootitem[p], rootitem3)
                p += 1
        sti.appendRow([rootitem1])
        sti.setHorizontalHeaderLabels(['Имя БД: ' + self.base_name])
        tv.setModel(sti)
        self.basebox.addWidget(tv)
        
    def resizeEvent(self, e):
        self.leftframe.setFixedWidth(0.25*e.size().width())
        QtWidgets.QWidget.resizeEvent(self, e)
        
        
    def make_topframe(self):
        self.clear_vtop()
        self.vtop.addWidget(QtWidgets.QLabel('Введите SQL запрос: '), alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.ent = QtWidgets.QLineEdit()
        self.vtop.addWidget(self.ent) #, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        btn = QtWidgets.QPushButton('Выполнить')
        btn.clicked.connect(self.execute_query)
        self.vtop.addWidget(btn)
        
    def make_bottomframe(self):
        self.clear_vbottom()
        if not self.query:
            self.query = self.query_sh_t
        text = 'Ответ:' if not self.error else self.error
        self.vbottom.addWidget(QtWidgets.QLabel('Запрос: '+ self.query))
        self.vbottom.addWidget(QtWidgets.QLabel(text))
        if not self.response:
            self.response = ['Ничего не найдено или синтксис запроса не поддерживается']
        else:
            if self.col:
                col_name = ' | '.join(self.col)
                self.response.insert(0, col_name)
                self.response.insert(1, '*' * len(col_name))
        self.lv = QtWidgets.QListView()
        slm = QtCore.QStringListModel(self.response)
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
            self.table_info = {}
            self.query_sh_t = 'select name from sqlite_master where type="table"'
            tables = self.curs.execute(self.query_sh_t).fetchall()
            self.response = [i[0] for i in tables]
            #self.make_bottomframe()
            for j in self.response:
                self.table_info[j] = {}
                query_table_info = self.curs.execute('pragma table_info('+ j +')').fetchall()
                for col in query_table_info:
                    col_name = col[1]
                    col_type = 'Type: ' + col[2]
                    if col[3] == 1:
                        col_null = 'NULL: Yes'
                    else:
                        col_null = 'NULL: No'
                    col_default = 'default: ' + str(col[4])
                    if col[5] == 0:
                        col_pk = 'PK: No'
                    else:
                        col_pk = 'PK: Yes'
                    self.table_info[j][col_name] = [col_type, col_null, col_default, col_pk]      
            self.len_tabels = len(self.table_info)
            self.len_cols = sum([len(self.table_info[key]) for key in self.table_info])
            len_list = self.len_tabels + self.len_cols
        else:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Отсутствует БД')
            
    def execute_query(self):
        self.query = self.ent.text()
        if not self.query:
            QtWidgets.QMessageBox.warning(None, 'Предупреждение', 'Не введен запрос')
            return
        try:
            self.response = self.curs.execute(self.query).fetchall()
            #response = [str(i) for i in response]
            self.response = [' | '.join([str(k) for k in i]) for i in self.response]
        except:
            self.response = sys.exc_info()[:2]
            self.response = [str(i) for i in self.response]
            
            self.error = 'ERROR'
        if not self.error: self.parse_query()
        self.make_bottomframe()
        self.ent.setText('')
    
    def save_DB(self):
        pass
            
    def parse_query(self):
        def within_parse(colon):
            check_list = ['*', '/', '-', '+', '|']
            answ = False
            res_check = False
            for j in check_list:
                    if j in colon:
                        answ = True
                        res_check = True
                        break
            if 'as' in colon.split(' '):
                        name = colon.split(' ')[-1]
                        self.col.append(name)
                        answ = True
            else:
                if res_check:
                    self.col.append('time_col')
            return answ
        
        def parse_subquery(q_str):
                st = q_str.find('from')
                if q_str[:st].count('select'):
                        return (st + 4) + parse_subquery(q_str[st+4:])
                else:
                        return st + 4
            
        low = self.query.lower()
        if low.startswith('select'):
            st = low.find('from')
            parse_part = self.query[6:st]
            if parse_part.lower().count('select'):
                stn = parse_subquery(low[st+4:].strip())
                parse_part = self.query[6:stn+st].strip()
            parse_list = parse_part.strip().split(',')
            if '*' == parse_list[0].strip():
                tab_n = self.query[st:].split()[1]
                col_cur = self.curs.execute('pragma table_info('+tab_n+')')
                for i in col_cur:
                    self.col.append(i[1])
                return
            for colon in parse_list:
                if not within_parse(colon):
                    self.col.append(colon)
        elif low.startswith('insert'):
            st = low.find('into')
            tab = self.query[st+4:].strip().split()[0]
            self.response.append('В таблицу %s добавлены значения' % tab)
        elif low.startswith('update'):
            st = low.find('set')
            en = low.find('where')
            tab = self.query[7:st].strip()
            self.response.append('В таблицу %s внесены изменения' % tab)
            cells = self.query[st+3:en].split(',')
            cell_list = []
            for i in cells:
                eq = i.find('=')
                i = i[:eq]
                cell_list.append(i)
            cells = ','.join(cell_list)
            self.response.append('Изменения внесены в ячейки: %s' % cells)
            if 'where' in low:
                target = self.query[en+5:]
                self.response.append('Где %s' % target)
        elif low.startswith('delete'):
            en = low.find('where')
            tab = self.query[:en].strip().split()[-1]
            self.response.append('Из таблицы %s удалены строки' % tab)
            if 'where' in low:
                target = self.query[en+5:]
                self.response.append('Где %s' % target)
            else:
                self.response.append('Все данные')
        elif low.startswith('create'):
            parse_part = self.query[6:]
            comp_item = parse_part.lower().strip().split()[0]
            target = parse_part.strip().split()[1]
            if comp_item == 'view':
                self.response.append('Создано представление: %s' % target)
            elif comp_item == 'table':
                self.response.append('Создана таблица: %s' % target)
                
                
                
                
        
        
        
        
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('SQLITE3 GUI')
    window.resize(350,200)
    # desktop = QtWidgets.QApplication.desktop()
    # x = (desktop.width() // 2) - window.width() 
    # window.move(x, 250)
    window.show()
    sys.exit(app.exec_())
        