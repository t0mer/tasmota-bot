import os
import re
import yaml
import shutil
from os import path
from loguru import logger
from telebot import types, TeleBot
from device import Device

ALLOWED_IDS = os.getenv('ALLOWED_IDS')
BOT_TOKEN = os.getenv('BOT_TOKEN')

tasmotas = []
config_path = "config/config.yaml"
messageid = 0
allowed_ids = os.getenv('ALLOWED_IDS')
bot_token = os.getenv('BOT_TOKEN')
statuses = {"on": "✅", "off": "❌"}
bot = TeleBot(bot_token)


def get_tasmotas():
    try:
        logger.info("Loading Tasmota  devices list")
        if not path.exists(config_path):
            shutil.copy('config.yaml', config_path)
        with open("config/config.yaml",'r',encoding='utf-8') as stream:
            try:
                for tasmota in yaml.safe_load(stream)["tasmotas"]:
                    tasmotas.append(Device(user=tasmota["user"],name=tasmota["name"], password = tasmota["password"], ip = tasmota["ip"]))
                logger.info(str(len(tasmotas)) + " Devices Loded")
            except yaml.YAMLError as exc:
                logger.error(exc)
    except Exception as e:
        logger.error(str(e))
        
        
if __name__=="__main__":
    get_tasmotas()