from flask import Flask
from flask import request
from flask import render_template
from hadata import get_client_data,str_Y_M_D ,str_Y_M_D_H ,get_test_group
from hadata import send_get_day , send_day_report,send_cmd,send_day_report_mail
from hadata import send_put_day ,is_repeat ,get_id,send_del_report,get_date_list
import threading
from collections import Counter
from MyExcel import save_cvs, Report
from Log import log


app = Flask(__name__,static_folder='./result')


A_NAME_LIST = '廖林梅,陈慧英,厍志敏,程思,娄新伟,汪国全,苏新新,陈云霞,郭子祥,曹粉粉,段晓杰,康敏,汪唯,薛鹏,张冶,杨侨,邢刚,靳发祥,易花萍,鲍乐,' \
              '王龙,李原原,孙小元,刘栋,孙德晶,杨越,刘莉,张岩,李士华,吴小莲,陈志钢,王玺敏,周文侠,方成,赵凤銮,徐新宇,徐新宇-硬测,' \
              '叶琦,陈蓉,杨晓佳,张明明,陆辰辰,庄春辉,卜书静'

NAME_LIST = A_NAME_LIST.split(',')

A_REPORT_LIST = 'SLM755,SLM757,SLB742,SLM758,SLB748,SLM755L,SLB749,SLB741,SLM752,SLB760,SLM756,SLB761,SLB742W,SLB763,' \
                'SLB765,SLB741W,SLB748W,SLB767,SLB769,SLB781,SLB788,SLB782,SLB783,SLB789,SLB765XQ,SLB761XQ,SLM758W,' \
                'SLM759,SLT187,SLB786,MC510,SLB785,SLB787,SLM900,SLM755LE,SLM300,SLB763P,MC501,MC502,MC503,MC506,' \
                'MC509,MC510,MT511,MT512,MC508,MC513,SLM758S,SLM310,SLM320,SLM500,MC518,MC519,MC521,MC520,MT523,' \
                'MC565X,MC525,MC526,MC528,SLM500S,SLM500QC,SLM500QW,SLM330,MC529,MC901,SRM900,MC902,MC561,MC301,' \
                'MT533,SLM326,MT903,MC531,MC532,SLM328,SLM920,SRM910,MC302,MT303,MT535,MC536,MT537,MC905,MC907,' \
                'MC908,MC329,SLM550,MC538,SLM921,SM130,SLM322,SLM322M,SLM322E,SLM326S,SLM330S,SLM320S,SLM320P,' \
                'SLM320PS,SLM326E,MT906,MC551,SLM320H,SLM326L,MC557,MC582,SRM930,SRM935,MC507,MC541,MC552,' \
                'MC583,MT504,MT545,SNM909,SRM900L,平台EVB项目,非自研项目,预研项目,其它,事假'

@app.route('/')
def my_form():
    ip = request.remote_addr
    log('info', f'主页  {ip} ---- ')
    return render_template("test.html")
    
@app.route('/update.html')
def my_update():
    ip = request.remote_addr
    log('info', f'update  {ip} ---- ')
    return render_template("update.html")

@app.route('/week_report.html')
def week_report_get():
    ip = request.remote_addr
    log('info', f'week_report  {ip} ---- ')
    return render_template("week_report.html")

@app.route('/week_report.html', methods=['POST'])
def week_report():
    error_page = """

                <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="utf-8">
                        <title>错误界面</title>
                        <meta http-equiv="refresh" content="5;url=./">
                    </head>
                    <body align="center">
                        <div style="width: 56%;margin: 0 auto;">

                            <header align="center" >
                                <div align="left" >
                                    <a href="./">
                                        <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                    </a>
                                </div>
                                <div align="center">
                                    <h1>工作报告系统</h1>
                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                </div>
                            </header>


                            <div style="margin: 100px 0px 100px 0px;">


                                <h4 style="color: red;">{0} ，{1}！</h4>
                                <p>5 秒后自动跳转</p>

                            </div>




                            <footer align="center" >
                                <p>美格 · 测试</p>
                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                <p><time 发布日期时间="2021-07-29"></time></p>
                            </footer>

                        </div>
                    </body>
                </html>

    """

    result_page = """
    
                <!DOCTYPE html>
                <html lang="zh">
                    <head>
                        <meta charset="utf-8">
                        <title>周报结论</title>
                        <!--meta http-equiv="refresh" content="5;url=./"-->
                    </head>
                    <body align="center">
                        <div style="width: 56%;margin: 0 auto;">
                
                            <header align="center" >
                                <div align="left" >
                                    <a href="./">
                                        <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                    </a>
                                </div>
                                <div align="center">
                                    <h1>工作报告系统</h1>
                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                </div>
                            </header>
                
                
                            <div style="margin: 100px 0px 100px 0px;">
                
                                <h4 style="color: red;">{0} ，周报已生成！</h4>
                                <a href="{1}" >
                                    <p style="margin: 50px 0px 50px 0px;">点击下载周报</p>
                                </a>
                                <h4 style="color: red;">调整周报显示步骤：</h4>
                                <h5 style="margin: 50px 0px 50px 0px;">1、原始的周报数据，如下图：</h5>
                                <img src="./result/1.png"/>
                                <h5 style="margin: 50px 0px 50px 0px;">2、全选表格数据，并将其设置为自动换行</h5>
                                <h5 style="margin: 50px 0px 50px 0px;">3、拉伸表格宽度使其显示完全</h5>
                                <img src="./result/3.png"/>
                            </div>
                
                
                
                
                            <footer align="center" >
                                <p>美格 · 测试</p>
                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                <p><time 发布日期时间="2021-07-29"></time></p>
                            </footer>
                
                        </div>
                    </body>
                </html>
    
    """


    try:
        name = request.form['tester_check']
        time_start = request.form['check_dep_start_time']
        time_end = request.form['check_dep_end_time']
    except:#信息错误
        return error_page.format('填写的信息错误','请重试！')
    date_js = [2, time_start, time_end]
    list_date = get_date_list(date_js)
    new_data = []
    for x in list_date:
        cmd = f"#@#@555@#@#|-|1|-|name='{name}'|*|date='{x}'"
        isPass, data = send_get_day(cmd, str(x))
        if isPass:
            list_data = data.replace('),)',"").replace('),',"|-|").replace("(","").replace(")","").replace("'","")
            list_data1 = list_data.split("|-|")
            for zz in list_data1:
                new_data.append(zz)
    project = []
    project_time = []
    task = ''
    ranmks = ''
    for x in new_data:
        list_x = x.split(',')
        prtj = list_x[2]
        time = list_x[8]
        tmp_task = str(list_x[4]).replace('\\r\\n','；')#当日起换行处理
        tmp_ranmks = str(list_x[7]).replace('\\r\\n','；')
        task += tmp_task +'\r\n'
        ranmks += tmp_ranmks + '\r\n'
        project.append(prtj)
        project_time.append(f'{prtj},{time}')
    project = list(set(project))
    len_project = len(project)

    new_project_time = []
    for x in project:
        float_x = 0.0
        for y in project_time:
            list_y = y.split(',')
            if x == list_y[0]:
                float_x += float(list_y[1])
        new_project_time.append(f'{x},{float_x}')

    report = Report(name)
    date_time = f'{time_start}\r\n ~ \r\n{time_end}'
    result = report.weekReport(len_project=len_project,task=task,times=date_time,remaks=ranmks,data=new_project_time)
    if result is None:
        return error_page.format('周报生成失败','请重试！')
    return result_page.format(name,result)


@app.route('/', methods=['POST'])
def my_form_post():
    ip = request.remote_addr
    error_page = """
    
                <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="utf-8">
                        <title>错误界面</title>
                        <meta http-equiv="refresh" content="5;url=./">
                    </head>
                    <body align="center">
                        <div style="width: 56%;margin: 0 auto;">
                            
                            <header align="center" >
                                <div align="left" >
                                    <a href="./">
                                        <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                    </a>
                                </div>
                                <div align="center">
                                    <h1>工作报告系统</h1>
                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                </div>
                            </header>
                            
                            
                            <div style="margin: 100px 0px 100px 0px;">
                                
                                
                                <h4 style="color: red;">{0} ，{1}！</h4>
                                <p>5 秒后自动跳转</p>
                                
                            </div>
                            
                            
                            
                            
                            <footer align="center" >
                                <p>美格 · 测试</p>
                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                <p><time 发布日期时间="2021-07-29"></time></p>
                            </footer>
                            
                        </div>
                    </body>
                </html>
    
    """


    is_select = 0


    try:
        project_1 = request.form['my-day']
        is_select = 1
    except:
        try:
            project_1 = request.form['my-get-day']
            is_select = 2
        except:
            try:
                project_1 = request.form['my-mom']
                is_select = 3
            except:
                try:
                    project_1 = request.form['my-del-day']
                    is_select = 4
                except:
                    try:
                        project_1 = request.form['my-get-day-all']
                        is_select = 5
                    except:
                        try:
                            project_1 = request.form['my-get-project-all']
                            is_select = 6
                        except:
                            try:
                                project_1 = request.form['check-put-user']
                                is_select = 7
                            except:
                                try:
                                    project_1 = request.form['my-updata-day']
                                    is_select = 8
                                except:
                                    is_select = 0

    if is_select == 1:#发送日报
        # '#@#@123@#@#|-|name|-|project|-|date|-|task|-|completion|-|introduce|-|remarks|-|time'
        # INSERT_DATA(self,tabName,name,project,time,task,completion,introduce,date=None,remarks='null'):

        REPORT_LIST = A_REPORT_LIST.split(',')
        name, date , list_data = get_client_data()
        log('info',f'发送日报 {ip} ---- {name} ------ {date} ----- {list_data}')
        list_data = str(list_data).replace('),)',"").replace('),',"|-|").replace("(","").replace(")","").replace("'","")
        list_data1 = list_data.split("|-|")
        # (('MC529', '任务简介', '100', '工作简介', '暂无', '8'),)
        len_list = len(list_data1)
        if len(list_data1) == 1:
            list1 = list_data1[0].split(',')
            """
            if is_repeat(name, date, list1[0]):
                return f'<a href="./"><p>error 404,{list1[0]} 提交重复 ，先查询确认后，请删除后再次提交</p></a>'
            """
            project = list1[0].replace(" ","")
            isPass = False
            if project == "其他":
                project = '其它'
            for x in REPORT_LIST:
                if x == project:
                    isPass = True
            if not isPass:
                return error_page.format(f"{project} 名称不正确","请向系统管理员要求新增项目！")
            completion = float(list1[2].replace(" ",""))/100
            time = list1[5].replace(" ","")
            cmd = f"#@#@123@#@#|-|{name}|-|{project}|-|{date}|-|{list1[1]}|-|{completion}|-|{list1[3]}|-|{list1[4]}|-|{time}"
            ispass = send_put_day(cmd,date)
            if not ispass:
                return error_page.format(f"{cmd} 执行失败","请排查输入情况")
        else:
            for x in list_data1:
                list1 = x.split(',')
                """
                if is_repeat(name, date, list1[0]):
                    return f'<a href="./"><p>error 404,{list1[0]} 提交重复 ，先查询确认后，请删除后再次提交</p></a>'
                """
                project = list1[0].replace(" ", "")
                isPass = False
                if project == "其他":
                    project = '其它'
                for y in REPORT_LIST:
                    if y == project:
                        isPass = True
                if not isPass:
                    return error_page.format(f"项目 ：{project} 名称不正确，请重新填写，其它已经提交！","请向系统管理员要求新增项目！")
                completion = float(list1[2].replace(" ", "")) / 100
                time = list1[5].replace(" ", "")
                cmd = f"#@#@123@#@#|-|{name}|-|{project}|-|{date}|-|{list1[1]}|-|{completion}|-|{list1[3]}|-|{list1[4]}|-|{time}"
                ispass = send_put_day(cmd, date)
                if not ispass:
                    return error_page.format(f"{cmd} 执行失败","请排查输入情况")
        # #@#@DAY@#@#|-|name|-|date
        if name == "陈慧英":
            cmd = f'#@#@DAY@#@#|-|{name}|-|{date}|-|1'
        else:
            cmd = f'#@#@DAY@#@#|-|{name}|-|{date}|-|0'
        #ispass = send_day_report(cmd,date)
        t = threading.Thread(target=send_day_report_mail, args=(cmd,date)) #子线程发送邮件
        t.start()
        """
        if not ispass:#TODO 邮件
            return f'<a href="./"><p>error 404, 发送邮件失败 ，请重试</p></a>'
        """
    elif is_select == 2:#查询个人日报
        # '#@#@555@#@#|-|0|-|list-tab|-|list-key'
        # String get_data = "#@#@555@#@#|-|1|-|name='"+getTesterName+"'|*|Project='"+getTesterProject+"'|*|date='"+geteditText_date+"'";
        name = request.form['tester_check']
        date = request.form['check_day_start_time']
        date = str(date)
        log('info', f'查询个人日报 {ip} ---- {name} ------ {date}')
        cmd = f"#@#@555@#@#|-|1|-|name='{name}'|*|date='{date}'"
        isPass , data = send_get_day(cmd,date)
        if isPass:
            list_data = data.replace('),)',"").replace('),',"|-|").replace("(","").replace(")","").replace("'","")
            list_data1 = list_data.split("|-|")
            if len(list_data1) == 1:
                list_data = list_data.split(',')
                del list_data[1]
                del list_data[2]
            else:
                y = ''
                a = 1
                z = len(list_data1)
                for x in list_data1:
                    list1 = x.split(',')
                    del list1[1]
                    del list1[2]
                    if a < z:
                        y += str(list1)+"|-|"
                    else:
                        y += str(list1)
                    a += 1
                list_data = y
            list_data = str(list_data).replace('[','').replace(']','').replace("'","").replace(" ","").replace('\\\\r\\\\n','<br>')

            result1 = """
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset="utf-8">
                            <title></title>
                            <style>
                            .longtext50{
                                width: 18%;
                                white-space: pre-wrap;
                            }
                                
                            .longtext150{
                                width: 25%;
                                white-space: pre-wrap;
                            }
                            
                            .longtext{
                                overflow: hidden;
                                white-space: nowrap;
                                text-overflow: ellipsis;
                            }
                            </style>
                            <script type="text/javascript">
            """
            result2 = f"""
                                var A_REPORT_LIST = '{A_REPORT_LIST}';
                    """
            result3="""
                                var REPORT_LIST = A_REPORT_LIST.split(',');
                                function get_project(){
                                    var x;
                                    for(x in REPORT_LIST){
                                        var name = REPORT_LIST[x];
                                        document.write('<option value="'+name+'">'+name+"</option>");
                                    }
                                }
                                
                                function input_only_project(id){
                                    
                                    var el = document.getElementById(id);
                                    var result = el.value;
                                    var x;
                                    if (result == ''){
                                        return;
                                    }
                                    for (x in REPORT_LIST){
                                        if (result == REPORT_LIST[x]){
                                            return;
                                        }
                                    }
                                    alert(result+" - 项目名称不正确！");
                                }
                            </script>
                        </head>
                        <body align="center">
                            <div style="width: 100%;">
                                
                                <header align="center" >
                                    <div align="left" >
                                        <a href="./">
                                            <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                        </a>
                                    </div>
                                    <div align="center">
                                        <h1>工作报告系统</h1>
                                        <p><time pubdate datetime="2021-07-19"></time></p>
                                    </div>
                                </header>
            """
            result4 = f"""
                    <fieldset>
                        <legend>查询结果 - {name} - {date}</legend>
                            <form action="." method="POST">
                                <input type="text" style="display: none;" value="{date}" name="date"/>
                                <input type="text" style="display: none;" value="{name}" name="name"/>
                                <script type="text/javascript">
                                
                                    var data = "{list_data}";
                            """
            result5 = r"""
                                    var x;
                                    var y;
                                    var z;
                                    var list_data;
                                    list_data = data.split("|-|");
                                    document.write('<div style="display: flex;justify-content: center;">');
                                    document.write('<table border="1" style="width: 100%; table-layout: fixed;word-wrap: normal;word-break: normal;">');
                                    document.write('<tr>')
                                    document.write('<th style="width: 4%;">id</th>');
                                    document.write('<th style="width: 7%;">项目</th>');
                                    document.write('<th class="longtext50">任务</th>');
                                    document.write('<th style="width: 4%;">进度%</th>');
                                    document.write('<th >简介</th>');
                                    document.write('<th class="longtext150">备注</th>');
                                    document.write('<th style="width: 4%;">工时</th>');
                                    document.write('<th style="width: 3%;">选取</th>');
                                    document.write('</tr>');
                                    document.write('<datalist id="source">');
                                    get_project();
                                    document.write("</datalist>")
                                    var iii = 0;
                                    for(y in list_data){
                                        x = list_data[y].split(",");
                                        document.write('<tr>');
                                        var id_name = x[0];
                                        for(z in x){
                                            var ttt = x[z];
                                            var tt = ttt.replace(new RegExp('<br>','g'),'\r\n');
                                            if (z == 0){
                                                document.write("<td align='left'>"+tt+"</td>");
                                            }else if (z == 1){
                                                document.write("<td align='left'>");
                                                document.write('<input list="source" id="ipt'+id_name+'" name="project_'+id_name+'" required="required" style="width: 85%;height: 23px;" value="'+tt+'" onchange="input_only_project('+"'"+'ipt'+id_name+"'"+')"/>');
                                                document.write("</td>");
                                            }else if(z == 2){
                                                document.write("<td align='left'> <textarea rows='4' style='width: 95%;' name='task_"+id_name+"'>"+tt+"</textarea></td>");
                                            }
                                            
                                            else if (z == 3){
                                                var xxx = parseFloat(tt) * 100;
                                                document.write("<td align='left'>");
                                                document.write('<input type="text" name="progress_'+id_name+'" required="required" style="width: 85%;height: 23px;" value="'+xxx+'"  oninput='+'"'+"value=value.replace(/(^\\.|[^\\d\\.])/g,''). replace('.','$#$').replace(/\\./g,'').replace('$#$','.').replace(/^([^1])(\\d)\\d*/, '$1$2').replace(/^1\\d{2,}.*/,'100')"+'"'+'/>');
                                                document.write("</td>");
                                            }else if (z == 4){
                                                
                                                document.write("<td align='left'> <textarea rows='4' style='width: 95%;' name='introduction_"+id_name+"' >"+tt+"</textarea></td>");
                                            }else if(z == 5){
                                                document.write("<td align='left'> <textarea rows='4' style='width: 95%;' name='remarks_"+id_name+"' >"+tt+"</textarea></td>");
                                            }
                                            else{
                                                document.write("<td align='left'>");
                                                document.write('<input type="text" name="time_'+id_name+'" required="required" style="width: 85%;height: 23px;" value="'+tt+'"  oninput='+'"'+"value=value.replace(/(^\\.|[^\\d\\.])/g,''). replace('.','$#$').replace(/\\./g,'').replace('$#$','.').replace(/^([^1])(\\d)\\d*/, '$1$2').replace(/^3\\d.*/,'24').replace(/^2[5-9].*/,'24')"+'"'+'/>');
                                                document.write("</td>");
                                            }
                                        }
                                        document.write("<td>"+'<input type="checkbox" name="vehicle'+iii+'" value="'+id_name+'">'+"</td>");
                                        iii++;
                                        document.write('</tr>');
                                    }
                                    document.write("</table>");
                                    document.write("</div>");
                                </script>
                                <input type="submit" style="margin: 5px 0px 0px 2px;" name="my-updata-day" value="更新选项" />
                                <input type="submit" style="margin: 5px 0px 0px 2px;" name="my-del-day" value="删除选项" />
                            </form>
                    </fieldset>
                    
                    
                    <footer align="center" >
                        <p>美格 · 测试</p>
                        <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                        <p><time 发布日期时间="2021-07-29"></time></p>
                    </footer>
                    
                </div>
            </body>
        </html>
            """

            return result1 + result2 + result3+ result4+ result5
        else:
            return error_page.format(f"未查询到当日提交","请检查是否提交！")
    elif is_select == 3:# #@#@MONTH@#@#|-|mon 发送月报
        date = request.form['start_time']
        log('info', f'发送月报 {ip} ----- {date} ')
        ispass = True
        try:
            d = date.split('-')
            mon = d[1]
            cmd = f'#@#@MONTH@#@#|-|{mon}'
            #ispass , tap = send_cmd(cmd,date)
            year = int(d[0])
            momy = int(d[1])
            if year > 2030:
                ispass = False
            elif year < 2021:
                ispass = False
            elif momy < 1:
                ispass = False
            elif momy > 12:
                ispass = False
            else:
                t = threading.Thread(target=send_cmd, args=(cmd,date)) #子线程发送邮件
                t.start()
        except:
            ispass = False
        mon_result = f"""
                    <!DOCTYPE html>
                        <html>
                            <head>
                                <meta charset="utf-8">
                                <title>月报</title>
                                <meta http-equiv="refresh" content="5;url=./">
                            </head>
                            <body align="center">
                                <div style="width: 56%;margin: 0 auto;">

                                    <header align="center" >
                                        <div align="left" >
                                            <a href="./">
                                                <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                            </a>
                                        </div>
                                        <div align="center">
                                            <h1>工作报告系统</h1>
                                            <p><time pubdate datetime="2021-07-19"></time></p>
                                        </div>
                                    </header>


                                    <div style="margin: 100px 0px 100px 0px;">


                                        <h4 style="color: forestgreen;">{mon} 月  报发送成功!</h4>
                                        <p>5 秒后自动跳转</p>

                                    </div>




                                    <footer align="center" >
                                        <p>美格 · 测试</p>
                                        <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                        <p><time 发布日期时间="2021-07-29"></time></p>
                                    </footer>

                                </div>
                            </body>
                        </html>
        """

        if ispass:
            return mon_result
        else:
            return error_page.format(f"日期 {date} 所在月份 查询失败","向管理员反馈此问题。")
    elif is_select == 4:# '#@#@456@#@#|-|id' 删除个人日报

        del_result = """
        
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset="utf-8">
                            <title>删除界面</title>
                            <meta http-equiv="refresh" content="5;url=./">
                        </head>
                        <body align="center">
                            <div style="width: 56%;margin: 0 auto;">
                                
                                <header align="center" >
                                    <div align="left" >
                                        <a href="./">
                                            <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                        </a>
                                    </div>
                                    <div align="center">
                                        <h1>工作报告系统</h1>
                                        <p><time pubdate datetime="2021-07-19"></time></p>
                                    </div>
                                </header>
                                
                                
                                <div style="margin: 100px 0px 100px 0px;">
                                    
                                    
                                    <h4 style="color: red;">{0}！</h4>
                                    <p>5 秒后自动跳转</p>
                                    
                                </div>
                                
                                
                                
                                
                                <footer align="center" >
                                    <p>美格 · 测试</p>
                                    <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                    <p><time 发布日期时间="2021-07-29"></time></p>
                                </footer>
                                
                            </div>
                        </body>
                    </html>
                            
        """

        data = get_id()
        date = request.form['date']
        list_data = data.split(',')
        log('info', f'删除个人日报 {ip} ---- {data} ------ {date} ')
        for x in list_data:
            try:
                int_x = int(x)
                ispass = send_del_report(int_x,date)
                if not ispass:
                    return error_page.format(f"删除 {int_x} 执行失败","向管理员反馈此问题。")
            except ValueError:
                pass
        return del_result.format(f"ID {list_data}已删除成功！")
    elif is_select == 5:#部门日报
        date = request.form['check_dep_start_time']
        log('info', f'部门日报 {ip} -------- {date} ')
        isALL = False
        try:
            date_end = request.form['check_dep_end_time']
            list_date_end = date_end.split('-')
            if len(list_date_end) == 3:
                isALL = True
        except:
            pass

        # GET_TEST_GROUP = '#@#@GGG@#@#' #获取分组

        # TODO 获取分组
        test_group = get_test_group()
        # print(test_group)
        test_group = eval(test_group)#转化为字典


        if not isALL: # 非区间
            cmd = f"#@#@555@#@#|-|1|-|date='{date}'"
            isPass, data = send_get_day(cmd, date)
            if isPass:
                list_data = data.replace('),)', "").replace('),', "|-|").replace("(", "").replace(")", "").replace("'", "")
                list_data1 = list_data.split("|-|")
                if len(list_data1) == 1:
                    list_data = list_data.split(',')
                    del list_data[1]
                    del list_data[2]
                else:
                    y = ''
                    a = 1
                    z = len(list_data1)
                    for x in list_data1:
                        list1 = x.split(',')
                        del list1[0]
                        del list1[2]
                        if a < z:
                            y += str(list1) + "|-|"
                        else:
                            y += str(list1)
                        a += 1
                    list_data = y
                list_data = str(list_data).replace('[', '').replace(']', '').replace("'", "").replace('\\\\r\\\\n','<br>')

                list_data = list_data.split('|-|')

                html_data = []

                len_group = len(test_group)
                split_list = '*'
                for x in range(len_group):
                    test_name = test_group[f'GROUP_{x+1}'].split(',')
                    test_name_str = split_list.join(test_name)
                    #html_data.append(f'----,-----,-----------,0,----{test_name_str}-----,------------,----')
                    for y in test_name:
                        for z in list_data:
                            list_z_name = z.split(',')[0]
                            if y in list_z_name:
                                html_data.append(z)
                split_list = '|-|'

                html_text = split_list.join(html_data)

                result1 = """
                        <!DOCTYPE html>
                            <html>
                                <head>
                                    <meta charset="utf-8">
                                    <title></title>
                                    <style>
                                    .longtext50{
                                        width: 18%;
                                        white-space: pre-wrap;
                                    }
                                    
                                    .longtext150{
                                        width: 25%;
                                        white-space: pre-wrap;
                                    }
    
                                    .longtext{
                                        overflow: hidden;
                                        white-space: nowrap;
                                        text-overflow: ellipsis;
                                    }
                """
                result2 = f"""
                                    </style>
                                </head>
                                <body align="center">
                                    <div style="width: 100%;">
    
                                        <header align="center" >
                                            <div align="left" >
                                                <a href="./">
                                                    <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                                </a>
                                            </div>
                                            <div align="center">
                                                <h1>工作报告系统</h1>
                                                <p><time pubdate datetime="2021-07-19"></time></p>
                                            </div>
                                        </header>
    
    
                                        <fieldset>
                                            <legend>查询结果 - 部门日报 - {date}</legend>
                                                <form action="." method="POST">
                                                    <input type="text" style="display: none;" value="{date}" name="date"/>
                                                    <script type="text/javascript">
    
                                                        var data = "{html_text}";
                                """
                result3 = """
                                                        var x;
                                                        var y;
                                                        var z;
                                                        var list_data;
                                                        list_data = data.split("|-|");
                                                        document.write('<div style="display: flex;justify-content: center;">');
                                                        document.write('<table border="1" style="width: 100%; table-layout: fixed;word-wrap: normal;word-break: normal;">');
                                                        document.write('<tr>');
                                                        document.write('<th style="width: 4%;">姓名</th>');
                                                        document.write('<th style="width: 5%;">项目</th>');
                                                        document.write('<th class="longtext50">任务</th>');
                                                        document.write('<th style="width: 3%;">进度%</th>');
                                                        document.write('<th >简介</th>');
                                                        document.write('<th class="longtext150">备注</th>');
                                                        document.write('<th style="width: 4%;">工时</th>');
                                                        document.write('</tr>');
                                                        var iii = 0;
                                                        for(y in list_data){
                                                            x = list_data[y].split(",");
                                                            var name_test = x[0];
                                                            if ('----' == name_test){
                                                                document.write('<tr style="background: #FABF8F;">');
                                                            }else{
                                                                document.write('<tr>');
                                                            }
                                                            
                                                            for(z in x){
                                                                if (z == 3){
                                                                    var xxx = parseFloat(x[z]) * 100;
                                                                    document.write("<td align='left'>"+xxx+"</td>");
                                                                }else{
                                                                    document.write("<td align='left'>"+x[z]+"</td>");
                                                                }
                                                            }
                                                            iii++;
                                                            document.write('</tr>');
                                                        }
                                                        document.write("</table>");
                                                        document.write("</div>");
                                                    </script>
                                                </form>
                                        </fieldset>
    
    
                                        <footer align="center" >
                                            <p>美格 · 测试</p>
                                            <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                            <p><time 发布日期时间="2021-07-29"></time></p>
                                        </footer>
    
                                    </div>
                                </body>
                            </html>
                """

                return result1 + result2 + result3
            else:
                return error_page.format(f"当日未查询到数据", "请稍后查询")
        else:
            test_data = [2, date, date_end]
            list_date = get_date_list(test_data)
            list_data_ov = ''
            list_date_ov = ''
            isGo = True
            for xx in list_date:
                cmd = f"#@#@555@#@#|-|1|-|date='{xx}'"

                isPass, data = send_get_day(cmd, str(xx))

                if data is not None:
                    if isPass:
                        list_data = data.replace('),)', "").replace('),', "|-|").replace("(", "").replace(")","").replace("'", "")
                        list_data1 = list_data.split("|-|")
                        if len(list_data1) == 1:
                            list_data = list_data.split(',')
                            del list_data[1]
                            del list_data[2]
                        else:
                            y = ''
                            a = 1
                            z = len(list_data1)
                            for x in list_data1:
                                list1 = x.split(',')
                                del list1[0]
                                del list1[2]
                                if a < z:
                                    y += str(list1) + "|-|"
                                else:
                                    y += str(list1)
                                a += 1
                            list_data = y
                        list_data = str(list_data).replace('[', '').replace(']', '').replace("'", "")
                    if isGo:
                        list_data_ov = list_data + "|*|"
                        list_date_ov = str(xx) + "|*|"
                        isGo = False
                    else:
                        list_data_ov += list_data + "|*|"
                        list_date_ov += str(xx) + "|*|"
                else:
                    pass
            list_data_ov += "****"
            list_date_ov += "****"
            list_data_ov = list_data_ov.replace("|*|****", "").replace(" ","").replace('\\\\r\\\\n','<br>')
            list_date_ov = list_date_ov.replace("|*|****", "").replace(" ","").replace('\\\\r\\\\n','<br>')


            list_data = list_data_ov.split('|*|')

            html_data = []

            len_group = len(test_group)
            split_list = '*'

            split_list_1 = '|-|'

            split_list_2 = '|*|'

            html_data_big = []

            for a in list_data:
                list_a = a.split("|-|")
                for x in range(len_group):
                    test_name = test_group[f'GROUP_{x + 1}'].split(',')
                    test_name_str = split_list.join(test_name)
                    #html_data.append(f'----,-----,-----------,0,----{test_name_str}-----,------------,----')
                    for y in test_name:
                        for z in list_a:
                            list_z_name = z.split(',')[0]
                            if y in list_z_name:
                                html_data.append(z)
                html_str = split_list_1.join(html_data)
                html_data_big.append(html_str)






                html_text = split_list_2.join(html_data_big)


            dap_top = """
            
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset="utf-8">
                            <title></title>
                            <style>
                            .longtext50{
                                width: 18%;
                                white-space: pre-wrap;
                            }
                            
                            .longtext150{
                                width: 25%;
                                white-space: pre-wrap;
                            }
                    
                            .longtext{
                                overflow: hidden;
                                white-space: nowrap;
                                text-overflow: ellipsis;
                            }
                    
                            </style>
                        </head>
            """

            dap_mid = f"""
                        <body align="center">
                            <div style="width: 100%;">
                    
                                <header align="center" >
                                    <div align="left" >
                                        <a href="./">
                                            <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                        </a>
                                    </div>
                                    <div align="center">
                                        <h1>工作报告系统</h1>
                                        <p><time pubdate datetime="2021-07-19"></time></p>
                                    </div>
                                </header>
                    
                                <script type="text/javascript">
                                    var list_date = "{list_date_ov}";
                                    var data = "{html_text}";
                                    var list_data;
                                    var list_date_new;
                                    var f;
                                    list_data = data.split("|*|");
                                    list_date_new = list_date.split("|*|");
            """

            dap_end = """
                                    for(f in list_date_new){
                                        document.write('<fieldset>')
                                            document.write('<legend >查询结果 - 部门日报 - '+list_date_new[f]+'</legend>')
                                                var x;
                                                var y;
                                                var z;
                                                var new_data;
                                                var new_list_data;
                                                new_data = list_data[f];
                                                new_list_data = new_data.split("|-|");
                                                document.write('<div style="display: flex;justify-content: center;">');
                                                document.write('<table border="1" style="width: 100%; table-layout: fixed;word-wrap: normal;word-break: normal;">');
                                                document.write('<tr>');
                                                document.write('<th style="width: 4%;">姓名</th>');
                                                document.write('<th style="width: 5%;">项目</th>');
                                                document.write('<th class="longtext50">任务</th>');
                                                document.write('<th style="width: 3%;">进度%</th>');
                                                document.write('<th >简介</th>');
                                                document.write('<th class="longtext150">备注</th>');
                                                document.write('<th style="width: 4%;">工时</th>');
                                                document.write('</tr>');
                                                for(y in new_list_data){
                                                    x = new_list_data[y].split(",");
                                                    
                                                    var name_test = x[0];
                                                    if ('----' == name_test){
                                                        document.write('<tr style="background: #FABF8F;">');
                                                    }else{
                                                        document.write('<tr>');
                                                    }
                                                     
                                                    for(z in x){
                                                        if (z == 3){
                                                            var xxx = parseFloat(x[z]) * 100;
                                                            document.write("<td align='left'>"+xxx+"</td>");
                                                        }else{
                                                            document.write("<td align='left'>"+x[z]+"</td>");
                                                        }
                                                    }
                                                    document.write('</tr>');
                                                }
                                                document.write("</table>");
                                                document.write("</div>");
                                        document.write("</fieldset>");
                                        document.write('<hr style="margin: 20px 0px 20px 0px;" />');
                                        
                                    }
                                </script>
                                <footer align="center" >
                                    <p>美格 · 测试</p>
                                    <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                    <p><time 发布日期时间="2021-07-29"></time></p>
                                </footer>
                    
                            </div>
                        </body>
                    </html>
            
            """


            return dap_top + dap_mid + dap_end
    elif is_select == 6:# #@#@PROJECTALL@#@#|-|project 项目总览

        project_result = """
        
                        <!DOCTYPE html>
                            <html>
                                <head>
                                    <meta charset="utf-8">
                                    <title>项目总结</title>
                                    <style>
                                    .longtext50{
                                        width: 18%;
                                        white-space: pre-wrap;
                                    }
                                    
                                    .longtext150{
                                        width: 25%;
                                        white-space: pre-wrap;
                                    }
                                    
                                    .longtext{
                                        overflow: hidden;
                                        white-space: nowrap;
                                        text-overflow: ellipsis;
                                    }
                                    
                                    </style>
                                </head>
                                <body align="center">
                                    <div style="width: 100%;">
                                        
                                        <header align="center" >
                                            <div align="left" >
                                                <a href="./">
                                                    <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                                </a>
                                            </div>
        """


        project_1 = request.form['project_check']
        date = str_Y_M_D()
        cmd = f'#@#@PROJECTALL@#@#|-|{date}|-|{project_1}'
        ispass , data = send_cmd(cmd,date)
        list_data = data.split("|-|")
        log('info', f'项目总览 {ip} -------- {project_1} ')
        if "1" not in list_data[1]:
            return error_page.format(f"{project_1} 项目总结失败","向管理员反馈此问题。")
        new_data = list_data[2].replace('),)', "").replace("(", "").replace("'", "").replace('),', "|-|").replace(' ', "").replace('))', "").replace('\\r\\n', "<br>")
        if not ispass:
            return error_page.format(f"{project_1} 总结失败！","向管理员反馈此问题。")

        end_result = f"""
                                        <fieldset>
                                            <legend>查询结果 - {project_1} - 项目总结</legend>
                                                    <script type="text/javascript">

                                                        var data = "{new_data}";
                                                        var x;
                                                        var y;
                                                        var z;
                                                        var list_data;
                                                        list_data = data.split("|-|");
                                                        document.write('<div style="display: flex;justify-content: center;">')
                                                        document.write('<table border="1" style="width: 100%; table-layout: fixed;word-wrap: normal;word-break: normal;">')
                                                        document.write('<tr>')
                                                        document.write('<th style="width: 4%;">id</th>')
                                                        document.write('<th style="width: 4%;">姓名</th>')
                                                        document.write('<th style="width: 5%;">项目</th>')
                                                        document.write('<th style="width: 8%;">日期</th>')
                                                        document.write('<th class="longtext50">任务</th>')
                                                        document.write('<th style="width: 3%;">进度%</th>')
                                                        document.write('<th >简介</th>')
                                                        document.write('<th class="longtext150">备注</th>')
                                                        document.write('<th style="width: 4%;">工时</th>')
                                                        document.write('</tr>')
        """
        new_data_1 = "id,姓名,项目,日期,任务,进度,简介,备注,工时|-|" + new_data
        list_new_data = new_data_1.split("|-|")
        path = save_cvs(project_1,str_Y_M_D_H(),list_new_data)

        end_end = """
                                                        for(y in list_data){
                                                            x = list_data[y].split(",");
                                                            document.write('<tr>')
                                                            for(z in x){
                                                                if (z == 5){
                                                                    var xxx = parseFloat(x[z]) * 100;
                                                                    document.write("<td align='left'>"+xxx+"</td>")
                                                                }else{
                                                                    document.write("<td align='left'>"+x[z]+"</td>")
                                                                }
                                                            }
                                                            document.write('</tr>')
                                                        }
                                                        document.write("</table>")
                                                        document.write("</div>")
                                                    </script>
                                        </fieldset>
                    """


        if path is None:

            top_1 = """
                                                <div align="center">
                                                    <h1>项目总结</h1>
                                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                                </div>
                                            </header>

            """

            end_end_1 = """

                                            <footer align="center" >
                                                <p>美格 · 测试</p>
                                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                                <p><time 发布日期时间="2021-07-29"></time></p>
                                            </footer>

                                        </div>
                                    </body>
                                </html>

            """
        else:

            top_1 = f"""
                                                <div align="center">
                                                    <h1>项目总结</h1>
                                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                                    <a href="{path}">
                                                        <p>下载 csv 格式文档</p>
                                                    </a>
                                                </div>
                                            </header>

            """

            end_end_1 = f"""

                                            <footer align="center" >
                                                <a href="{path}">
                                                    <p>下载 csv 格式文档</p>
                                                </a>
                                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                                <p><time 发布日期时间="2021-07-29"></time></p>
                                            </footer>

                                        </div>
                                    </body>
                                </html>

            """

        return project_result + top_1 + end_result + end_end + end_end_1
    elif is_select == 7:#查询未提交日报人员

        date = request.form['check_put-user_time']
        cmd = f"#@#@555@#@#|-|1|-|date='{date}'"
        isPass, data = send_get_day(cmd, date)
        log('info', f'查询未提交日报人员 {ip} ----- {date} ')
        if isPass:
            list_data1 = data.replace('),)', "").replace('),', "|-|").replace("(", "").replace(")", "").replace("'", "")
            list_data = ''
            isStrat = True
            for x in NAME_LIST:
                if x not in list_data1:
                    if isStrat:
                        list_data = f'{x}'
                        isStrat = False
                    else:
                        list_data = f'{list_data}|-|{x}'


            result1 = """
                    <!DOCTYPE html>
                        <html>
                            <head>
                                <meta charset="utf-8">
                                <title></title>
                                <style>
                                .longtext50{
                                    overflow: hidden;
                                    white-space: nowrap;
                                    text-overflow: ellipsis;
                                    width: 50px;
                                }

                                .longtext150{
                                    overflow: hidden;
                                    white-space: nowrap;
                                    text-overflow: ellipsis;
                                    width: 150px;
                                }

                                .longtext{
                                    overflow: hidden;
                                    white-space: nowrap;
                                    text-overflow: ellipsis;
                                }
            """
            result2 = f"""
                                </style>
                            </head>
                            <body align="center">
                                <div style="width: 56%;margin: 0 auto;">

                                    <header align="center" >
                                        <div align="left" >
                                            <a href="./">
                                                <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                            </a>
                                        </div>
                                        <div align="center">
                                            <h1>工作报告系统</h1>
                                            <p><time pubdate datetime="2021-07-19"></time></p>
                                        </div>
                                    </header>


                                    <fieldset>
                                        <legend>查询结果 - 尚未提交日报人员 - {date}</legend>
                                            <form action="." method="POST">
                                                <input type="text" style="display: none;" value="{date}" name="date"/>
                                                <script type="text/javascript">

                                                    var data = "{list_data}";
                            """
            result3 = """
                                                    var x;
                                                    var y;
                                                    var z;
                                                    var list_data;
                                                    list_data = data.split("|-|");
                                                    document.write('<div style="display: flex;justify-content: center;">')
                                                    document.write('<table border="1">')
                                                    document.write('<tr>')
                                                    document.write('<th class="longtext50">姓名</th>')
                                                    document.write('</tr>')
                                                    var iii = 0;
                                                    for(y in list_data){
                                                        document.write('<tr>')
                                                        document.write("<td class='longtext'>"+list_data[y]+"</td>")
                                                        document.write('</tr>')
                                                    }
                                                    document.write("</table>")
                                                    document.write("</div>")
                                                </script>
                                            </form>
                                    </fieldset>


                                    <footer align="center" >
                                        <p>美格 · 测试</p>
                                        <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                        <p><time 发布日期时间="2021-07-29"></time></p>
                                    </footer>

                                </div>
                            </body>
                        </html>
            """

            return result1 + result2 + result3
        else:
            return error_page.format(f"当日尚未有任何人提交日报", "稍后再来查询吧")

    elif is_select == 8:#更新个人日报
        # '#@#@789@#@#|-|id|-|name|-|project|-|date|-|task|-|completion|-|introduce|-|remarks|-|time'
        id_data = get_id()
        date = request.form['date']
        name = request.form['name']
        list_id = id_data.split(',')
        log('info', f'更新个人日报 {ip} -----{name}--- {date}-----{id_data} ')
        for x in list_id:
            try:
                int(x)
                project = request.form[f'project_{x}']
                task = request.form[f'task_{x}']
                task = str(task).replace(",","，")
                progress = request.form[f'progress_{x}']
                progress = float(progress)/100
                introduction = request.form[f'introduction_{x}']
                introduction = str(introduction).replace(",", "，")
                remarks = request.form[f'remarks_{x}']
                remarks = str(remarks).replace(",", "，")
                time = request.form[f'time_{x}']
                cmd = f'#@#@789@#@#|-|{x}|-|{name}|-|{project}|-|{date}|-|{task}|-|{progress}|-|{introduction}|-|{remarks}|-|{time}'
                isPass, tap = send_cmd(cmd, date)
                if not isPass:
                    return error_page.format(f"更新 id {x} 未成功", "向管理员反馈此问题。")
            except ValueError:
                pass
        return error_page.format(f"id {id_data} 更新完成", "")
    else:
        log('info', f'未知指令错误 {ip} ---- ')
        return error_page.format("未知指令错误","向管理员反馈此问题。")


    result = """
            <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="utf-8">
                        <title>日报结果</title>
                        <meta http-equiv="refresh" content="5;url=./">
                        
                        <style>
                        .longtext50{
                            width: 18%;
                            white-space: pre-wrap;
                        }
                                    
                        .longtext150{
                            width: 25%;
                            white-space: pre-wrap;
                        }
          
                        </style>
                        
                    </head>
    """
    mid = f"""
                    <body align="center">
                        <div style="width: 100%">
                            
                            <header align="center" >
                                <div align="left" >
                                    <a href="./">
                                        <img src="https://www.meigsmart.com/userfiles/images/2020/03/23/2020032311354713.png" style="width: 200px;" alt="上海·美格" />
                                    </a>
                                </div>
                                <div align="center">
                                    <h1>工作报告系统</h1>
                                    <p><time pubdate datetime="2021-07-19"></time></p>
                                </div>
                            </header>
                            
                            
                            <fieldset>
                                <legend>提交结果 - {name} - {date}</legend>
                                    <script type="text/javascript">
                                    
                                        var data = "{list_data}";
    """
    end = """
                                        var x;
                                        var y;
                                        var z;
                                        var list_data;
                                        list_data = data.split("|-|");
                                        document.write('<div style="display: flex;justify-content: center;">')
                                        document.write('<table border="1" style="width: 100%; table-layout: fixed;word-wrap: normal;word-break: normal;">')
                                        document.write('<tr>')
                                        document.write('<th style="width: 6%;">项目</th>')
                                        document.write('<th class="longtext50">任务</th>')
                                        document.write('<th style="width: 3%;">进度%</th>')
                                        document.write('<th>简介</th>')
                                        document.write('<th class="longtext150">备注</th>')
                                        document.write('<th style="width: 4%;">工时</th>')
                                        document.write('</tr>')
                                        for(y in list_data){
                                            x = list_data[y].split(",");
                                            document.write('<tr>')
                                            for(z in x){
                                                document.write("<td>"+x[z]+"</td>")
                                            }
                                            document.write('</tr>')
                                        }
                                        document.write("</table>")
                                        document.write("</div>")
                                    </script>
                            </fieldset>
                            
                            <div style="margin: 100px 0px 100px 0px;">
                            <p style="color: red;">5 秒后自动跳转</p>
                            </div>


                            <footer align="center" >
                                <p>美格 · 测试</p>
                                <p><dfn><abbr title="发布时间：2021-09-18">版本：v1.50</abbr><a href="./update.html">更新日志</a></dfn></p>
                                <p><time 发布日期时间="2021-07-29"></time></p>
                            </footer>

                        </div>
                    </body>
                </html>
    """

    return result +mid+ end


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5770)