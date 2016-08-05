#coding:utf-8
import sqlite3
import redis
redisServer =  redis.StrictRedis(host='192.168.10.239', port=6379)


from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import json
#导入包装的csrf请求，对跨站攻击脚本做处理
from django.views.decorators.csrf import csrf_exempt
import time
import os
import sys
import platform

from ftplib import FTP
ftp = FTP()
from socket import *




@login_required(login_url="/login/")
@csrf_exempt
def index(request):
    if request.method == 'POST':
        postdata = request.POST
        msg = postdata.get('message')
        lastindex = postdata.get('lastindex')
        data ={}
        if msg:
            #lsize = redisServer.llen('index_chatdata')
            user = request.user.username
            data['username'] = user
            data['message'] = msg
            data['time'] = time.asctime()
            #print json.dumps(data)
            lsize = redisServer.rpush('index_chatdata',json.dumps(data))
            data['id'] = str(lsize)
            return HttpResponse(json.dumps(data))
        if lastindex:
            lastindex = int(lastindex)
            lsize = redisServer.llen('index_chatdata')
            datalist =[]
            if lastindex ==lsize -1:
                return HttpResponse(json.dumps(data))
            if lastindex < 0:
                data = redisServer.lrange('index_chatdata',lsize-10,lsize)
                lastindex = lsize - 10
            else:
                data = redisServer.lrange('index_chatdata',lastindex,lsize)
            for d in data:
                data_dict =json.loads(d)
                data_dict['id'] = str(lastindex)
                lastindex = lastindex+1
                datalist.append(data_dict)
            return HttpResponse(json.dumps(datalist))
        return HttpResponse(json.dumps(data))
    return render(
        request,
        "NiceAdmin/index.html",
    )

@csrf_exempt
def login(request):
    if request.method == 'POST':
        postdata = request.POST
        username = postdata.get('name', '')
        password = postdata.get('pwd', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponse(json.dumps({"msg":"true","url":"/index/"}))
        return HttpResponse(json.dumps({"msg":"false"}))

    return render(
        request,
        "NiceAdmin/login.html",
    )

@login_required(login_url="/login/")
def mediaInfo(request):
    return render(
        request,
        "NiceAdmin/MediaInfo.html",
    )


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url="/login/")
def  tabledata(request):
    print request
    return render(
        request,
        "NiceAdmin/tabledata.html",
    )



def countFromTable():
    with sqlite3.connect('MediaInfoDB.db') as conn:
        cu = conn.cursor()
        cu.execute('select count(1) from VideoInfo')
        data = cu.fetchone()
        cu.close()
        return int(data[0])

def selectFromMediaInfoDB(start,length):
    with sqlite3.connect('MediaInfoDB.db') as conn:
        cu = conn.cursor()
        sql = 'select * from VideoInfo  LIMIT %s,%s' % (start,length)
        cu.execute(sql)
        data = cu.fetchall()
        l = [list(x) for x in data]
        cu.close()
        return l

def  server_side(request):
    recordsTotal = countFromTable()
    GetData = request.GET
    draw = GetData.get("draw")
    start = request.GET.get("start",0)
    length= request.GET.get("length")
    search = request.GET.get("search[value]")
    columns = request.GET.get("columns[1]")
    #print draw,start,length,search,columns
    data = selectFromMediaInfoDB(start,length)
    #print(data)


    return HttpResponse(json.dumps({
  "draw": draw,
  "recordsTotal": recordsTotal,
  "recordsFiltered": recordsTotal,
  "data": data
}))


def selectDataFromMediaInfoDB(start,length):
    with sqlite3.connect('MediaInfoDB.db') as conn:
        cu = conn.cursor()
        sql = 'select * from VideoInfo  LIMIT %s,%s' % (start,length)
        cu.execute(sql)
        data = cu.fetchall()
        datalist =[]
        for x in data:
            d ={}
            d['ID'] = x[0]
            d['Duration'] = x[1]
            d['Width'] = x[2]
            d['Height'] = x[3]
            d['FPS'] = x[4]
            datalist.append(d)
        cu.close()
        return datalist

@login_required(login_url="/login/")
@csrf_exempt
def  dtgrid(request):
    if request.method == 'POST':
        postdata = request.POST['dtGridPager']
        postdata=json.loads(postdata)
        pageSize =  postdata["pageSize"]
        startRecord = postdata["startRecord"]
        recordCount = countFromTable()
        postdata["recordCount"] = recordCount
        addone = 0
        if recordCount%pageSize>0:
            addone =1

        postdata["pageCount"] = recordCount/pageSize+addone
        postdata['exhibitDatas'] = selectDataFromMediaInfoDB(startRecord,pageSize)
        postdata['isSuccess'] = True
        return HttpResponse(json.dumps(postdata))

    return render(
            request,
            "NiceAdmin/dtgrid_test.html",
        )

def get_os():
    os_ = platform.system()
    if os_ == "Windows":
        return "n"
    else:
        return "c"



@csrf_exempt
def ping_ip(request):
    if request.method == 'POST':
        postdata = request.POST
        ip_str = postdata.get('IP', '')
        cmd = ["ping", "-{op}".format(op=get_os()), "1", ip_str]
        output = os.popen(" ".join(cmd)).readlines()
        flag = False
        for line in list(output):
            if not line:
                continue
            if str(line).upper().find("TTL") >=0:
                flag = True
                break
        if flag:
            msg = {"msg":"true"}
            return HttpResponse(json.dumps(msg))
        else:
            msg = {"msg":"false"}
            return HttpResponse(json.dumps(msg))

@csrf_exempt
def ConnectServer(request):
    if request.method == 'POST':
        postdata = request.POST
        ip_str = postdata.get('IP', '')
        timeout = 2
        port = 21
        global ftp
        try:
            ftp.connect(ip_str,port,timeout) # 连接FTP服务器
            ftp.login('user','12345') # 登录
            print ftp.getwelcome()  # 获得欢迎信息
            dirtlist = ftp.nlst()       # 获得目录列表
            msg = {"msg":"true","dirtlist":dirtlist}
            return HttpResponse(json.dumps(msg))
        except:
            msg = {"msg":"false"}
            return HttpResponse(json.dumps(msg))

@csrf_exempt
def uninstall(request):
    if request.method == 'POST':
        postdata = request.POST
        ip = postdata.get('IP', '')
        fileName = postdata.get('filename', '')
        port = 9999
        bufsize = 1024
        addr = (ip,port)
        client = socket(AF_INET,SOCK_STREAM)
        client.connect(addr)
        data={}
        data["cmd"] = "uninstallmodule"
        data["filename"] = fileName
        client.send(json.dumps(data))
        data = client.recv(bufsize)
        data = json.loads(data)
        client.close()
        print data["status"]
        if data["status"] == "200":
            msg = {"msg":"true"}
            return HttpResponse(json.dumps(msg))
        else:
            print data["errorInfo"]
            msg = {"msg":"false","errorInfo":data["errorInfo"]}
            return HttpResponse(json.dumps(msg))



@csrf_exempt
def install(request):
    if request.method == 'POST':
        postdata = request.POST
        ip = postdata.get('IP', '')
        fileName = postdata.get('filename', '')
        rsize=0L
        ftp.voidcmd('TYPE I')
        try:
            rsize=ftp.size(fileName)
            print rsize
        except:
            pass


        if (rsize==None):
            rsize=0L
        localpath = "\\media\\"+ fileName
        lsize=os.stat(localpath).st_size
        print('rsize : %d, lsize : %d' % (rsize, lsize))

        if (rsize==lsize):
            print 'remote filesize is equal with local'
            list = ftp.nlst()       # 获得目录列表
            msg = {"msg":"false","errorInfo":"remote filesize is equal with local","listdir":list}
            return HttpResponse(json.dumps(msg))

        if (rsize<lsize):
            localf=open(localpath,'rb')
            localf.seek(rsize)

            datasock=''
            esize=''
            try:
                print(fileName)
                ftp.voidcmd('TYPE I')
                datasock,esize=ftp.ntransfercmd("STOR "+fileName,rsize)
            except Exception, e:
                print >>sys.stderr, '----------ftp.ntransfercmd-------- : %s' % e
                msg = {"msg":"false","errorInfo": e}
                return HttpResponse(json.dumps(msg))
            cmpsize=rsize
            while True:
                buf=localf.read(1024 * 1024)
                if not len(buf):
                    print '\rno data break'
                    break
                datasock.sendall(buf)
                cmpsize+=len(buf)
                print '\b'*30,'uploading %.2f%%'%(float(cmpsize)/lsize*100),
                if cmpsize==lsize:
                    print '\rfile size equal break'
                    break
            datasock.close()
            print 'close data handle'
            localf.close()
            print 'close local file handle'
            # self.ftp.voidcmd('NOOP')
            # print 'keep alive cmd success'
            ftp.voidresp()
            print 'No loop cmd'
        #self.ftp.quit()


        port = 9999
        bufsize = 1024
        addr = (ip,port)
        client = socket(AF_INET,SOCK_STREAM)
        client.connect(addr)
        data={}
        data["cmd"] = "extractFile"
        data["filename"] = fileName
        client.send(json.dumps(data))
        data = client.recv(bufsize)
        data = json.loads(data)
        client.close()
        print data["status"]
        if data["status"] == "200":
            msg = {"msg":"true"}
            return HttpResponse(json.dumps(msg))
        else:
            msg = {"msg":"false","errorInfo":data["errorInfo"]}
            return HttpResponse(json.dumps(msg))




@csrf_exempt
def Getfilelist(request):
    if request.method == 'POST':
        list = os.listdir("/media/")
        msg = {"msg":"true","listdir":list}
        return HttpResponse(json.dumps(msg))

@csrf_exempt
def removefile(request):
    if request.method == 'POST':
        postdata = request.POST
        filename = postdata.get('filename', '')
        filePath = "\\media\\"+filename
        os.remove(filePath)

        list = os.listdir("/media/")
        msg = {"msg":"true","listdir":list}
        return HttpResponse(json.dumps(msg))



@csrf_exempt
def Getremotefilelist(request):
    if request.method == 'POST':
        postdata = request.POST
        ip = postdata.get('IP', '')
        port = 9999
        bufsize = 1024
        addr = (ip,port)
        client = socket(AF_INET,SOCK_STREAM)
        client.connect(addr)
        data={}
        data["cmd"] = "listdir"
        client.send(json.dumps(data))
        data = client.recv(bufsize)
        data = json.loads(data)
        client.close()

        msg = {"msg":"true","listdir":data['listdir']}
        return HttpResponse(json.dumps(msg))

def handle_uploaded_file(f):
    file_name = ""

    try:
        path = "/media/editor" + time.strftime('/%Y/%m/%d/%H/%M/%S/')

        path = "/media/"
        print path
        if not os.path.exists(path):
            os.makedirs(path)
        file_name = path + f.name
        destination = open(file_name, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    except Exception, e:
        print e

    return file_name



@login_required(login_url="/login/")
@csrf_exempt
def  upload(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])
        postdata = {"data":"success"}
        return HttpResponse(json.dumps(postdata))

    return render(
            request,
            "NiceAdmin/upload.html",
        )




@login_required(login_url="/login/")
@csrf_exempt
def ComputerInfo(request):
    if request.method == 'POST':
        postdata = request.POST
        IP = postdata.get('IP', '')
        keys =  'ComputerList:'+IP
        if IP is not None:
            computerdict ={}
            ComputerList = redisServer.keys('ComputerList:*')
            for c in ComputerList:
                datajson = redisServer.get(c)
                d = c.split(":")
                computerdict[d[1]] = (json.loads(datajson))
            return HttpResponse(json.dumps(computerdict))

    return render(
        request,
        "NiceAdmin/ComputerInfo.html",
    )

keys = None
@login_required(login_url="/login/")
@csrf_exempt
def ProgressInfo(request):
    global keys
    if request.method == 'GET':
        getdata = request.GET
        IP = getdata.get('IP', '')
        keys =  'Progress:'+IP

    if request.method == 'POST':
        if keys is not None:
            computerdict ={}
            datajson = redisServer.get(keys)
            return HttpResponse(datajson)

    return render(
        request,
        "NiceAdmin/progressInfo.html",
    )




@csrf_exempt
def Register(request):
    if request.method == 'POST':
        postdata = request.POST
        username = postdata.get('name', '')
        password = postdata.get('pwd', '')
        #user = User.objects.get(username__exact=username)
        try:
            user = User.objects.create_user(username, '', password)
            if user:
                # user.is_staff = True
                # user.is_superuser =True
                user.save()
                return HttpResponse(json.dumps({"msg":"true","url":"/login/"}))
        except Exception, e:
            return HttpResponse(json.dumps({"msg":"false"}))
        return HttpResponse(json.dumps({"msg":"false"}))

    return render(
        request,
        "NiceAdmin/register.html",
    )
# Create your views here.
