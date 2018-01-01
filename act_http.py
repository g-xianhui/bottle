#coding=utf-8
import json
import logging
import os
import site
import sys
import time
import hmac
import hashlib

import bottle
wsgi_app = bottle.Bottle()

if len(sys.argv) == 2:
    APPDIR = sys.argv[1]
else:
    APPDIR = os.path.split(os.path.abspath(__file__))[0]

site.addsitedir(APPDIR)

import act_config as gameconf

LOGGERS = {}
LOGDIR = getattr(gameconf, "act_logdir", os.path.join(APPDIR, "log"))
if not os.path.isdir(LOGDIR):
    os.makedirs(LOGDIR)

def get_logger(name):
    """init log handler."""
    import logging as _logging
    import logging.handlers

    # if requested name in cache, do not generate a new logger instance.
    if name in LOGGERS:
        return LOGGERS[name]

    file_full_path = os.path.join(LOGDIR, "%s.log" % name)

    if getattr(gameconf, "AUTO_ROTATE", True):
        default_handler = logging.handlers.TimedRotatingFileHandler(
            file_full_path, when='midnight', backupCount=7,
        )
    else:
        default_handler = _logging.FileHandler(file_full_path)

    formatter = _logging.Formatter(
        fmt='%(asctime)s %(message)s',
    )
    default_handler.setFormatter(formatter)

    log = _logging.getLogger(name)
    log.addHandler(default_handler)
    for handler in getattr(gameconf, "log_handlers", []):
        log.addHandler(handler)
    log.setLevel(_logging.DEBUG)
    log.log = log.debug
    LOGGERS[name] = log
    return log

logging = get_logger("app")

import subprocess

all_sub_process = {}

def execute_shell(args):
    global all_sub_process
    t = int(time.time())
    name = '%s.log' % t
    path = os.path.join(LOGDIR, name)
    out_file = open(path, 'w')
    sub_obj = subprocess.Popen(args, shell=True, stdout=out_file, stderr=subprocess.STDOUT)
    all_sub_process[name] = sub_obj
    return name

def test_func(name):
    execute_shell(['ls', name])

def upload(script):
    logging.debug("upload: %s", script)
    global all_sub_process
    for k, v in all_sub_process.iteritems():
        if v.poll() is None:
            return 'wait'

    # use test.sh for test
    path = os.getcwd()
    script_path = os.path.join(path, script)
    log_name = execute_shell([script_path])
    return log_name

def get_log(name):
    global all_sub_process
    path = os.path.join(LOGDIR, name)
    out_file = open(path, 'r')
    content = out_file.read()
    sub_obj = all_sub_process.get(name)
    if sub_obj.poll() != None:
        all_sub_process.pop(name)
        return {'fin': 1, 'txt': content}
    else:
        return {'fin': 0, 'txt': content}

all_funcs = {
    'test': test_func,
    'upload': upload,
    "log": get_log,
}

@wsgi_app.get('/agancmd/<name>')
def agancmd(name):
    request = bottle.request
    params = {}
    for k, v in request.query.iteritems():
        params[k] = v

    func = all_funcs.get(name)
    if func:
        ret = func(**params)
    else:
        ret = 'function not found'

    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.response_type = 'text'
    return ret

@wsgi_app.post('/agancmd/<name>')
def agancmd(name):
    request = bottle.request
    params = {}
    for k, v in request.forms.iteritems():
        params[k] = v

    func = all_funcs.get(name)
    if func:
        ret = func(**params)
    else:
        ret = 'function not found'

    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.response_type = 'text'
    return ret

@wsgi_app.get('/aganrequest/<name>')
def aganrequest(name):
    return bottle.template(name)

def main():
    server = 'wsgiref'
    logging.debug("httpd start using %s engine.", server)
    bottle.run(
        app=wsgi_app,
        server=server,
        host="0.0.0.0",
        port=getattr(gameconf, "act_http_port", 8080),
    )

if __name__ == '__main__':
    main()
