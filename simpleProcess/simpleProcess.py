__author__ = 'lgu'

from tkinter import *
from tkinter import tix
from tkinter import messagebox
from tkinter.filedialog import *
import os

from utils import *

class AbstractComponent:
    def executeCmds(self, cmdLines):
        ExecuteCommandsThread(cmdLines, self).start()

    def start(self):
        print('Start')

    def finish(self):
        print('Finish')

class CommonVar:
    CONFIG_INI = 'config.ini'
    CONFIG_FILE = 'config/process.json'
    ICONBITMAP = 'icons/tank.ico'
    GEOMETRY = '1000x600'

import configparser
class ConfigFile:
    def getConfigFile(self):
        filename = self.getValue('configfile')

        if os.path.isfile(filename):
            return filename
        return CommonVar.CONFIG_FILE

    def saveConfigFile(self, file):
        ConfigFile.saveValue('configfile',file)

    @staticmethod
    def getValue(param):
        config = configparser.ConfigParser()
        config.read(CommonVar.CONFIG_INI)
        return config['DEFAULT'][param]

    @staticmethod
    def saveValue(param, var):
        config = configparser.ConfigParser()
        config.read(CommonVar.CONFIG_INI)
        config['DEFAULT'][param]=str(var)
        with open(CommonVar.CONFIG_INI, 'w') as configfile:
            config.write(configfile)

    def getColumns(self):
        return  ConfigFile.getValue('columns')

    def saveColumns(self, columns):
        ConfigFile.saveValue('columns',columns)

class ProcessComponent(AbstractComponent):
    def __init__(self,frame):

        p = PanedWindow(frame, orient=VERTICAL)
        p.pack(fill=BOTH, expand=1)
        top = PanedWindow(p)
        p.add(top)

        bottom = PanedWindow(p)
        p.add(bottom)

        self.outText = tix.ScrolledText(bottom)
        self.outText.pack(fill=BOTH, expand=1)

        scr_win = tix.ScrolledWindow(top)
        scr_win.pack(fill=BOTH, expand=True)
        self.frame = scr_win.window
        self.cf = ConfigFile().getConfigFile()
        self.createWidgets()

    def replaceJS(self, js):
        properties = []
        if os.path.exists(self.setting):
            file = open(self.setting,'rU')
            for line in file.readlines():
                p = line.split('=',1)
                if len(p) == 2:
                    p[0] = p[0].strip()
                    p[1] = p[1].strip()
                    p[0] = '%'+p[0]+'%'
                    properties.append(p)
            file.close()

        for item in js:
            for index,cmd in enumerate(item['cmds']):
                for p in properties:
                    cmd = cmd.replace(p[0],p[1])
                    item['cmds'][index] = cmd

    def createWidgets(self):
        self.loadFile(self.cf)
        js = self.js

        self.replaceJS(js)

        p = PanedWindow(self.frame, orient=VERTICAL)
        p.pack(fill=BOTH, expand=1)

        pt = PanedWindow(p)
        p.add(pt)

        run = Button(pt, text="Run Selected", command=self.callRun)
        run.pack(side =TOP)

        pb = PanedWindow(p)
        pb.pack(fill=BOTH, expand=1)
        p.add(pb)

        global col
        self.pane = p
        self.runButton = run
        self.vars = []
        self.singleButtons = []

        l_cmds = len(js)
        rows = int((l_cmds+col.get()-1)/col.get())

        pcs = []
        for c in range(0,col.get()):
            pc = PanedWindow(pb)
            pc.pack(fill=BOTH, expand=1)
            pcs.append(pc)
            pb.add(pc)

        for c in range(0,col.get()):
            pc = pcs[c]
            for r in range(0,rows):
                index = c*rows + r
                if index < l_cmds:
                    item = js[index]
                    print(str(index)+': '+item['model'])
                    v = StringVar()
                    v.set('0')
                    self.vars.append(v)

                    b = Checkbutton(pc, text=item['model'], variable = v , command = lambda : self.callCheck(),
                                    onvalue=item['model'], offvalue='0',borderwidth=10)
                    b.grid(row=r,column=0, sticky = W)

                    items = self.getSource(item['model'])
                    singleButton = self.SingleRunButton(pc ,r,items['cmds'],self.outText.text)
                    self.singleButtons.append(singleButton)

    def callCheck(self):
        text = self.outText.text
        text.delete(1.0, END)
        for v in self.vars:
            if v.get() != '0':
                item = self.getSource(v.get())
                if 'cmds' in item.keys():
                    for cmd in item['cmds']:
                        text.insert(END, cmd)
                        text.insert(END, '\n')

    class SingleRunButton:
        def __init__(self, p, index, cmds, text):
            self.b = Button(p,text="Run",command = lambda : self.callSingleRun(cmds, text))
            self.b.grid(row=index,column=1)

        def start(self):
            self.b['state'] = DISABLED

        def finish(self):
            self.b['state'] = NORMAL

        def callSingleRun(self,cmds,text):
            text.delete(1.0, END)
            for cmd in cmds:
                text.insert(END, cmd)
                text.insert(END, '\n')
            print(cmds)
            ProcessComponent.executeCmds(self, cmds)

    def getSource(self, model):
        for item in self.js:
            if model == item['model']:
                return item
        return NONE


    def callRun(self):
        cmdLines = []
        for v in self.vars:
            if v.get() != '0':
                item = self.getSource(v.get())
                if 'cmds' in item.keys():
                    cmdLines.extend(item['cmds'])
        self.executeCmds(cmdLines)

    def start(self):
        self.runButton['state'] = DISABLED
        for b in self.singleButtons:
            b.start()

    def finish(self):
        self.runButton['state'] = NORMAL
        for b in self.singleButtons:
            b.finish()

    def loadFile(self, file):
        self.setting = file.replace('.json','')
        print(self.setting)
        self.js = JsonUtil.getJson(file)
        ConfigFile().saveConfigFile(file)

    def callLoad(self, cf):
        self.cf = cf
        self.pane.destroy()
        self.createWidgets()

class EnvironmentComponent:
    def __init__(self, frame, component):
        self.frame = frame
        self.component = component
        self.createWidgets()

    def createWidgets(self):
        text = tix.ScrolledText(self.frame)
        text.pack(fill = BOTH, expand = TRUE)
        setting = self.component.setting

        if os.path.exists(setting):
            file = open(setting,'r+')
            for line in file.readlines():
                text.text.insert(END,line)
            file.close()
        self.text = text.text

        p = Frame(self.frame)
        p.pack(side=BOTTOM, expand=NO, fill=NONE)
        save = Button(p, text = 'Save', command = self.callSave)
        save.pack(side=LEFT)
        Cancel = Button(p, text = 'Cancel', command = self.callCancel)
        Cancel.pack(side=LEFT)
        pass

    def callSave(self):
        print(self.text.get(1.0,'end-1c'))
        f = open(self.component.setting, 'w')
        f.writelines(self.text.get(1.0,'end-1c'))
        f.close()
        self.frame.destroy()
        self.component.callLoad(self.component.cf)

    def callCancel(self):
        self.frame.destroy()

class MenuComponent:
    def __init__(self, frame):
        self.frame = frame
        self.cf = ConfigFile().getConfigFile()
        self.createWidgets()

    def createWidgets(self):
        menu = Menu(self.frame)

        fileMenu = Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Load Config File...", command=self.callLoad)
        fileMenu.add_command(label="Refresh", command=self.callReload)
        fileMenu.add_separator()
        fileMenu.add_command(label="Set Environment Variables", command=self.callSetting)

        viewMenu = Menu(menu)
        menu.add_cascade(label="View", menu=viewMenu)
        global col
        viewMenu.add_radiobutton(label="Show Column 1", variable=col, value=1, command=self.callSetColumns)
        viewMenu.add_radiobutton(label="Show Column 2", variable=col, value=2, command=self.callSetColumns)
        viewMenu.add_radiobutton(label="Show Column 3", variable=col, value=3, command=self.callSetColumns)

        helpMenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(label="About...", command=self.callAbout)

        self.frame.config(menu=menu)

    def setComponent(self, component):
        self.component = component

    def callLoad(self):
        name = askopenfilename(filetypes=[("Config Files","*.json"),('All Files','*')])
        if name:
            self.cf = name
            self.component.callLoad(self.cf)

    def callSetColumns(self):
        global col
        ConfigFile.saveColumns(self,col.get())
        self.component.callLoad(self.cf)

    def callReload(self):
        self.component.callLoad(self.cf)

    def callSetting(self):
        tl = Toplevel()
        EnvironmentComponent(tl, self.component)
        pass

    def callAbout(self):
        messagebox.showinfo('Simple Process','Supporting development tool!\nAuthor: lgu\nSkype: freedomgll\nDate: 2014/9/30\nVersion: 0.7')

master = tix.Tk()
master.wm_title("Simple Process")
master.wm_iconbitmap(CommonVar.ICONBITMAP)
master.geometry(CommonVar.GEOMETRY)

col = IntVar()
columns = ConfigFile().getColumns()
col.set(columns)

menu = MenuComponent(master)
process = ProcessComponent(master)
menu.setComponent(process)

mainloop()