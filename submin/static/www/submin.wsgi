#!/usr/bin/python3
import os
import sys
import inspect
import logging


# put the root directory of the script into the include path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) #www
parentdir = os.path.dirname(currentdir) #static
basedir = os.path.dirname(os.path.dirname(parentdir)) #submin
sys.path.insert(0,basedir) 

logging.basicConfig(filename='/tmp/example.log',level=logging.DEBUG)


svndir = os.path.dirname(basedir)+"/swig-py3/subversion/bindings/swig/python"
sys.path.insert(0,svndir) 

try:
    import uwsgi
    from uwsgidecorators import filemon
except ImportError as e:
    pass
else:
    filemon(__file__)(uwsgi.reload)

def application(environ, start_response):
    for key in ['SUBMIN_ENV', 'SUBMIN_REMOVE_BASE_URL']:
        if key in os.environ and key not in environ:
            environ[key] = os.environ[key]
        if key in environ:
            os.environ[key] = environ[key]

    # __file__ contains <submin-dir>/static/www/submin.wsgi
    submin_www_dir = os.path.dirname(__file__)
    submin_static_dir = os.path.dirname(submin_www_dir)
    submin_dir = os.path.dirname(submin_static_dir)
    os.chdir(submin_www_dir) # same behaviour as CGI script

    from submin.bootstrap import SubminInstallationCheck
    check = SubminInstallationCheck(submin_dir, environ)
    if not check.ok:
        start_response("500 Not Ok", [])
        return check.error_page().encode("utf-8")

    from submin.models import storage
    storage.open()

    try:
        from submin.dispatch.wsgirequest import WSGIRequest
        from submin.dispatch.dispatcher import dispatcher
        req = WSGIRequest(environ)
        response = dispatcher(req)
        headers = []
        for k,v in response.headers.items():
            item = (k,v)            
            headers.append(item)

        #response.headers = [
        #    ('Content-Type','text/html; charset=utf-8'),
        #    ('Set-Cookie','SubminSessionID=8620c46216126cca44edd2b33dba5b1c; expires=Sun, 16 Aug 2020 12:44:52 -0000; Path=/submin2/ah')    
        #]
        response.headers = headers
        start_response(response.status(), response.headers)
        content = response.encode_content()
    except Exception as e:
        import traceback
        trace = traceback.extract_tb(sys.exc_info()[2])
        list = traceback.format_list(trace)
        list.append(str(e))
        start_response('500 Not Ok', [])
        content = ''.join(list)
    
    storage.close()
    return bytes(content,'utf-8')
