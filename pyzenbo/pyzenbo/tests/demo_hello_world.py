import logging

import pyzenbo
from pyzenbo.modules.dialog_system import RobotFace

logging.basicConfig(level=logging.INFO)
host = '192.168.12.181'#zenbo ip #網路不一樣 ip位置要記得改!! 

sdk = pyzenbo.connect(host)

for i in range(1,10):
    for j in range(1,10):
        sdk.robot.set_expression(RobotFace.PROUD_ADV, "%d乘以%d等於%d"%(i,j,i*j))
    #sdk.robot.set_expression(RobotFace.emotion, fromatstring往後找值%(i))
#ADV大概都會動
#sdk.robot.set_expression(RobotFace.HIDEFACE)

sdk.release()
