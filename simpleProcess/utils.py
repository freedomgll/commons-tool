#Date 2014/5/5
__version__ = '0.1'
__author__ = 'Leilei Gu <freedomgll@163.com>'

import threading
import datetime
import os

class ExecuteCommandsThread(threading.Thread):
    def __init__(self, cmdLines, component = None):
        threading.Thread.__init__(self)
        self.cmdLines = cmdLines
        if component is None:
            self.guard = False
        else:
            self.guard = True
            self.component = component

    def run(self):
        begin = datetime.datetime.now()

        if self.guard:
            self.component.start()

        for cmdLine in self.cmdLines:
            self.executeCommand(cmdLine)

        if self.guard:
            self.component.finish()

        time = datetime.datetime.now()-begin
        print('Total time is: '+str(time))

    def executeCommand(self,cmdLine):
        print(cmdLine)
        os.system(cmdLine)

import json
class JsonUtil:
    @staticmethod
    def getJson(file):
        return json.load(open(file))

import configparser
class ConfigFile:
    @staticmethod
    def getConfigFile(file):
        config = configparser.ConfigParser()
        config.read(file)
        return config

    @staticmethod
    def saveConfigFile(config, file):
        with open(file, 'w') as configfile:
            config.write(configfile)

def test1():
    cmds = ['dir','help']
    command = ExecuteCommandsThread(cmds)
    command.run()

def test2():
    class Component:
        def start(self):
            print('Start...')
        def finish(self):
            print('Finish...')

    cmds = ['dir','help']
    command = ExecuteCommandsThread(cmds,Component())
    command.run()

if __name__ == '__main__':
    test1()
    test2()