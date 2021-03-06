#encoding: utf-8
import logging
import time
import os
import requests
import json
import traceback

logger = logging.getLogger(__name__)

SERVER_URL = 'http://localhost:9001/performs/'

def execute_cmd(cmd):
    _fh = os.popen(cmd)
    _cxt = _fh.read()
    _fh.close()
    return _cxt

def get_ip():
    _cmd = "ifconfig eth0 | grep 'inet addr' | awk '{print $2}'"
    _cxt = execute_cmd(_cmd)
    return str(_cxt.split(':')[-1]).strip()
    

def collect_cpu():
    _cmd = "top -n 1 | grep Cpu | awk '{print $5}'"
    _cxt = execute_cmd(_cmd)
    return 100 - float(_cxt.split('%')[0])


def collect_ram():
    _fh = open('/proc/meminfo')
    _total = float(_fh.readline().split()[1])
    _free = float(_fh.readline().split()[1])
    _buffer = float(_fh.readline().split()[1])
    _fh.close()
    return 100 - 100 * (_free + _buffer) / _total

def collect():
    _rt = {}
    _rt['ip'] = get_ip()
    _rt['cpu'] = collect_cpu()
    _rt['ram'] = collect_ram()
    _rt['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    return _rt

def send(msg):
    try:
        _reponse = requests.post(SERVER_URL, data=json.dumps(msg), headers={"Content-Type":"application/json"})
        if not _reponse.ok:
            logger.error('error send msg:%s', msg)
    except BaseException as e:
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s [%(lineno)d] %(levelname)s:%(message)s",
                    filename="agent.log")

    while True:
        try:
            _msg = collect()
            logger.debug(_msg)
            send(_msg)
            time.sleep(10)
        except BaseException as e:
            logger.error(traceback.format_exc())