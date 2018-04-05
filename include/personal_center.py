#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modules.myatm_bankcard import BankcardBaseClass
from modules import myatm_logger
from include.account_auth import forgot_password
from include.account_auth import login_required
from modules import myatm_creditcard
from modules import myatm_accounts

userBankcard = BankcardBaseClass()
server_logger = myatm_logger.logger("server")

def personal_center_menu(user_data):    #个人中心
    account_id = user_data["account_id"]
    phone = user_data["user_data"]["phone"]
    address = user_data["user_data"]["address"]
    identificationcard = user_data["user_data"]["IdentificationCard"]

    if identificationcard == "":
        is_authidentificationcard = "否"
    else:
        is_authidentificationcard = "是"

    user_bankcard_info = userBankcard.user_bankcard_info(account_id)
    user_creditcard_info = myatm_creditcard.load_user_creditcard(account_id)
    if user_bankcard_info != None:
        user_bankcard_list = user_bankcard_info.keys()
        user_bankcard = " ".join(user_bankcard_list)
    else:
        user_bankcard = "无"

    if user_creditcard_info != None:
        user_creditcard_list = user_creditcard_info
        user_creditcard = " ".join(user_creditcard_list)
    else:
        user_creditcard = "无"
    return account_id,phone,address,is_authidentificationcard,identificationcard,user_bankcard,user_creditcard


def personal_info(user_data):    #个人资料
    personal_info = personal_center_menu(user_data)
    info = """
-------------------------------------
            个人资料
用户名      : {0}
手机号      : {1}
收货地址    : {2}
身份验证    : {3}
身份证号码  : {4}
银行卡绑定  : {5}
信用卡绑定  : {6}
-------------------------------------""".format(personal_info[0],personal_info[1],personal_info[2],personal_info[3],personal_info[4],personal_info[5],personal_info[6])
    Enter = input(info)


def auth_identificationcard_num(user,user_data):    #身份证号码登记
    ''''''
    if user_data["user_data"]["IdentificationCard"] == "":
        identificationcard_num = ""
    else:
        identificationcard_num = user_data["user_data"]["IdentificationCard"]

    prompt = """
    ------------------------------
    用户名:     {0}
    身份证号码: {1}
    ------------------------------
    注意: 用户必须进行身份证号码登记后才可以进行购物！
    """.format(user,identificationcard_num)
    print(prompt)

    if identificationcard_num == "":
        user_accounts_dic = myatm_accounts.load_account_data()
        while True:
            choice = input("您未进行身份认证, 是否现在认证(Yes|No)? ")
            if choice == "Yes" or choice == "yes" or choice == "Y" or choice == "y":
                prompt = "输入18位数字身份证号码(格式示例: 456700199210106631): "
                while True:
                    identificationcard_id = input(prompt)
                    if len(identificationcard_id) != 18:
                        identificationcard_id = input(prompt)
                    elif not identificationcard_id.isalnum():
                        identificationcard_id = input(prompt)
                    else:
                        break
                print(identificationcard_id)
                user_accounts_dic[user]["IdentificationCard"] = identificationcard_id
                print(user_accounts_dic)
                update = myatm_accounts.update_account_data(user_accounts_dic)
                if update:
                    print("登记成功！")
                    time.sleep(2)
                    user_data["user_data"] = user_accounts_dic[user]
                    server_logger.info("Authentication identificationcard.")
                    return user_data
            else:
                break
    else:
        choice = input()
        return user_data


def modify_phone(user,user_data):    #修改手机号码
    ''''''
    user_accounts_dic = myatm_accounts.load_account_data()

    prompt = """
    ------------------------------
               手机号码
    用户名:    {0}
    手机号码:  {1}
    ------------------------------""".format(user,user_data["user_data"]["phone"])
    print(prompt)
    while True:
        user_option = input("是否要修改手机号码(Yes|No)? ")
        if user_option == "Yes" or user_option == "yes" or user_option == "Y" or user_option == "y":
            prompt = "请输入11位数字的手机号码: "
            phone_flag = False
            while True:
                new_phone = input(prompt)
                phone_len = len(new_phone)
                if new_phone.isdigit():
                    if new_phone[0] != "1":
                        prompt = "格式不正确,重新输入(如:13100224466): "
                    elif phone_len != 11:
                        prompt = "格式不正确,重新输入: "
                    else:
                        phone_flag = True
                        break
                else:
                    print("手机号码只能为数字!")
            if phone_flag == True:
                select = input("确认修改(Y|n)?")
                if select == "Y" or select == "y":
                    user_accounts_dic[user]["phone"] = new_phone
                    update = myatm_accounts.update_account_data(user_accounts_dic)
                    if update:
                        print("修改成功！")
                        time.sleep(2)
                        user_data["user_data"] = user_accounts_dic[user]
                        server_logger.info("modify phone.")
                        return user_data
                else:
                    break
        else:
            return user_data


def modify_shopping_address(user,user_data):   #修改收货地址
    ''''''
    user_accounts_dic = myatm_accounts.load_account_data()
    prompt = """
        ------------------------------
                   收货地址
        用户名:    {0}
        收货地址:  {1}
        ------------------------------""".format(user, user_data["user_data"]["address"])
    print(prompt)
    while True:
        user_option = input("是否要修改收货地址(y|n)? ")
        if user_option == "Y" or user_option == "y":
            prompt = "请输入您的收货地址: "
            while True:
                address = input(prompt)
                if address != "":
                    select = input("确认修改(y|n)?")
                    if select == "y" or select == "Y":
                        user_accounts_dic[user]["address"] = address
                        update = myatm_accounts.update_account_data(user_accounts_dic)
                        if update:
                            print("修改成功！")
                            time.sleep(2)
                            user_data["user_data"] = user_accounts_dic[user]
                            server_logger.info("modify shopping address.")
                            return user_data
                else:
                    continue
        else:
            return user_data


def binding_bankcard_account(user,user_data):    #银行卡绑定
    ''''''
    user_identificationcard = user_data["user_data"]["IdentificationCard"]
    user_bankcard_info = userBankcard.user_bankcard_info(user)
    while True:
        prompt = """
        ------------------------------
                   银行卡
        """
        print(prompt)

        if user_bankcard_info == None:
            user_bankcard_list = []
        else:
            user_bankcard_list = user_bankcard_info.keys()

        for index,bank in enumerate(user_bankcard_list):
            print("        储蓄卡%s: %s" % (index+1,bank))
        enter = """
        ------------------------------
        (Add)添加银行卡  (Back)返回
        """
        select = input(enter)
        if select == "A" or select == "a":
            while True:
                prompt = "请输入你的银行卡号(如: 66668888001)[返回b]: "
                while True:
                    bankcard_id = input(prompt)
                    if bankcard_id == "b":
                        return True
                    if bankcard_id.isdigit():
                        if bankcard_id in user_bankcard_list:
                            print("不能重复绑定!")
                        elif len(bankcard_id) != 11:
                            print("银行卡号为11位数字!")
                        elif bankcard_id == "":
                            prompt = "请输入你的银行卡号(如: 6666888001): "
                        else:
                            check_result = userBankcard.check_bankcard_id(bankcard_id)
                            if check_result:
                                print("重复绑定!")
                            else:
                                break
                break

            prompt = "输入您的身份证号(必须要和用户帐号已绑定的一致)[返回b]: "
            while True:
                identificationcard_id = input(prompt)
                if identificationcard_id == "b":
                    return True
                if identificationcard_id.isdigit():
                    if identificationcard_id == user_identificationcard:
                        break
                    else:
                        print("与帐号绑定的身份证号码不一致！")
                else:
                    print("格式不正确！")

            prompt = "设置6位数字的支付密码: "
            while True:
                bankcard_pay_pass = input(prompt)
                if bankcard_pay_pass != "":
                    if len(bankcard_pay_pass) == 6:
                        if bankcard_pay_pass.isalnum():
                            break
                        else:
                            print("密码为数字或字母组成！")
                    else:
                        print("密码长度不正确！")
                else:
                    print("密码不能为空")

            bankcard_data_dic = userBankcard.load_bankcard_table()
            bankcard_data = {"pay_passwd": bankcard_pay_pass, "balance": 50000,
                             "IdentificationCard": identificationcard_id, "status": 0}

            if user_bankcard_info == None:
                bankcard_data_dic[user] = {}
                bankcard_data_dic[user][bankcard_id] = bankcard_data
            else:
                bankcard_data_dic[user][bankcard_id] = bankcard_data

            update = userBankcard.update_bankcard_table(bankcard_data_dic)
            if update:
                print("添加成功！")
                server_logger.info("Add binding bankcard success.")
                time.sleep(2)

        if select == "B" or select == "b":
            break


def binding_creditcard_account(user,user_data):    #信用卡绑定
    ''''''
    user_identificationcard = user_data["user_data"]["IdentificationCard"]
    user_creditcard_list = myatm_creditcard.load_user_creditcard(user)
    while True:
        prompt = """
        ------------------------------
                   信用卡
        """
        print(prompt)


        for index,bank in enumerate(user_creditcard_list):
            print("        信用卡%s: %s" % (index+1,bank))
        enter = """
        ------------------------------
        (Add)添加信用卡  (Back)返回
        """
        select = input(enter)
        if select == "A" or select == "a":
            while True:
                prompt = "请输入你的信用卡号(如: 77779999001): "
                while True:
                    creditcard_id = input(prompt)
                    if creditcard_id.isdigit():
                        if creditcard_id in user_creditcard_list:
                            print("不能重复绑定!")
                        elif len(creditcard_id) != 11:
                            print("信用卡号为11位数字!")
                        elif creditcard_id == "":
                            prompt = "请输入你的信用卡号(如: 77779999001): "
                        else:
                            check_result = myatm_creditcard.check_creditcard_bind(user,creditcard_id)
                            if check_result:
                                print("重复绑定!")
                            else:
                                break
                break

            prompt = "输入您的身份证号(必须要和用户帐号已绑定的一致): "
            while True:
                identificationcard_id = input(prompt)
                if identificationcard_id.isdigit():
                    if identificationcard_id == user_identificationcard:
                        break
                    else:
                        print("与帐号绑定的身份证号码不一致！")
                else:
                    print("格式不正确！")

            prompt = "输入6位数字的支付密码: "
            while True:
                creditcard_pay_pass = input(prompt)
                if creditcard_pay_pass != "":
                    if len(creditcard_pay_pass) == 6:
                        if creditcard_pay_pass.isalnum():
                            break
                        else:
                            print("密码为数字或字母组成！")
                    else:
                        print("密码长度不正确！")
                else:
                    print("密码不能为空")

            print(identificationcard_id,creditcard_id,creditcard_pay_pass)
            bank_creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()

            if creditcard_id in bank_creditcard_data_dic:
                bank_creditcard_identificationcard_id = bank_creditcard_data_dic[creditcard_id]["IdentificationCard"]
                bank_creditcard_pay_pass = bank_creditcard_data_dic[creditcard_id]["pay_passwd"]
                bank_creditcard_lock_status = bank_creditcard_data_dic[creditcard_id]["status"]

                if identificationcard_id == bank_creditcard_identificationcard_id:
                    if bank_creditcard_lock_status == 0:
                        if creditcard_pay_pass == bank_creditcard_pay_pass:
                            credit_limit = bank_creditcard_data_dic[creditcard_id]["credit_limit"]
                            available_balance = bank_creditcard_data_dic[creditcard_id]["available_balance"]
                            enroll_date = bank_creditcard_data_dic[creditcard_id]["enroll_date"]
                            expire_date = bank_creditcard_data_dic[creditcard_id]["expire_date"]
                            pay_day = bank_creditcard_data_dic[creditcard_id]["pay_day"]

                            #绑定信用卡
                            bind_creditcard_data = myatm_creditcard.load_bind_creditcard_table()
                            bind_creditcard_data[user] = user_creditcard_list
                            bind_creditcard_data[user].append(creditcard_id)
                            update = myatm_creditcard.update_bind_creditcard_table(bind_creditcard_data)
                            if update:
                                print("添加成功！")
                                print("信用卡: %s  额度: %s  可用额度: %s  还款日期: 每月%s日" % (creditcard_id,credit_limit,available_balance,pay_day))
                                time.sleep(2)
                                server_logger.info("Add binding creditcard success.")
                        else:
                            print("信用卡支付密码错误!")
                    else:
                        print("信用卡状态异常!")
                        server_logger.error("creditcard is locked!")
                else:
                    print("身份证号码不一致!")
            else:
                print("信用卡不存在!")

        if select == "B" or select == "b":
            break

def transaction_history(user):
    print("-----------------------------------交易信息记录-----------------------------------")
    transaction_log_file = os.path.join(base_dir, "logs", "transactions.log")
    with open(transaction_log_file,"r",encoding='utf-8') as transaction_log:
        transaction_info = transaction_log.readlines()
        for line in transaction_info:
            if user in line:
                print(line.strip())
    Enter = input("按任意键继续")

@login_required
def personal_center(user_data):    #个人中心
    # account_id,phone,address,is_authidentificationcard,identificationcard,user_bankcard,user_creditcard
    user_info = personal_center_menu(user_data)
    user = user_data["account_id"]
    prompt = """
----------------------个人中心---------------------------------
1. 个人资料            -------------------------------------
2. 修改密码              用户名      : {0}
3. 修改手机              手机号      : {1}
4. 收货地址              收货地址    : {2}
5. 身份证号              身份验证    : {3}
6. 银行卡绑定            身份证号码  : {4}
7. 信用卡绑定            银行卡绑定  : {5}
8. 账单查询              信用卡绑定  : {6}
9. 返回首页            -------------------------------------
---------------------------------------------------------------
Enter your choice: """.format(user_info[0],user_info[1],user_info[2],user_info[3],user_info[4],user_info[5],user_info[6])
    while True:
        choice = input(prompt)
        if choice == "1":
            personal_info(user_data)
        elif choice == "2":
            forgot_password()
        elif choice == "3":
            modify_phone(user,user_data)
        elif choice == "4":
            modify_shopping_address(user,user_data)
        elif choice == "5":
            auth_identificationcard_num(user,user_data)
        elif choice == "6":
            binding_bankcard_account(user,user_data)
        elif choice == "7":
            binding_creditcard_account(user,user_data)
        elif choice == "8":
            transaction_history(user)
        elif choice == "9" or choice == "b":
            break
