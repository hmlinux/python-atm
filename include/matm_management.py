#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import time
import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modules import myatm_supperuser
from modules import myatm_accounts
from modules import myatm_creditcard

supper_user = {
    "account": None
}

def supper_user_login(supper_user):
    supper_user_dic = myatm_supperuser.load_supper_user()
    if supper_user["account"] == None:
        while True:
            print("-----------管理员登录-----------")
            username = input("输入管理员帐号: ")
            password = input("输入管理员密码: ")
            if username in supper_user_dic:
                if password == supper_user_dic[username]["password"]:
                    supper_user["account"] = username
                    print("登录成功！")
                    time.sleep(1)
                    return True
                else:
                    print("用户名或密码错误！")
                    return False
            else:
                print("用户名或密码错误！")
                return False
    else:
        return True

def lock_account():
    user_accounts_dic = myatm_accounts.load_account_data()
    print("---------------帐号列表---------------")
    print("帐号说明: 0表示未锁定, 1表示已锁定.")
    for user in user_accounts_dic:
        print("用户名: %s\t\t\t状态: %s" % (user,user_accounts_dic[user]["lock"]))
    print("--------------------------------------")
    while True:
        lock_user = input("输入要锁定的用户名(返回b): ")
        if lock_user == "b":
            break
        if lock_user in user_accounts_dic:
            lock_ = input("锁定用户%s[确定y|n]?" % lock_user)
            if lock_ == "y":
                user_accounts_dic[lock_user]["lock"] = 1
                result = myatm_accounts.update_account_data(user_accounts_dic)
                if result:
                    print("锁定成功！")
                    time.sleep(1)
                    break
            else:
                break
        else:
            print("用户名不存在！")


def unlock_account():
    user_accounts_dic = myatm_accounts.load_account_data()
    print("---------------帐号列表---------------")
    print("帐号说明: 0表示未锁定, 1表示已锁定.")
    for user in user_accounts_dic:
        print("用户名: %s\t\t\t状态: %s" % (user,user_accounts_dic[user]["lock"]))
    print("--------------------------------------")
    while True:
        lock_user = input("输入要解锁的用户名(返回b): ")
        if lock_user == "b":
            break
        if lock_user in user_accounts_dic:
            lock_ = input("解锁用户%s[确定y|n]?" % lock_user)
            if lock_ == "y":
                user_accounts_dic[lock_user]["lock"] = 0
                result = myatm_accounts.update_account_data(user_accounts_dic)
                if result:
                    print("解锁成功！")
                    time.sleep(1)
                    break
            else:
                break
        else:
            print("用户名不存在！")


def account_management():
    prompt = """
    -------------帐号管理-------------
    1.锁定帐号
    2.解锁帐号
    3.返回
    ---------------------------------
    Enter your choice: """
    while True:
        account_option = input(prompt)
        if account_option == "3" or account_option == "b":
            break
        elif account_option == "1":
            lock_account()
        elif account_option == "2":
            unlock_account()


def query_user_creditcard():    #查看信用卡
    creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()

    print("-------------------------------------------信用卡列表------------------------------------------")
    for creditcard in creditcard_data_dic:
        credit_limit = creditcard_data_dic[creditcard]["credit_limit"]
        available_balance = creditcard_data_dic[creditcard]["available_balance"]
        repayment = creditcard_data_dic[creditcard]["repayment"]
        identificationCard = creditcard_data_dic[creditcard]["IdentificationCard"]
        enroll_date = creditcard_data_dic[creditcard]["enroll_date"]
        expire_date = creditcard_data_dic[creditcard]["expire_date"]
        lock_status = creditcard_data_dic[creditcard]["status"]
        print("信用卡卡号:%s  持有人身份证:%s  额度:%s  可用额度:%s\t下月还款:%s\t发行日期:%s\t有效日期:%s\t锁定状态:%s" % \
              (creditcard,identificationCard,credit_limit,available_balance,repayment,enroll_date,expire_date,lock_status))
    print("----------------------------------------------------------------------------------------------")


def modify_creditcard_limit():    #修改信用卡额度
    creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
    prompt = """
--------------------修改额度--------------------
输入信用卡卡号和修改的额度,用空格分隔(返回b): """
    while True:
        ns = input(prompt)
        if ns == "b":
            break
        nslist = ns.split()
        try:
            id, limit = nslist[0], nslist[1]
            if not id.isdigit():
                print("信用卡ID错误!")
            if not limit.isdigit():
                print("额度不正确!")
        except IndexError as diag:
            diag = "输入格式不正确"
            print(diag)
            continue
        if id in creditcard_data_dic:
            Enter = input("确认修改信用卡%s的额度为:%s [确认Y|y]?" % (id,limit))
            if Enter == "Y" or Enter == "y":
                creditcard_data_dic[id]["credit_limit"] = limit
                update = myatm_creditcard.update_bank_creditcard_table(creditcard_data_dic)
                if update:
                    print("修改成功！")
                    time.sleep(1)
                    break
            else:
                break
        else:
            print("信用卡不存在！")

def add_creditcard():    #新增信用卡
    creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
    enroll_date = datetime.date.today()
    expire_date = enroll_date + datetime.timedelta(days=365*4)
    enroll_date = str(enroll_date)
    expire_date = str(expire_date)
    credit_limit = 5000
    available_balance = 5000
    repayment = 0
    pay_day = 22
    status = 0
    IdentificationCard = ""

    prompt = """
-----------------添加信用卡-----------------
说明: 1.信用卡自发行日期起,有效期为4年
      2.信用卡默认额度为5000元
      3.信用卡ID格式: 77779999001

信用卡ID(返回b): """
    while True:
        creditcard_id = input(prompt)
        if creditcard_id == "b":
            return True
        if creditcard_id.isdigit():
            if creditcard_id not in creditcard_data_dic:
                if len(creditcard_id) == 11:
                    break
                else:
                    print("信用卡号为11位数字!")
            else:
                print("信用卡:%s 已存在！" % creditcard_id)
        else:
            print("信用卡格式不正确！")

    print("信用卡%s可用" % creditcard_id)
    while True:
        pay_passwd = input("设置6位数字信用卡密码: ")
        if pay_passwd != "":
            if len(pay_passwd) == 6:
                if pay_passwd.isalnum():
                    break
                else:
                    print("密码为数字或字母组成！")
            else:
                print("密码长度不正确！")
        else:
            print("密码不能为空")
    print("您设置的信用卡密码为:%s " % pay_passwd)

    while True:
        IdentificationCard = input("绑定持有人身份证号码(如: 432100199108081234): ")
        if len(IdentificationCard) != 18:
            continue
        elif not IdentificationCard.isalnum():
            continue
        else:
            break
    print("绑定持有人身份证号码: %s" % IdentificationCard)

    while True:
        print("信用卡:%s  持有人身份证:%s  密码:%s  信用卡额度:%s  生效日期:%s  过期时间:%s" % \
              (creditcard_id,IdentificationCard,pay_passwd,credit_limit,enroll_date,expire_date))
        Enter = input("填写资料通过, 立即提交[确定Y|y]?")
        if Enter == "b":
            break
        if Enter == "Y" or Enter == "y":
            creditcard_info = {"pay_passwd": pay_passwd, "credit_limit": credit_limit, "available_balance": credit_limit, "repayment": 0,
                               "IdentificationCard": IdentificationCard,
                               "enroll_date": enroll_date, "expire_date": expire_date, "pay_day": 22, "status": 0}
            creditcard_data_dic[creditcard_id] = creditcard_info
            print(creditcard_data_dic)
            update = myatm_creditcard.update_bank_creditcard_table(creditcard_data_dic)
            if update:
                print("提交成功！")
                time.sleep(2)
                break
        else:
            break


def lock_creditcard():
    creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
    query_user_creditcard()
    while True:
        creditcard_id = input("输入信用卡卡号(返回b): ")
        if creditcard_id == "b":
            break
        if creditcard_id.isdigit():
            if creditcard_id in creditcard_data_dic:
                Enter = input("确认锁定[Y|y]?")
                if Enter == "Y" or Enter == "y":
                    creditcard_data_dic[creditcard_id]["status"] = 1
                    update = myatm_creditcard.update_bank_creditcard_table(creditcard_data_dic)
                    if update:
                        print("锁定成功！")
                        time.sleep(1)
                        break
                else:
                    break
            else:
                print("信用卡不存在!")
        else:
            print("输入错误!")

def unlock_creditcard():
    creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
    query_user_creditcard()
    while True:
        creditcard_id = input("输入信用卡卡号(返回b): ")
        if creditcard_id == "b":
            break
        if creditcard_id.isdigit():
            if creditcard_id in creditcard_data_dic:
                Enter = input("确认解锁[Y|y]?")
                if Enter == "Y" or Enter == "y":
                    creditcard_data_dic[creditcard_id]["status"] = 0
                    update = myatm_creditcard.update_bank_creditcard_table(creditcard_data_dic)
                    if update:
                        print("解锁成功！")
                        time.sleep(1)
                        break
                else:
                    break
            else:
                print("信用卡不存在!")
        else:
            print("输入错误!")


def creditcard_management():
    prompt = """
    -------------信用卡管理-------------
    1.信用卡查询
    2.修改额度
    3.添加信用卡
    4.冻结信用卡
    5.解锁信用卡
    6.返回
    ---------------------------------
    Enter your choice: """
    while True:
        creditcard_option = input(prompt)
        if creditcard_option == "6" or creditcard_option =="b":
            break
        elif creditcard_option == "1":
            query_user_creditcard()
        elif creditcard_option == "2":
            modify_creditcard_limit()
        elif creditcard_option == "3":
            add_creditcard()
        elif creditcard_option == "4":
            lock_creditcard()
        elif creditcard_option == "5":
            unlock_creditcard()


def matm_management(user_data):    #后台管理
    prompt = """
-------------后台管理-------------
1.帐号管理
2.信用卡管理
3.退出后台
4.返回
---------------------------------
Enter your choice: """
    login = supper_user_login(supper_user)
    if login:
        while True:
            matm_option = input(prompt)
            if matm_option == "1":
                account_management()
            elif matm_option == "2":
                creditcard_management()
            elif matm_option == "3":
                supper_user["account"] = None
                break
            elif matm_option == "4":
                break