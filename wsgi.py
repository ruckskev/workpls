#!/usr/bin/env python

import os
import re
import datetime

import fit

def application(environ, start_response):
    logpath = "%s/winti.log" % os.getenv("OPENSHIFT_DATA_DIR")
    ctype = 'text/plain'

    if environ['PATH_INFO'] == '/history':
        lines = open(logpath).readlines()
        response_body = "".join(lines)
    elif environ['PATH_INFO'] == '/current':
        lines = open(logpath).readlines()
        response_body = lines[-1]	
    elif environ['PATH_INFO'] == '/filter':
	lines = open("logpath","r")
	output = []
	for line in lines:
		for line in lines:
			if  (not line.find(',,') >= 0):
        			if(not line.endswith(',')):
            				output.append(line)
	lines.close()
	response_body = "".join(output)
    elif environ['PATH_INFO'].startswith('/predict/'):
        s = re.compile("/predict/(\d+)")
        m = s.match(environ['PATH_INFO'])
        predpeople = int(m.group(1))
        histstamps = []
        histpeople = []
        lines = open(logpath).readlines()
        for line in lines:
            try:
                stamp, people, date = line.split(",")
            except:
                stamp, people = line.strip().split(",")
                date = None
            if stamp == "" or people == "":
                continue
            histstamps.append(int(stamp))
            histpeople.append(int(people))
        fitlambda = fit.fit(histpeople, histstamps)
        predstamp = int(fitlambda(predpeople))
        preddate = datetime.datetime.strftime(datetime.datetime.fromtimestamp(predstamp), "%a, %-d. %B %Y, %-H:%M")
        response_body = "Predicted date when the population of Winterthur reaches %s: %s" % (m.group(1), preddate)
    elif environ['PATH_INFO'] == '/source':
        response_body = "https://github.engineering.zhaw.ch/spio/wintipoptracker.git"
    else:
        response_body = "This is a data source/data service informing about the population of Winterthur. Use /filter to filter /current or /history or /predict/{number-of-inhabitants} as invocation methods. Use /source to get a pointer to the service implementation source code."
    response_body = response_body.encode('utf-8')

    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]

    start_response(status, response_headers)
    return [response_body]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    httpd.handle_request()
