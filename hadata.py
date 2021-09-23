from flask import request
import socket
import time
import datetime


#获取两个日期中间的日期列表
def gen_dates(b_date, days):
    day = datetime.timedelta(days=1)
    for i in range(days):
        yield b_date + day*i


def get_date_list(user_say_date):
    """
    user_say_date [2,'2021-07-21','2021-07-29'] ,2代不日期。1代表星期
    """
    data = []
    if user_say_date[0] == 1:
        data.append(user_say_date[1])
        return data
    elif user_say_date[0] == 2:
        start = datetime.datetime.strptime(user_say_date[1],"%Y-%m-%d").date()
        end = datetime.datetime.strptime(user_say_date[2], "%Y-%m-%d").date()
        for d in gen_dates(start, (end-start).days):
            data.append(d)
        #最后把日期加入
        data.append(user_say_date[2])
        return data
    else:
        data = []
        return data



def str_Y_M_D():
    """
    格式化时间，返回当前时间%H-%M
    """
    t = time.localtime(time.time())
    strT = time.strftime('%Y-%m-%d', t)
    # %Y-%m-%d-%H-%M-%S  Y 年  m月 d日  H时 M分 S秒
    return str(strT)

def str_Y_M_D_H():
    """
    格式化时间，返回当前时间%H-%M
    """
    t = time.localtime(time.time())
    strT = time.strftime('%Y-%m-%d-%H', t)
    # %Y-%m-%d-%H-%M-%S  Y 年  m月 d日  H时 M分 S秒
    return str(strT)

def str_Y_M_D_H_M_s():
    """
    格式化时间，返回当前时间%H-%M
    """
    t = time.localtime(time.time())
    strT = time.strftime('%Y-%m-%d-%H-%M-%S', t)
    # %Y-%m-%d-%H-%M-%S  Y 年  m月 d日  H时 M分 S秒
    return str(strT)


def send_day_report_mail(cmd, date):
    send_day_report(cmd, date)


def get_test_group():#GET_TEST_GROUP
    init_cmd = '#@#@GGG@#@#'
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(('172.16.20.46', 9000))
    tcp_socket.send(init_cmd.encode('utf-8'))
    tap = tcp_socket.recv(1024 * 2).decode("utf-8")
    try:
        tcp_socket.close()
    except:
        pass
    return tap



def send_cmd(tcp_input,date):
    d = date.split('-')
    year = d[0]
    mon = d[1]
    init_cmd = f"#@#@+++@#@#|-|REPORT{year}|-|{mon}"
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(('172.16.20.46', 9000))
    tcp_socket.send(init_cmd.encode('utf-8'))
    tap = tcp_socket.recv(1024).decode("utf-8")
    tap = tap.split("|-|")
    if len(tap) < 2:
        return False, tap
    if "#@#@+++@#@#" not in tap[0]:
        if "1" not in tap[1]:
            tcp_socket.close()
            return False, tap
    tcp_socket.send(tcp_input.encode('utf-8'))
    tap = tcp_socket.recv(10240*4).decode("utf-8",'ignore')
    tcp_socket.close()
    return True, tap

def is_repeat(name,date,Project):
    # '#@#@555@#@#|-|0|-|list-tab|-|list-key'
    # String get_data = "#@#@555@#@#|-|1|-|name='"+getTesterName+"'|*|Project='"+getTesterProject+"'|*|date='"+geteditText_date+"'";
    cmd = f"#@#@555@#@#|-|1|-|name='{name}'|*|date='{date}'"
    ispass , tap = send_cmd(cmd,date)
    if not ispass:
        return False
    list_tap = tap.split('|-|')
    if "#@#@555@#@#" in list_tap[0]:
        if "0" in list_tap[1]:
            return False
    tap = list_tap[2]
    list_data = tap.replace('),)', "").replace('),', "|-|").replace("(", "").replace(")", "").replace("'", "")
    list_data1 = list_data.split("|-|")
    for x in list_data1:
        y = x.split(",")[2]
        if Project in y:
            return True
    return False

def send_put_day(cmd,date):
    ispass, tap = send_cmd(cmd,date)
    if ispass:
        list_tap = tap.split('|-|')
        if "#@#@123@#@#" in list_tap[0]:
            if "1" in list_tap[1]:
                return True
        return False
    else:
        return False


def send_day_report(cmd,date):
    ispass, tap = send_cmd(cmd, date)
    if not ispass:
        return False
    list_tap = tap.split('|-|')
    if "#@#@DAY@#@#" in list_tap[0]:
        if "1" in list_tap[1]:
            return True
    return False


def send_get_day(cmd,date):
    ispass, tap = send_cmd(cmd,date)
    if ispass:
        list_tap = tap.split('|-|')
        if "#@#@555@#@#" in list_tap[0]:
            if "1" in list_tap[1]:
                return True, list_tap[2]
        return False, None
    else:
        return False, None


def send_del_report(id,date):
    cmd = f'#@#@456@#@#|-|{id}'
    ispass , tap = send_cmd(cmd,date)
    if not ispass:
        return False
    list_tap = tap.split('|-|')
    if "#@#@456@#@#" in list_tap[0]:
        if "1" in list_tap[1]:
            return True
    return False



def get_id():
    id_list = ''
    for i in range(15):
        try:
            id = request.form[f'vehicle{i}']
            id_list += id+","
        except:
            pass
    return id_list


def get_client_data():
    name = request.form['tester']
    date = request.form['start_time']
    count = request.form['count']
    try:
        count = int(count)
    except ValueError:
        count = 1
    # name , date , (list1 , list2)
    if count == 2:
        return name, date, (get_data('1'), get_data('2'))
    elif count == 3:
        return name, date, (get_data('1'), get_data('2'), get_data('3'))
    elif count == 4:
        return name, date, (get_data('1'), get_data('2'), get_data('3'), get_data('4'))
    elif count == 5:
        return name, date, (get_data('1'), get_data('2'), get_data('3'), get_data('4'), get_data('5'))
    elif count == 6:
        return name, date, (get_data('1'), get_data('2'), get_data('3'), get_data('4'), get_data('5'), get_data('6'))
    elif count == 7:
        return name, date, (get_data('1'), get_data('2'), get_data('3'), get_data('4'), get_data('5'), get_data('6'), get_data('7'))
    elif count == 8:
        return name, date, (get_data('1'), get_data('2'), get_data('3'), get_data('4'), get_data('5'), get_data('6'), get_data('7'), get_data('8'))
    else:
        return name, date, (get_data('1'),)


def get_data(id):
    project_1 = request.form[f'project_{id}']
    progress_1 = request.form[f'progress_{id}']
    time_1 = request.form[f'time_{id}']
    task_1 = request.form[f'task_{id}']
    task_1 = str(task_1).replace(",","，")
    introduction_1 = request.form[f'introduction_{id}']
    introduction_1 = str(introduction_1).replace(",", "，")
    remarks_1 = request.form[f'remarks_{id}']
    remarks_1 = str(remarks_1).replace(",", "，")
    
    return project_1, task_1, progress_1, introduction_1, remarks_1, time_1