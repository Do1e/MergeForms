# -*- encoding: utf-8 -*-
import tkinter
import tkinter.messagebox
import time
import json
from form import Form

class UI(object):
    def __init__(self):
        try:
            with open('config.json', 'r', encoding='gbk') as f:
                config = json.load(f)
        except:
            config = {}
        if 'from' not in config:
            config['from'] = ''
        if 'to' not in config:
            config['to'] = ''
        if 'fromsheet' not in config:
            config['fromsheet'] = 0
        if 'tosheet' not in config:
            config['tosheet'] = 0
        if 'baserow' not in config:
            config['baserow'] = ''
        if 'updatecol' not in config:
            config['updatecol'] = ''
        if 'savename' not in config:
            config['savename'] = 'result.xlsx'

        self.root = tkinter.Tk()
        self.root.title('MergeForms')
        self.root.resizable(0, 0)
        self.fromTitle = tkinter.Label(self.root, text='the file path of the form to be updated from:')
        self.fromTitle.grid(row=0, column=0, sticky=tkinter.W)
        self.fromInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['from']))
        self.fromInputBox.grid(row=1, column=0)

        self.toTitle = tkinter.Label(self.root, text='the file path of the form to be updated:')
        self.toTitle.grid(row=0, column=1, sticky=tkinter.W)
        self.toInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['to']))
        self.toInputBox.grid(row=1, column=1)

        self.sheetnameFromTitle = tkinter.Label(self.root, text='the sheet name of the form to be updated from:')
        self.sheetnameFromTitle.grid(row=2, column=0, sticky=tkinter.W)
        self.sheetnameFromInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['fromsheet']))
        self.sheetnameFromInputBox.grid(row=3, column=0)

        self.sheetnameToTitle = tkinter.Label(self.root, text='the sheet name of the form to be updated:')
        self.sheetnameToTitle.grid(row=2, column=1, sticky=tkinter.W)
        self.sheetnameToInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['tosheet']))
        self.sheetnameToInputBox.grid(row=3, column=1)

        self.baseTitle = tkinter.Label(self.root, text='find based on which column:')
        self.baseTitle.grid(row=4, column=0, sticky=tkinter.W)
        self.baseInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['baserow']))
        self.baseInputBox.grid(row=5, column=0)

        self.updateColTitle = tkinter.Label(self.root, text='the column to be updated:')
        self.updateColTitle.grid(row=4, column=1, sticky=tkinter.W)
        self.updateColInputBox = tkinter.Entry(width=50, textvariable=tkinter.StringVar(value=config['updatecol']))
        self.updateColInputBox.grid(row=5, column=1)

        self.saveTitle = tkinter.Label(self.root, text='the file path to save the result:')
        self.saveTitle.grid(row=6, column=0, columnspan=2, sticky=tkinter.W)
        self.saveInputBox = tkinter.Entry(width=100, textvariable=tkinter.StringVar(value=config['savename']))
        self.saveInputBox.grid(row=7, column=0, columnspan=2)

        self.mergeButton = tkinter.Button(self.root, text='Merge', command=self.merge)
        self.mergeButton.grid(row=8, column=0, columnspan=2)

        self.root.mainloop()

    def merge(self):
        try:
            fromPath = self.fromInputBox.get()
            toPath = self.toInputBox.get()
            if fromPath == '' or toPath == '':
                raise Exception('the file path of the form is empty')

            base_col = self.baseInputBox.get()
            if base_col == '':
                raise Exception('find based on which column is empty')

            fromSheetName = self.sheetnameFromInputBox.get()
            toSheetName = self.sheetnameToInputBox.get()
            if fromSheetName == '':
                fromSheetName = 0
            if toSheetName == '':
                toSheetName = 0
            fromForm = Form(fromPath, base_col=base_col, sheet_name=fromSheetName)
            toForm = Form(toPath, base_col=base_col, sheet_name=toSheetName)
            count = toForm.merge_from(fromForm, self.updateColInputBox.get())
            toForm.save(self.saveInputBox.get())
            tkinter.messagebox.showinfo('MergeForms', 'Merge successfully, {} rows updated.'.format(count))
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
                f.write(str(e) + '\n\n')
            tkinter.messagebox.showerror('MergeForms', 'Merge failed, please check error.log for details.')

if __name__ == '__main__':
    try:
        ui = UI()
    except Exception as e:
        with open('error.log', 'a') as f:
            f.write(str(e) + '\n')
        tkinter.messagebox.showerror('MergeForms', 'Merge failed, please check error.log for details.')
        time.sleep(5)
        exit(-1)