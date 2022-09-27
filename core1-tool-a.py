import json
import requests
import urllib.request
import json
from flask import Flask, request, jsonify, render_template, abort
import werkzeug
from datetime import date
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
import pandas as pd
from json.decoder import JSONDecodeError
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
# from pydantic import BaseModel
info = Info(title="CORE-1 PT TI TOOL", version="1.0.0")
app = OpenAPI(__name__, info=info)

core1_tag = Tag(name="CORE-1", description="CORE-1 TEAM")

API_URL = 'http://127.0.0.1:5000'
OPEN_API_URL='http://127.0.0.1:5000/openapi'

# class TestingQuery(BaseModel):
#     team: int
#     author: str

testlink = "http://smartlab-service.int.net.nokia.com:9000/log/SDAN-iHUB_Protocols/2209.458/CHE_CORE1_SDFX_FANT-F/SB_Logs_F32F-keerthak-Sep17155818_SLS_BATCH_1/ROBOT/output.json"
testtms = "http://smartlab-service.int.net.nokia.com:9000/log/SDAN-iHUB_Protocols/2209.458/CHE_CORE1_SDFX_FANT-F/SB_Logs_F32F-keerthak-Sep17155818_SLS_BATCH_1/ROBOT/ATDD_focus.tms"

CORS(app)
# today = date.today()
# d4 = today.strftime("%b-%d-%Y")
# Merge dict


def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res
# print(Merge({"Status":"Okay"},{"NT":"FANT-G"}))


def url_checker(url):
    try:
        get = requests.get(url)
        if get.status_code == 200:
            return get.status_code  # (f"{url}: is reachable")
        else:
            return (f"{url}: is Not reachable, status_code: {get.status_code}")
    # Exception
    except requests.exceptions.RequestException as e:
        # print URL with Errs
        # raise SystemExit(f"{url}: is Not reachable \nErr: {e}")
        return (f"{url}: is Not reachable \nErr: {e}")


def give_json(link):
    with urllib.request.urlopen(link) as url:
        data = json.load(url)
    data_by_fil = []
    for d in data:
        if "failSteps" in d:
            if not d["failSteps"]:
                # empty list
                data_by_fil.append(Merge({k: d[k] for k in (
                    "jobName", "runOnObjName", "ATCName", "testResult", "startTime")}, {"Status": "OK"}))
                #print(Merge({k:d[k] for k in ("jobName", "runOnObjName", "failSteps", "ATCName", "startTime")},{"Status","Okay"}))
            else:
                # list not empty
                data_by_fil.append(Merge({k: d[k] for k in (
                    "jobName", "runOnObjName", "ATCName", "testResult", "startTime")}, {"Status": "NOK"}))
        else:
            # "failSteps" key missing
            data_by_fil.append(Merge({k: d[k] for k in (
                "jobName", "runOnObjName", "ATCName", "testResult", "startTime")}, {"Status": "Failstep Missing"}))
    return data_by_fil


def give_tms(link):
    with urllib.request.urlopen(link) as url:
        data = url.read()
    return data.decode(encoding="utf-8")

# print(type(give_tms(testtms).decode(encoding="utf-8")))


# print(type(give_tms(testjson)))

def str_to_txt(data):
    # open text file
    text_file = open("a.txt", "w")
    # write string to file
    text_file.write(data)
    # close file
    text_file.close()


def giv_link(link):
    str_to_txt(give_tms(link))


def give_json_with_tms(link):
    arr = []
    giv_link(link)
    with open('a.txt', 'r') as f:
        for line in f:
            # split around semicolon and then strip spaces from the ends
            fields = list(map(lambda s: s.strip(), line.split(';')))
            if "setup" not in fields[4] and "teardown" not in fields[4]:
                arr.append({
                    "Testcase": fields[4],
                    "Board": fields[5],
                    "Domain":fields[7],
                    "Status": fields[11],
                    "RunTime": fields[13],
                    "Buildname": fields[16],
                })
            else:
                continue
    with open('key_registry.json', 'r') as f:
        datalist = json.load(f)
    if any([(obj.get('URL') == link) for obj in datalist]):
        print("Already registered")
    else:
        print("New Entry")
        with open('key_registry.json', 'r+') as f:
            dtlist = json.load(f)
            # Update your dict here
            dtlist.append(dict({'URL': link, 'count': 0}))
            f.seek(0)
            f.truncate()
            json.dump(dtlist, f)
    return arr


def merge_lst(lst1, lst2):
    result = []
    lst1.extend(lst2)
    for myDict in lst1:
        if myDict not in result:
            result.append(myDict)
    return result


def give_entry(data):
    with open('key_registry.json', 'r') as f:
        datalist = json.load(f)
        if any([(obj.get('URL') == data and obj.get('count') == 0) for obj in datalist]):
            # print("Ready to append")
            try:
                with open('entire-output.json', 'r+') as f:
                    dtlist = json.load(f)
                    # dtlist.append((json.loads(give_json_with_tms(data), indent=4)))
                    f.seek(0)
                    f.truncate()
                    json.dump(merge_lst(dtlist, give_json_with_tms(data)), f)
            except ValueError:
                dtlist = []
                with open('entire-output.json', 'r+') as f:
                    json.dump(merge_lst(dtlist, give_json_with_tms(data)), f)
            with open('key_registry.json', 'r+') as fs:
                dtlista = json.load(fs)
                for obj in dtlista:
                    if obj.get('URL') == data:
                        obj['count'] = 1
                # print("changed")
                # dtlista.append(dict({'URL':data,'count':1}))
                fs.seek(0)
                fs.truncate()
                json.dump(dtlista, fs)
            return ("Appended")
        elif any([(obj.get('URL') == data and obj.get('count') == 1) for obj in datalist]):
            return ("Already appended")
        else:
            return ("URL not available")


def read_entire_json():
    arr = []
    with open('entire-output.json', 'r') as f:
        datalist = json.load(f)
        arr = datalist
    return arr


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.get('/test', tags=[core1_tag])
def test():
    return jsonify('Test Success')


@app.get('/entire-json',  tags=[core1_tag])
def download_entire():
    return jsonify(read_entire_json())


@app.post('/with-json', doc_ui=False)
def give_a_json():
    record = json.loads(request.data)
    url = record['url']
    return jsonify(give_json(url))


@app.post('/with-tms', tags=[core1_tag])
def give_a_tms():
    try:
        record = json.loads(request.data)
        url = record['url']
        if url_checker(url) == 200:
            return jsonify(give_json_with_tms(url)), 200
        else:
            return jsonify({"msg": "URL not reachable"}), 404
    except IndexError:
        return jsonify({"msg": "Internal Server Error"}), 500


@app.post('/append-exl', tags=[core1_tag])
def append_excel():
    try:
        record = json.loads(request.data)
        url = record['url']
        if url_checker(url) == 200:
            check = give_entry(url)
            if check == "Appended":
                return jsonify({"msg": "Successfully appended!"}), 200
            else:
                return jsonify({"msg": check}), 200
        else:
            return jsonify({"msg": "URL not reachable"}), 404
    except IndexError:
        return jsonify({"msg": "Internal Server Error"}), 500


app.run(debug=True)
app.run(host='0.0.0.0', port=5000)

# http://127.0.0.1:5000/openapi/swagger#/
# # JSON Body
# {
#     "url":"http://smartlab-service.int.net.nokia.com:9000/log/SDAN-iHUB_Protocols/2209.458/CHE_CORE1_SDFX_FANT-F/SB_Logs_F32F-keerthak-Sep17155818_SLS_BATCH_1/ROBOT/output.json"
# }

# .TMS
# {
#     "url":"http://smartlab-service.int.net.nokia.com:9000/log/SDAN-iHUB_Protocols/2209.458/CHE_CORE1_SDFX_FANT-F/SB_Logs_F32F-keerthak-Sep17155818_SLS_BATCH_1/ROBOT/ATDD_focus.tms"
# }
