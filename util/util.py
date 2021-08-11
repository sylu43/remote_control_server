import configparser
import time

def getConf():
    configPath = 'files/config.txt'
    parser = configparser.ConfigParser()
    parser.read(configPath)
    return parser
