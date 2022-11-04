import json
from collections import OrderedDict
import math


# 配置文件对象
class SystemConfigurations():
    def __init__(self, config_json_file):
        self.config_json_file = config_json_file
        #  注意有些参数配置文件中没有（DownSipDis）、有些参数读出来后需要转换（TransfersProduceConfig中的角度变成弧度，UpperLimitOfGaussNewteon）
        #  如果这一步都出错，则抛出异常，不进行后续操作
        # TODO 检查设置的参数是否异常
        try:
            json_str = ''
            with open(config_json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.split('//')[0] + '\n'
                    json_str += line
            para_dict = json.loads(json_str, object_pairs_hook=OrderedDict)

            # 配置文件所有参数
            self.MapSizeX = para_dict['MapSizeX']
            self.MapSizeY = para_dict['MapSizeY']
            self.MoveX = para_dict['MoveX']
            self.MoveY = para_dict['MoveY']

            self.PdrModelFile = para_dict['PdrModelFile']
            self.PdrWindowSize = para_dict['PdrWindowSize']
            self.PdrSlideSize = para_dict['PdrSlideSize']

            self.BlockSize = para_dict['BlockSize']
            self.InitailBufferDis = para_dict['InitailBufferDis']
            self.BufferDis = para_dict['BufferDis']
            self.DownSipDis = self.BlockSize

            self.SlideStep = para_dict['SlideStep']
            self.SlideBlockSize = para_dict['SlideBlockSize']
            self.MaxIteration = para_dict['MaxIteration']
            self.TargetMeanLoss = para_dict['TargetMeanLoss']
            self.IterStep = para_dict['IterStep']
            self.UpperLimitOfGaussNewteon = para_dict['UpperLimitOfGaussNewteon'] * self.MaxIteration

            self.EmdFilterLevel = para_dict['EmdFilterLevel']
            self.PdrImuAlignSize = para_dict['PdrImuAlignSize']
            temp = para_dict['TransfersProduceConfig']
            temp[0][2] = math.radians(temp[0][2])
            self.TransfersProduceConfig = temp
            self.MagMapFiles = para_dict['MagMapFiles']
            self.CoordinateOffset = para_dict['CoordinateOffset']
            self.EntranceList = para_dict['EntranceList']


            self.ServerPort = para_dict['ServerPort']
        except Exception as e:
            print(e)
            self.init_succeed = False

        self.init_succeed = True


