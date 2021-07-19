#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
графический интерфейс для работы с sqlite3
"""

import os, sys, sqlite3
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo, showwarning


class MainWindow(Frame):
    def __init__(self, parent=None, *args):
        Frame.__init__(self, parent)
        self.pack()
        self.makeMenu()
        self.makeWidget()
        self.master.title('SQLITE3 GUI')
        self.master.geometry('+150+150')
        self.b_n = ''
        self.query = ''
        self.error = ''
        self.col = []
        
    def create_DB(self):
        name_DB = asksaveasfilename()
        name_DB = name_DB + '.sqlite'
        if not name_DB: return
        conn = sqlite3.connect(name_DB)
        conn.close()
        last_name = os.path.basename(name_DB)
        showinfo('Create', 'создана БД: ' + last_name)
        
    def open_DB(self):
        if not self.b_n:
            self.b_n = askopenfilename()
            self.bd = sqlite3.connect(self.b_n)
            self.base_name = os.path.basename(self.b_n)
            self.curs = self.bd.cursor()
        else:
            print('БД уже открыта')
            return
        self.make_topframe()

    def makeMenu(self):
        self.top = Menu(self)
        self.master.config(menu=self.top)
        self.file = Menu(self.top, tearoff=False)
        self.file.add_command(label='Create', command=lambda:self.create_DB())
        self.file.add_command(label='Open', command=lambda:self.open_DB())
        self.file.add_command(label='Save', command=lambda:self.save_DB())
        self.file.add_command(label='Close', command=lambda:self.onQuit())
        self.top.add_cascade(label='File', menu=self.file)
        self.db = Menu(self.top, tearoff=False)
        self.db.add_command(label='Show table', command=lambda:self.showTable())
        self.db.add_command(label='Close DB', command=lambda:self.close_DB())
        self.top.add_cascade(label='DB', menu=self.db)
        self.about = Menu(self.top, tearoff=False)
        self.about.add_command(label='About', command=lambda:self.aboutMe())
        self.top.add_cascade(label='About', menu=self.about)
        
    def makeWidget(self):
        self.top_f = Frame(self, bd=2, relief=RIDGE)
        self.top_f.pack(side=TOP, expand=YES, fill=BOTH)
        self.top_b = Frame(self, bd=2, relief=RIDGE)
        self.top_b.pack(side=TOP, expand=YES, fill=BOTH)
        Button(self, text='Quit', command=self.quit).pack(side=BOTTOM)
        text = 'Откройте или создайте базу данных\n Используйте меню File'
        Label(self.top_f, text=text, font='bold').pack(side=TOP)
        
    def make_topframe(self):
        self.clear_top()
        Label(self.top_f, text='Имя БД: '+self.base_name).pack(side=TOP)
        Label(self.top_f, text='Введите SQL запрос').pack(side=TOP)
        self.ent = Entry(self.top_f)
        self.ent.pack(side=TOP, expand=YES, fill=BOTH)
        Button(self.top_f, text='Выполнить', command=self.execute_query).pack(side=TOP)
        
    def make_bottomframe(self, data):
        self.clear_bottom()
        if not self.query:
            self.query = self.query_sh_t
        text = 'Ответ:' if not self.error else self.error
        Label(self.top_b, text='Запрос: '+ self.query).pack(side=TOP)
        Label(self.top_b, text=text).pack(side=TOP)
        sbar = Scrollbar(self.top_b)
        tx = Text(self.top_b)
        sbar.config(command=tx.yview)
        tx.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        tx.pack(side=LEFT, expand=YES, fill=BOTH)
        if self.col:
            col_name = ' | '.join(self.col)
            tx.insert('end', col_name+'\n')
        for label in data:
            tx.insert('end', str(label)+'\n')
        self.query = ''
        self.error = ''
        self.col = []
        
    def showTable(self):
        if self.b_n:
            self.query_sh_t = 'select name from sqlite_master where type="table"'
            table = self.curs.execute(self.query_sh_t)
            self.make_bottomframe(table)
        else:
            showwarning("Warning", "There isn't DB")
            return
        
    def close_DB(self):
        if self.b_n:
            self.bd.close()
            self.b_n = ''
        
    def execute_query(self):
        self.query = self.ent.get()
        if not self.query:
            showwarning('Предупреждение', 'Не введен запрос')
            return
        try:
            response = self.curs.execute(self.query).fetchall()
        except:
            response = sys.exc_info()[:2]
            self.error = 'ERROR'
        if not self.error: self.parse_query()
        self.make_bottomframe(response)
        self.ent.delete(0, END)
        
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
              
    def clear_top(self):
        for l in self.top_f.pack_slaves():
            l.destroy()
            
    def clear_bottom(self):
        for l in self.top_b.pack_slaves():
            l.destroy()
    

MainWindow().mainloop()



'''
list_ = Listbox(self.top_b)
        sbar.config(command=list_.yview)
        list_.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list_.pack(side=LEFT, expand=YES, fill=BOTH)
        pos = 0
        for label in data:
            print(label)
            list_.insert(pos, label)
            pos+=1
'''