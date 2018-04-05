#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modules import myatm_accounts
from modules import myatm_logger

server_logger = myatm_logger.logger("server")

def login_required(func):     #用户登录验证装饰器
    def wrapper(*args, **kwargs):
        if args[0].get('is_authenticated'):
            return func(*args, **kwargs)
        else:
            print("帐号未登录验证！")
    return wrapper

def account_auth(name,passwd):   #登录帐号密码验证
    user_accounts = myatm_accounts.load_account_data()
    if name in user_accounts:
        password = user_accounts[name]['passwd']
        if passwd == password:
            user_data = user_accounts[name]
            return user_data


def new_login(user_data):    #用户登录
    retry_count = 0
    while user_data["is_authenticated"] is not True and retry_count < 3:
        username = input("Username: ").strip()
        if username == "":
            print("用户名不能为空! ")
            continue
        password = input("Password: ").strip()
        account_data = account_auth(username,password)
        if account_data:
            user_data["is_authenticated"] = True
            user_data["account_id"] = username
            user_data["user_data"] = account_data
            print("账号验证成功")
            server_logger.info("%s login authentication success." % username)
            return user_data
        else:
            print("用户名或密码错误！")
            retry_count += 1
    else:
        print("错误次数超过3次!")
        server_logger.error("authentication failed.")

def account_logout(user_data):    #退出登录
    print("退出登录！")
    user_data["account_id"] = None
    user_data["is_authenticated"] = False
    user_data["user_data"] = None
    server_logger.info("logout.")

def forgot_password():       #重置密码
    print("----重置密码----")
    server_logger.info("reset password.")
    retry_count = 0
    while retry_count < 3:
        username = input("请输入你的用户名: ")
        user_accounts_dic = myatm_accounts.load_account_data()
        server_logger.info("加载用户数据")
        if username in user_accounts_dic:
            password = input("请输入新密码: ")
            if password != "":
                password2 = input("再次输入新密码: ")
                if password2 == password:
                    user_accounts_dic[username]['passwd'] = password
                    reset = myatm_accounts.update_account_data(user_accounts_dic)
                    if reset:
                        print("修改成功! 返回登录页面")
                        return True
                else:
                    print("两次输入密码不匹配.")
            else:
                print("密码不能为空")
                retry_count += 1
        elif username == "":
            print("用户名为空! ")
            retry_count += 1
        else:
            print("用户名不存在! ")
            retry_count += 1

def registered_account():    #注册新账户
    print("----注册帐号----")
    server_logger.info("registered account.")
    prompt = "输入您要注册的用户名: "
    user_flag = False
    while True:
        username = input(prompt)
        user_accounts_dic = myatm_accounts.load_account_data()
        if username in user_accounts_dic:
            prompt = "用户名已经存在,请重新输入: "
            continue
        elif username == "":
            prompt = "用户名不能为空,请重新输入: "
            continue
        elif not username.isalnum():
            print("用户名包含特殊字符!")
            prompt = "输入您要注册的用户名: "
            continue
        else:
            user_flag = True
            print("您要注册的新账号: %s" % username)

        prompt = "输入您要设置的密码: "
        passwd_flag = False
        while True:
            password = input(prompt)
            if password != "":
                password2 = input("再次输入您要设置的密码: ")
                if password2 == password:
                    passwd_flag = True
                    break
                else:
                    print("两次输入密码不一致,重新输入!")
            else:
                print("密码不能为空! ")
                break

        print("您注册的帐号为: %s %s (请妥善保管您的帐号密码.)" % (username,password))

        prompt = "请输入11位数字的手机号码(如:13100224466): "
        phone_flag = False
        while True:
            phone = input(prompt).strip()
            phone_len = len(phone)
            if phone.isdigit():
                if phone[0] != "1":
                    prompt = "格式不正确,重新输入(如:13100224466): "
                elif phone_len != 11:
                    prompt = "格式不正确,重新输入: "
                else:
                    phone_flag = True
                    break
            else:
                print("手机号码只能为数字!")
                break

        if user_flag == True and passwd_flag == True and phone_flag == True:
            '''{"name": {"id": 2001, "passwd": "123456", "phone": "13011112221", "IdentificationCard": None, "wallet_balance": 0.0, "pay_passwd": None, "address": None, "lock": 0}}'''
            choice = input("您注册的帐号%s检测通过，确认注册(Yes|No)? " % username)
            if choice == "Yes" or choice == "Y" or choice == "yes" or choice == "y":
                account_id = 2000 + len(user_accounts_dic) + 1
                account = {"id": account_id, "passwd": password, "phone": phone, "IdentificationCard": "", "wallet_balance": 0.0, "pay_passwd": "", "address": "", "lock": 0}
                user_accounts_dic[username] =account
                update = myatm_accounts.update_account_data(user_accounts_dic)
                if update:
                    print("注册成功！")
                    return True
            elif choice == "No" or choice == "N" or choice == "no" or choice == "n":
                break
            else:
                print("资料未提交!")
        break


def account_login(user_data):      #立即登录
    prompt = """
-----登录页面-----
  1. 帐号登录
  2. 忘记密码
  3. 立即注册
  4. 返回首页
------------------
Enter your choice: """
    logout = False
    while True:
        choice = input(prompt)
        if choice == "1":
            Login = new_login(user_data)
            if Login:
                break
        elif choice == "2":
            Reset = forgot_password()
        elif choice == "3":
            Register = registered_account()
        elif choice == "4":
            break







