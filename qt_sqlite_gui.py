#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
import sys,sqlite3, random, os, time

lang = {'ru':[('&Файл', 0), ('Закрыть', 1), ('БД', 2), ('Создать БД', 3), ('Открыть БД', 4),
              ('Коммит БД', 5), ('Закрыть БД', 6), ('О...', 7), ('О программе', 8), ('Обо мне', 9),
              ('Имя БД', 10), ('Введите имя БД', 11), ('Предупреждение', 12), ('Не задано имя БД', 13),
              ('Инфо', 14), ('Создана БД: ', 15), ("""<center>Откройте или создайте базу данных</center>\n
                <center>Используйте меню:</center>\n<center><b>"БД"</b></center>""", 16),
              ('БД уже открыта', 17), ('Вы действительно хотите закрыть текущую БД?', 18), ('Таблицы: ',19),
              ('Введите SQL запрос: ', 20), ('Выполнить', 21), ('Ответ:', 22), ('Запрос: ', 23),
              ('Ничего не найдено или синтксис запроса не поддерживается', 24), ('Не введен запрос',25),
              ('ОШИБКА', 26), ('В таблицу %s добавлены значения', 27), ('В таблицу %s внесены изменения', 28),
              ('Изменения внесены в ячейки: %s', 29), ('Где %s', 30), ('Все данные', 31),
              ('Из таблицы %s удалены строки', 32), ('Создано представление: %s', 33),
              ('Создана таблица: %s', 34), ('Таблица %s переименована в %s', 35),
              ('Создан индекс: %s,\n для таблицы: %s,\n для столбца(-ов): %s', 36),
              ('Столбец %s таблицы %s переименован в %s', 37), ('Удален индекс: %s', 38),
              ('В таблицу %s добавлен столбец %s', 39), ('Из таблицы %s удален столбец %s', 40),
              ('Удалена таблица: %s', 41), ('Удалено представление: %s', 42), ('Язык', 43),
              ('Русский', 44), ('Английский', 45)],
        'en':[('&File', 0), ('Close', 1), ('DB', 2), ('Create DB', 3), ('Open DB', 4),
              ('Commit DB', 5), ('Close DB', 6), ('About...', 7), ('About programm', 8), ('About me', 9),
              ('Name DB', 10), ('Enter name of DB', 11), ('Warning', 12), ('Name of DB not specified', 13),
              ('Info', 14), ('Created DB: ', 15), ("""<center>Open or create database</center>\n
                <center>Use menu:</center>\n<center><b>"DB"</b></center>""", 16),
              ('DB already open', 17), ('Do you really want to close current DB?', 18), ('Tables: ',19),
              ('Enter SQL query: ', 20), ('Execute', 21), ('Answer:', 22), ('Query: ', 23),
              ('Nothing found or syntax of query not supported', 24), ('Query not entered',25),
              ('ERROR', 26), ('Into table %s added values', 27), ('Table %s changed', 28),
              ('Cells changed: %s', 29), ('Where %s', 30), ('All data', 31),
              ('From table %s deleted rows', 32), ('Created view: %s', 33),
              ('Created table: %s', 34), ('Table %s renamed to %s', 35),
              ('Created index: %s,\n for table: %s,\n for column(-s): %s', 36),
              ('Column %s of table %s renamed to %s', 37), ('Deleted index: %s', 38),
              ('To table %s added column %s', 39), ('From table %s deleted column %s', 40), ('Deleted table: %s', 41),
              ('Deleted view: %s', 42), ('Language', 43), ('Russian', 44), ('English', 45)]
        }

settings = QtCore.QSettings('zmv', 'qt_sqlite')
if settings.contains('Language'):
   menu_l = settings.value('Language')
else:
   menu_l = 'en'
   settings.setValue('Language', menu_l)
#app_l = lang[menu_l]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.win = None
        self.wp = os.path.dirname(os.path.abspath(__file__))
        self.start = 0
        self.setLanguage(menu_l)
        self.greeting()
        self.menuBar = self.menuBar()
        self.makeMenu()
        self.b_n = ''
        
        
    def makeMenu(self):
        myMenu = self.menuBar.addMenu(self.app_l[0][0])
        action = myMenu.addAction('&'+self.app_l[1][0],  self.close)
        #action = myMenu.addAction('Test',  self.test)
        myDB = self.menuBar.addMenu(self.app_l[2][0])
        action = myDB.addAction('&'+self.app_l[3][0],  self.create_DB)
        action = myDB.addAction('&'+self.app_l[4][0], self.open_DB)
        action = myDB.addAction(self.app_l[5][0], self.commit_DB)
        action = myDB.addAction(self.app_l[6][0],  self.close_DB)
        menuLang = self.menuBar.addMenu(self.app_l[43][0])
        action = menuLang.addAction(self.app_l[44][0], lambda ln='ru': self.setLanguage(ln))
        action = menuLang.addAction(self.app_l[45][0], lambda ln='en': self.setLanguage(ln))
        myAbout = self.menuBar.addMenu(self.app_l[7][0])
        action = myAbout.addAction(self.app_l[8][0], self.aboutProgramm)
        action = myAbout.addAction(self.app_l[9][0], self.aboutMe)
        
    def setLanguage(self, ln):
        settings.setValue('Language', ln)
        self.app_l = lang[ln]
        if self.start > 0:
            self.main_update()
        self.start += 1
        
    def main_update(self):
        self.menuBar.clear()
        self.makeMenu()
        if self.b_n:
            self.win = MyWorkWindow(self.curs, self.base_name, self.app_l)
            self.win.btncl.clicked.connect(self.close)
            self.setCentralWidget(self.win)
        else:
            self.gr_lab.setText(self.app_l[16][0])
            
    
            
    def create_DB(self):
        s, ok = QtWidgets.QInputDialog.getText(None, self.app_l[10][0], self.app_l[11][0])
        if not ok: return
        if ok and not s:
            QtWidgets.QMessageBox.warning(None, self.app_l[12][0], self.app_l[13][0])
            return
        name_DB = s + '.sqlite'
        conn = sqlite3.connect(name_DB)
        conn.close()
        last_name = os.path.basename(name_DB)
        QtWidgets.QMessageBox.information(None,self.app_l[14][0], self.app_l[15][0] + last_name)
        
    def greeting(self):
        text_ch = self.app_l[16][0]
        self.gr_lab = QtWidgets.QLabel(text_ch)
        self.setCentralWidget(self.gr_lab) 
        
        
        
    def open_DB(self):
        if not self.b_n:
            self.b_n, fil_ = QtWidgets.QFileDialog.getOpenFileName(None, caption=self.app_l[4][0],
                                                                         directory=self.wp, filter='DB (*.sqlite)') 
            self.bd = sqlite3.connect(self.b_n)
            self.base_name = os.path.basename(self.b_n)
            self.curs = self.bd.cursor()
            self.win = MyWorkWindow(self.curs, self.base_name, self.app_l)
            self.win.btncl.clicked.connect(self.close)
            self.setCentralWidget(self.win)
        else:
            QtWidgets.QMessageBox.warning(None, self.app_l[12][0], self.app_l[17][0])
            return
        
    def commit_DB(self):
        self.bd.commit()
        
    def close_DB(self):
        result = QtWidgets.QMessageBox.question(None, self.app_l[12][0],
                    self.app_l[18][0],
                    buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    defaultButton=QtWidgets.QMessageBox.No)
        if result == 16384:
            self.bd.close()
            self.b_n = ''
            self.greeting()
        
    def aboutProgramm(self):
        pass
    
    def aboutMe(self):
        pass
        
    def closeEvent(self, e):
        if not self.win: return
        e.accept()
        QtWidgets.QWidget.closeEvent(self, e)
        
#########################################################################################################
class MyWorkWindow(QtWidgets.QWidget):
    def __init__(self,curs, base_name, app_l, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.app_l = app_l
        self.curs = curs
        self.base_name = base_name
        self.query = ''
        self.error = ''
        self.col = []
        self.rl_flag = 1
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
        self.btncl = QtWidgets.QPushButton(self.app_l[1][0])
        self.infobox.addWidget(self.btncl)
        self.setLayout(self.box)
        self.make_basebox()
        self.make_topbox()
        
    def make_basebox(self):
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
        rootitem1 = QtGui.QStandardItem(self.app_l[19][0])
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
        sti.setHorizontalHeaderLabels([self.app_l[10][0] + ': ' + self.base_name])
        tv.setModel(sti)
        self.basebox.addWidget(tv)
        
    def resizeEvent(self, e):
        self.leftframe.setFixedWidth(0.25*e.size().width())
        QtWidgets.QWidget.resizeEvent(self, e)
        
        
    def make_topbox(self):
        self.clear_vtop()
        self.vtop.addWidget(QtWidgets.QLabel(self.app_l[20][0]), alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.ent = QtWidgets.QLineEdit()
        self.vtop.addWidget(self.ent, alignment=QtCore.Qt.AlignTop)
        btn = QtWidgets.QPushButton(self.app_l[21][0])
        btn.clicked.connect(self.execute_query)
        self.vtop.addWidget(btn)
        
    def make_bottombox_list(self):
        self.clear_vbottom()
        text = self.app_l[22][0] if not self.error else self.error
        self.vbottom.addWidget(QtWidgets.QLabel(self.app_l[23][0] + self.query))
        self.vbottom.addWidget(QtWidgets.QLabel(text))
        if not self.response:
            self.response = [self.app_l[24][0]]
        self.lv = QtWidgets.QListView()
        slm = QtCore.QStringListModel(self.response)
        self.lv.setModel(slm)
        self.vbottom.addWidget(self.lv)
        self.query = ''
        self.error = ''
        self.col = []
        self.rl_flag = 1
        
    def make_bottombox(self):
        if not self.response or self.rl_flag:
            self.make_bottombox_list()
            return
        self.clear_vbottom()
        self.vbottom.addWidget(QtWidgets.QLabel(self.app_l[23][0]+ self.query))
        self.vbottom.addWidget(QtWidgets.QLabel(self.app_l[22][0]))
        self.tb = QtWidgets.QTableView()
        sti = QtGui.QStandardItemModel()
        for row in self.response:
            row_list = []
            for it in row:
                row_list.append(QtGui.QStandardItem(str(it)))
            sti.appendRow(row_list)
        sti.setHorizontalHeaderLabels(self.col)
        self.tb.setModel(sti)
        self.vbottom.addWidget(self.tb)
        self.query = ''
        self.error = ''
        self.col = []
        self.rl_flag = 1
        
        
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
            
    def clear_basebox(self):
        for i in reversed(range(self.basebox.count())):
            wt = self.basebox.itemAt(i).widget()
            wt.setParent(None)
            wt.deleteLater()        
    
            
    def showTable(self):
        self.table_info = {}
        self.query_sh_t = 'select name from sqlite_master where type="table"'
        tables = self.curs.execute(self.query_sh_t).fetchall()
        self.response_ = [i[0] for i in tables]
        for j in self.response_:
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
        
            
    def execute_query(self):
        self.query = self.ent.text()
        if not self.query:
            QtWidgets.QMessageBox.warning(None, self.app_l[12][0], self.app_l[25][0])
            return
        try:
            self.response = self.curs.execute(self.query).fetchall()
        except:
            self.response = sys.exc_info()[:2]
            self.response = [str(i) for i in self.response]
            self.error = self.app_l[26][0]
        if not self.error: self.parse_query()
        self.make_bottombox()
        self.ent.setText('')
    
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
            self.rl_flag = 0
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
            self.response.append(self.app_l[27][0] % tab)
        elif low.startswith('update'):
            st = low.find('set')
            en = low.find('where')
            tab = self.query[7:st].strip()
            self.response.append(self.app_l[28][0] % tab)
            cells = self.query[st+3:en].split(',')
            cell_list = []
            for i in cells:
                eq = i.find('=')
                i = i[:eq]
                cell_list.append(i)
            cells = ','.join(cell_list)
            self.response.append(self.app_l[29][0] % cells)
            if 'where' in low:
                target = self.query[en+5:]
                self.response.append(self.app_l[30][0] % target)
        elif low.startswith('delete'):
            en = low.find('where')
            tab = self.query[:en].strip().split()[-1]
            self.response.append(self.app_l[32][0] % tab)
            if 'where' in low:
                target = self.query[en+5:]
                self.response.append(self.app_l[30][0] % target)
            else:
                self.response.append(self.app_l[31][0])
        elif low.startswith('create'):
            parse_part = self.query[6:]
            comp_item = parse_part.lower().strip().split()[0]
            target = parse_part.strip().split()[1]
            if comp_item == 'view':
                self.response.append(self.app_l[33][0] % target)
            elif comp_item == 'table':
                self.clear_basebox()
                self.make_basebox()
                self.response.append(self.app_l[34][0] % target)
            elif comp_item == 'index':
                tt = parse_part.strip().split()[3]
                tc = parse_part.strip().split()[4]
                self.response.append(self.app_l[36][0] % (target, tt, tc))
        elif low.startswith('alter table'):
            parse_list = self.query[11:].strip().split()
            target = parse_list[0]
            if ' '.join(parse_list[1:3]).startswith('rename to'):
                self.response.append(self.app_l[35][0] % (target, parse_list[-1]))
            elif ' '.join(parse_list[1:3]).startswith('rename column'):
                self.response.append(self.app_l[37][0] % (parse_list[3], target, parse_list[-1]))
            elif ' '.join(parse_list[1:3]).startswith('add column'):
                self.response.append(self.app_l[39][0] % (target, parse_list[-2]))
            elif ' '.join(parse_list[1:3]).startswith('drop column'):
                self.response.append(self.app_l[40][0] % (target, parse_list[-1]))
            self.clear_basebox()
            self.make_basebox()
        elif low.startswith('drop'):
            parse_part = self.query[4:]
            comp_item = parse_part.lower().strip().split()[0]
            target = parse_part.strip().split()[1]
            if comp_item == 'view':
                self.response.append(self.app_l[42][0] % target)
            elif comp_item == 'table':
                self.clear_basebox()
                self.make_basebox()
                self.response.append(self.app_l[41][0] % target)
            elif comp_item == 'index':
                self.response.append(self.app_l[38][0] % target)
    
            
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('SQLITE3 GUI')
    desktop = QtWidgets.QApplication.desktop()
    # x = (desktop.width() // 2) - window.width() 
    # window.move(x, 250)
    window.resize(desktop.width()*0.3, desktop.height()*0.25)
    window.show()
    sys.exit(app.exec_())
        