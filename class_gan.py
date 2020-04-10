from time import sleep
from selenium import webdriver
import requests

requests.packages.urllib3.disable_warnings()  # 预防报错抛出


# 登录函数并且获取登录cookies
def login(userid, passd, wd):
    cookies = {}  # cookie字典
    wd.get('https://www.mosoteach.cn/web/index.php?c=passport')
    username = wd.find_element_by_id('account-name')
    password = wd.find_element_by_id('user-pwd')
    login1 = wd.find_element_by_id('login-button-1')
    username.send_keys(userid)
    password.send_keys(passd)
    login1.click()
    all_cookie = wd.get_cookies()
    for cookie_list in all_cookie:
        cookies.update({cookie_list["name"]: cookie_list["value"]})
    return cookies


# 打开对应课程
def open_class(name_class, wd):
    try:
        for url in wd.find_elements_by_class_name('class-info-subject'):
            if url.text == name_class:
                wd.execute_script("arguments[0].click();", url)  # 进入链接
    except:
        for url in wd.find_elements_by_class_name('class-info-subject'):
            if url.text == name_class:
                wd.execute_script("arguments[0].click();", url)  # 进入链接


# 查找所有课程名称
def find_all_class(wd):
    class_name = []  # 所有课程名称
    for url in wd.find_elements_by_class_name('class-info-subject'):
        class_name.append(url.text)
    return class_name


# ppt word url  播放函数
def look_url(wd):
    wd.switch_to.window(wd.window_handles[1])
    wd.close()
    wd.switch_to.window(wd.window_handles[0])


# POST图片
def POST_image(tre, cookies, wd):
    file_id = tre.get_attribute('data-value')  # 当前资源唯一地址id
    clazz_course_id = wd.find_element_by_css_selector('[name = clazz_course_id]').get_attribute('value')  # 当前房间地址id
    data = {'clazz_course_id': clazz_course_id, 'file_id': file_id, 'type': 'VIEW'}
    index = requests.post('https://www.mosoteach.cn/web/index.php?c=res&m=request_url_for_json', verify=False,
                          cookies=cookies, data=data)
    index.encoding = index.apparent_encoding  # 网页转码utf8


# POST音频
def POST_audio(tre, cookies, wd):
    file_id = tre.get_attribute('data-value')  # 当前资源唯一地址id
    clazz_course_id = wd.find_element_by_css_selector('[name = clazz_course_id]').get_attribute('value')  # 当前房间地址id
    data = {'clazz_course_id': clazz_course_id, 'file_id': file_id, 'type': 'VIEW'}
    index = requests.post('https://www.mosoteach.cn/web/index.php?c=res&m=request_url_for_json', verify=False,
                          cookies=cookies, data=data)
    index.encoding = index.apparent_encoding  # 网页转码utf8


# POST服务器视频观看进度
def POST_video(tre, cookies, wd):
    number = "0123456789."
    video_time = ""
    res_id = tre.get_attribute('data-value')  # 当前资源唯一地址id
    clazz_course_id = wd.find_element_by_css_selector('[name = clazz_course_id]').get_attribute('value')  # 当前房间地址id
    get_video_time = tre.find_element_by_xpath(".//div[4]//span[3]").text  # 视频时间
    # 提取视频时间并且转换为浮点
    for son_get_video_time in get_video_time:
        if son_get_video_time in number:
            video_time = video_time + son_get_video_time
    video_time = float(video_time)
    watch_to = video_time * 60 + 2
    duration = video_time * 60 + 3
    data = {'clazz_course_id': clazz_course_id, 'res_id': res_id, 'watch_to': watch_to, 'duration': duration,
            'current_watch_to': 20}
    index = requests.post('https://www.mosoteach.cn/web/index.php?c=res&m=save_watch_to', verify=False,
                          cookies=cookies, data=data)
    index.encoding = index.apparent_encoding  # 网页转码utf8
    print("网页请求状态：", index.text)
    print("video_time:", video_time)
    print("watch_to:", watch_to)
    print("duration:", duration)


# 干掉当前资源
def gan_class(name, cookies, wd):
    for tre in name.find_elements_by_class_name('res-row-open-enable'):
        swiper = tre.find_element_by_css_selector('[data-is-drag]').get_attribute('data-is-drag')  # 资源看过还是没看过
        classwork_name = tre.find_element_by_class_name('res-name').text  # 资源名称
        element = tre.get_attribute('data-mime')  # 资源链接类型
        if swiper == 'N':
            if element == 'mosoink' or element == 'application':
                if ('.zip' in classwork_name) or ('.exe' in classwork_name) or ('.swf' in classwork_name) or (
                        '.graphml' in classwork_name) or ('.rtf' in classwork_name) or ('.rar' in classwork_name):
                    pass
                else:
                    wd.execute_script("arguments[0].click();", tre)  # 进入链接
                    sleep(0.1)
                    style = wd.find_element_by_class_name('pop-tips-box').get_attribute('style')
                    if 'block' in style:
                        sleep(0.2)
                        wd.find_element_by_class_name('tips-ok').click()
                    else:
                        look_url(wd)
            elif element == 'video':
                POST_video(tre, cookies, wd)
                print(classwork_name)
            elif element == 'image':
                POST_image(tre, cookies, wd)
            elif element == 'audio':
                POST_audio(tre, cookies, wd)


# 打开资源并且折叠课程
def open_fold_class(cookies, wd):
    try:
        lala = wd.find_element_by_class_name('select-role-bg').get_attribute('style')
    except:
        wd.refresh()
        print("错误")
    if 'block' in lala:
        wd.find_element_by_class_name('select-role-bg').find_element_by_class_name('select-role-student').click()
    wd.find_element_by_partial_link_text('资源').click()  # 打开资源
    js = "window.scrollTo(100,9999);"
    wd.execute_script(js)  # 执行JavaScript代码
    for name in wd.find_elements_by_class_name('res-row-box '):
        no_look = int(name.find_element_by_xpath(".//span[3]").text)  # 多少资源没看
        switch = name.find_element_by_class_name('hide-div').get_attribute('data-status')  # 看过没
        chick_switch = name.find_element_by_class_name('slidedown-button')  # 点击展开位置
        muluname = name.find_element_by_class_name('res-group-name').text
        if no_look != 0:
            print("有东西看", muluname)
            if switch == 'N':
                chick_switch.click()
                gan_class(name, cookies, wd)
            else:
                gan_class(name, cookies, wd)
        else:
            print("没有东西看", muluname)


def shuake(username, password):
    i = 0
    wd = webdriver.Chrome(r'chromedriver.exe')  # 自动化浏览器路径
    wd.implicitly_wait(1)  # 超时两秒
    cookies = login(username, password, wd)
    class_name = find_all_class(wd)
    print(class_name, cookies)
    print("一共有这么多", len(class_name))
    for one in class_name:
        print("=================================当前===================================")
        print(i, '/', len(class_name), ":", one)
        i = i + 1
        try:
            open_class(one, wd)
            open_fold_class(cookies, wd)
        except:
            open_class(one, wd)
            open_fold_class(cookies, wd)
        wd.get('https://www.mosoteach.cn/web/index.php?c=clazzcourse&m=index')
    print("----------------------------------所有完成----------------------------------------")
    wd.quit()


shuake('输入用户名', '输入密码')