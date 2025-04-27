
import os
import threading
import json
from pyzenbo.modules.dialog_system import DynamicEditAction
import re
import pyzenbo
import pyzenbo.modules.zenbo_command as commands
import time
from pyzenbo.modules.dialog_system import RobotFace
import pandas as pd
import random
zenbo = pyzenbo.connect('192.168.12.181') #zenbo ip
zenbo_listenLanguageId = 1
myUtterance = ''
zenbo_speakSpeed = 100
zenbo_speakPitch = 100


def exit_function():
  zenbo.robot.unregister_listen_callback()
  zenbo.robot.set_expression(RobotFace.DEFAULT)
  zenbo.release()
  time.sleep(1)


def listen_callback(args):
    global zenbo_listenLanguageId, myUtterance, zenbo_speakSpeed, zenbo_speakPitch
    event_slu_query = args.get('event_slu_query', None)
    if event_slu_query and '不玩了'.lower().replace(".","").replace("!","").replace("?","").strip() == str(event_slu_query.get('app_semantic').get('correctedSentence')).lower().replace(".","").replace("!","").replace("?","").strip():
        zenbo.robot.set_listen_context(
            "1207", "stop_script,intercept_cross_intent,Context_WhenHear")
        
        def job():
            global zenbo_listenLanguageId, myUtterance, zenbo_speakSpeed, zenbo_speakPitch
            exit_function()
            os._exit(0)
        t = threading.Thread(target=job)
        t.start()
    event_slu_query = args.get('event_slu_query', None)
    if event_slu_query and event_slu_query.get('app_semantic').get('correctedSentence') and event_slu_query.get('app_semantic').get('correctedSentence') != 'no_BOS':
        myUtterance = str(event_slu_query.get(
           'app_semantic').get('correctedSentence'))
    if event_slu_query and event_slu_query.get('error_code') == 'csr_failed':
        myUtterance = ''


zenbo.robot.set_expression(RobotFace.DEFAULT)
time.sleep(int(0.5))
zenbo.robot.register_listen_callback(1207, listen_callback)
zenbo.robot.dynamic_edit_instance(
   "1207", DynamicEditAction.ADD_NEW_INSTANCE, "WhenHearWords", ['不玩了'])
zenbo.robot.set_listen_context(
   "1207", "stop_script,intercept_cross_intent,Context_WhenHear")
time.sleep(int(1))

qa_data = pd.read_excel("D:\\pyzenbo\\pyzenbo\\test.xlsx")
lenth = len(qa_data)



for count in range(1000000):
    zenbo_listenLanguageId = 1
    zenbo.robot.speak_and_listen(
        '請吩咐!',{'listenLanguageId': zenbo_listenLanguageId})
    time.sleep(int(1))
    c = 0
    for i in range(lenth):
        if myUtterance == qa_data.iloc[i][0]:
            for j in range(5):
                if not pd.isna(qa_data.iloc[i][j]):
                    c = c+1  

            zenbo_speakLanguage = 1
            zenbo.robot.set_expression(RobotFace.PREVIOUS, qa_data.iloc[i][random.randint(1,c)], {
                               'speed':zenbo_speakSpeed, 'pitch':zenbo_speakPitch, 'languageId':zenbo_speakLanguage} , sync = True)
            time.sleep(0.5)
try:
    while True:
        time.sleep(int(10))
finally:
     exit_function()
