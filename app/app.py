import os
import re
import socket
import ipaddress
import subprocess
from os import path
from loguru import logger
from device import Device
from telebot import types, TeleBot
from mac_vendor_lookup import MacLookup

mac = MacLookup()


ALLOWED_IDS = os.getenv('ALLOWED_IDS')
BOT_TOKEN = os.getenv('BOT_TOKEN')

TASMO_USER = os.getenv('TASMO_USER')
TASMO_PASSWORD = os.getenv('TASMO_PASSWORD')
IP_NETWORK=os.getenv("IP_NETWORK")
devices = []
messageid = 0
statuses = {"ON": "✅", "OFF": "❌"}
bot = TeleBot(BOT_TOKEN)
mac = MacLookup()
network = ipaddress.ip_network(IP_NETWORK)


messageid = 0
commands = [{"text": "רשימת שקעים", "callback_data": "list"},]


# **************************************
# ** Get MAC address of a remote host **
def arpreq_ip(ip):
    # type: (str) -> Optional[str]
    import arpreq
    return arpreq.arpreq(ip)

def ping(host):
    try:
        p = subprocess.Popen("fping -C1 -q "+ host +"  2>&1 | grep -v '-' | wc -l", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        status = re.findall('\d+', str(output))[0]
        if status=="1":
            return True
        else:
            return False
    except Exception as e:
        logger.error(str(e))
        return False

def port_scanner(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.1)
        result = s.connect_ex((ip,80))
        if result ==0:
            pass
        s.close()
    except Exception as e:
        logger.error(f"Error scanning ip. {str(e)}")

def get_devices():
    devices.clear()
    for ip in network:
        try:
            port_scanner(str(ip))
            if ip == network.broadcast_address or ip == network.network_address:
                continue
            mac_address = arpreq_ip(ip)
            if mac_address is None:
                continue
            else:
                if(ping(str(ip))):
                    if mac_address.lower().startswith(('4c:eb:d6','80:64:6f')):
                        devices.append(Device(ip=str(ip),mac_address=mac_address))
        except Exception as e:
            logger.error(f"Error getting device info. {str(e)}")
    return devices

def devices_keyboard(devices):
    try:
        logger.debug(f"{len(devices)} sockets found in the network")
        markup = types.InlineKeyboardMarkup()
        markup.row_width=2
        for device in devices:
            device.login()
            markup.add(types.InlineKeyboardButton(
                text=f"{device.getFriendlyName()}  ({device.getPower()})",
                callback_data="_device_" + device.ip))

        return markup
    except Exception as e:
        logger.error("Error creating devices keyboard. " + str(e))


# ------------- Build command keyboard -----------------
def command_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=command['text'],
                    callback_data=command["callback_data"]
                )
            ]
            for command in commands
        ], row_width=1
    )



# ---------------- Handle the start menu --------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        loading = open("loading.gif",'rb')
        # devices = get_devices()
        if str(message.chat.id) in ALLOWED_IDS:
            welcome_messageid=bot.send_message(message.chat.id, text="Searcing for sockets").message_id
            loading_messageid = bot.send_animation(message.chat.id, loading).message_id
            devices = get_devices()
            bot.delete_message(message_id=welcome_messageid,chat_id=message.chat.id)
            bot.delete_message(message_id=loading_messageid,chat_id=message.chat.id)
            bot.send_message(message.chat.id,"Sockets list:",reply_markup=devices_keyboard(devices))
    except Exception as e:
        logger.error(e)

def run():
    for device in get_devices():
        try:
            
            device.login()
            status = device.getStatus()
            print("--------------------------------------------------------------------------------")  
            print(f"Friendly Name: {device.getFriendlyName()}")
            print(f"Device IP: {device.ip}")
            print(f"Power State: {device.getPower()}")
            print(f"Total Energy: {status.get('StatusSNS').get('ENERGY').get('Total','')}Kwh")
            print(f"Today Energy: {status.get('StatusSNS').get('ENERGY').get('Today')}Kwh")
            print(f"Yesterday Energy: {status.get('StatusSNS').get('ENERGY').get('Yesterday')}Kwh")
            print(f"Voltage: {status.get('StatusSNS').get('ENERGY').get('Voltage')}V")
            print(f"Current: {status.get('StatusSNS').get('ENERGY').get('Current')}A")
            print("--------------------------------------------------------------------------------")
        except:
            pass
           
if __name__=="__main__":
    logger.info("Starting the bot")
    bot.infinity_polling()
    # run()