# 导入所需的库
import requests
import json
import os
import threading
import pyzenbo
import pyzenbo.modules.zenbo_command as commands
import time
from pyzenbo.modules.dialog_system import DynamicEditAction, RobotFace
import sqlite3

# 连接到Zenbo机器人
zenbo = pyzenbo.connect('192.168.100.168')

# 设置语言ID（1为中文）
zenbo_listenLanguageId = 1

# 存储用户说话内容的变量
myUtterance = ''

# 设置说话速度和音调
zenbo_speakSpeed = 100
zenbo_speakPitch = 100

# 退出程序时的清理函数
def exit_function():
    zenbo.robot.unregister_listen_callback()  # 注销监听回调
    zenbo.robot.set_expression(RobotFace.DEFAULT)  # 设置默认表情
    zenbo.release()  # 释放Zenbo连接
    time.sleep(1)

# 监听回调函数，处理用户语音输入
def listen_callback(args):
    global zenbo_listenLanguageId, myUtterance, zenbo_speakSpeed, zenbo_speakPitch
    event_slu_query = args.get('event_slu_query', None)

    # 检查是否说了"我問完了"，如果是则退出程序
    if event_slu_query and '我問完了'.lower().replace(".","").replace("!","").replace("?","").strip() == str(event_slu_query.get('app_semantic').get('correctedSentence')).lower().replace(".","").replace("!","").replace("?","").strip():
        zenbo.robot.set_listen_context("1207", "stop_script,intercept_cross_intent,Context_WhenHear")
        def job():
            global zenbo_listenLanguageId, myUtterance, zenbo_speakSpeed, zenbo_speakPitch
            exit_function()
            os._exit(0)
        t = threading.Thread(target=job)
        t.start()

    # 获取用户说话内容
    event_slu_query = args.get('event_slu_query', None)
    if event_slu_query and event_slu_query.get('app_semantic').get('correctedSentence') and event_slu_query.get('app_semantic').get('correctedSentence') != 'no_BOS':
        myUtterance = str(event_slu_query.get('app_semantic').get('correctedSentence'))

    # 如果语音识别失败，清空用户说话内容
    if event_slu_query and event_slu_query.get('error_code') == 'csr_failed':
        myUtterance = ''

# 初始化Zenbo表情和监听设置
zenbo.robot.set_expression(RobotFace.DEFAULT)
time.sleep(0.5)

# 注册监听回调
zenbo.robot.register_listen_callback(1207, listen_callback)

# 添加"我問完了"的语音识别实例
zenbo.robot.dynamic_edit_instance("1207", DynamicEditAction.ADD_NEW_INSTANCE, "WhenHearWords", ['我問完了'])
zenbo.robot.set_listen_context("1207", "stop_script,intercept_cross_intent,Context_WhenHear")
time.sleep(1)

# Google Gemini API设置
api_key = "AIzaSyBToGaFA2IcmvCZJQ-TicysWYp8rFNqOD4"
headers = {'Content-Type': 'application/json'}
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

# 数据库连接和药品查询函数
def connect_db():
    return sqlite3.connect('medicines.db')

def get_medicine_by_use(symptom):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM medicines WHERE uses LIKE ?
    ''', ('%' + symptom + '%',))
    medicines = cursor.fetchall()
    conn.close()
    return medicines

def suggest_medicine(symptom):
    medicines = get_medicine_by_use(symptom)
    if not medicines:
        return "抱歉，沒有找到适合的药品。"
    suggestion = []
    for med in medicines:
        suggestion.append(f"{med[1]} ({med[3]}) 剩餘 {med[4]} 錠，效期至 {med[6]}")
    return "\n".join(suggestion)

# 更新药品库存
def update_medicine_quantity(medicine_id, quantity_used):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE medicines
    SET remaining = remaining - ?
    WHERE id = ?
    ''', (quantity_used, medicine_id))
    conn.commit()
    conn.close()

# 发起API请求获取回答
def handle_user_input(utterance):
    # 使用症状来推荐药品
    answer = suggest_medicine(utterance)

    # 如果需要，你可以继续扩展到Google Gemini API
    data = {
        "contents": [{"parts": [{"text": f"{utterance}?"}]}]
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        content = r.json()
        gemini_answer = content['candidates'][0]['content']['parts'][0]['text']
        return f"{answer}\n另外，Google Gemini建议：{gemini_answer}"
    except Exception as e:
        return f"{answer}\n抱歉，发生了错误，请稍后再试。"

# 主程序循环，持续监听用户的请求并回答
for count in range(1000000):
    zenbo.robot.speak_and_listen('你有問題都可以詢問我!', {'listenLanguageId': zenbo_listenLanguageId})
    time.sleep(1)

    # 使用获取的语音内容生成回答
    if myUtterance:
        answer = handle_user_input(myUtterance)

        # 让Zenbo说出回答
        zenbo.robot.set_expression(RobotFace.PREVIOUS, answer, {
            'speed': zenbo_speakSpeed,
            'pitch': zenbo_speakPitch,
            'languageId': zenbo_listenLanguageId
        }, sync=True)

        time.sleep(0.5)

# 程序结束前的清理工作
try:
    while True:
        time.sleep(10)
finally:
    exit_function()
