# /usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modules import myatm_logger
from include.account_auth import login_required
from modules import myatm_creditcard
from modules import myatm_accounts
from modules.myatm_bankcard import userBankcard
from include.personal_center import binding_bankcard_account

server_logger = myatm_logger.logger("server")
transaction_logger = myatm_logger.logger("transaction")

commission_charge = {
    "wallet_withdrawal_rate": 0.01, "wallet_transfers_rate": 0.01,
    "creditcard_withdrawal_rate": 0.05, "creditcard_transfers_rate": 0.05
}

def set_wallet_pay_passwd(user_data):
    pay_passwd = user_data["user_data"]["pay_passwd"]
    if pay_passwd == "":
        print("您还没有设置支付密码！")
        result = False
        while True:
            passwd1 = input("设置支付密码(6位数字): ")
            if passwd1.isdigit():
                if len(passwd1) == 6:
                    passwd2 = input("确认支付密码(6位数字): ")
                    if passwd2.isdigit():
                        if passwd1 == passwd2:
                            result = True
                            time.sleep(1)
                            break
                        else:
                            print("密码不一致！")
                    else:
                        print("密码格式不正确！")
                else:
                    print("支付密码为6位数字")
            else:
                print("密码格式不正确！")
        print(passwd1)
        pay_passwd = passwd1
        user_data["user_data"]["pay_passwd"] = pay_passwd
        account_data_dic = myatm_accounts.load_account_data()
        account_data_dic[user_data["account_id"]]["pay_passwd"] = pay_passwd
        update_account_info = myatm_accounts.update_account_data(account_data_dic)
        if update_account_info:
            print("设置成功！")
            return user_data
    else:
        return user_data

def bankcard_pay_way(user,user_data,recharge_money):  # 银行卡支付
    user_bankcard = userBankcard.user_bankcard_info(user)
    user_bankcard_list = list(user_bankcard.keys())
    retry_pay_pass = True
    while retry_pay_pass:
        print("\n(选择付款银行卡[B返回])")
        for index, value in enumerate(user_bankcard_list):
            print("银行卡%s %s" % (index, value))
        select_bankcard = input("Enter your choice: ")

        if select_bankcard == "B" or select_bankcard == "b":
            break
        if select_bankcard.isdigit():
            select_bankcard = int(select_bankcard)
            if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                bankcard = user_bankcard_list[select_bankcard]
                print(bankcard)
                pay_passwd = user_bankcard[bankcard]["pay_passwd"]
                bankcard_balance = user_bankcard[bankcard]["balance"]

                retry_passwd = 0
                while retry_passwd < 3:
                    passwd = input("输入银行卡支付密码: ")
                    if passwd == pay_passwd:
                        print("银行卡余额: %s" % bankcard_balance)
                        if recharge_money <= bankcard_balance:
                            print("充值金额: %s" % recharge_money)
                            wallet_balance = recharge_money + user_data["user_data"]["wallet_balance"]  # 充值后钱包余额

                            bankcard_data_dic = userBankcard.load_bankcard_table()  # 加载银行卡数据
                            bankcard_balance = bankcard_data_dic[user_data["account_id"]][bankcard][
                                "balance"]  # 读取余额
                            bankcard_balance = bankcard_balance - recharge_money  # 支付后剩余
                            print("剩余: %s" % bankcard_balance)
                            bankcard_data_dic[user_data["account_id"]][bankcard]["balance"] = bankcard_balance
                            update = userBankcard.update_bankcard_table(bankcard_data_dic)
                            if update:
                                print("从银行卡扣款成功！")

                                # print("充值后钱包余额: %s" % wallet_balance)
                                user_data["user_data"]["wallet_balance"] = wallet_balance
                                account_data_dic = myatm_accounts.load_account_data()
                                account_data_dic[user_data["account_id"]]["wallet_balance"] = wallet_balance
                                update_account_info = myatm_accounts.update_account_data(account_data_dic)
                                if update_account_info:
                                    print("支付成功！返回...")
                                    transaction_logger.info("用户:%s 银行卡:%s 交易类型:普通支付 交易扣款:%s 余额:%s 交易结果: 成功" % (user,bankcard,recharge_money,bankcard_balance))
                                    time.sleep(2)
                                    return user_data
                        else:
                            print("银行卡余额不足！")
                            transaction_logger.info(
                                "用户:%s 银行卡:%s 交易类型:普通支付 交易扣款:%s 余额:%s 交易结果: 失败, 余额不足" % (user,bankcard, recharge_money, bankcard_balance))
                            break
                    else:
                        retry_passwd += 1
                        print("密码有误！")
                else:
                    print("错误次数超过3次！")
                    retry_pay_pass = False
            else:
                print("找不到银行卡！")
        else:
            print("输入银行卡序号")


def creditcard_pay_way(user,user_data,recharge_money):  # 信用卡支付
    user_creditcard = myatm_creditcard.load_user_creditcard(user)
    user_creditcard_list = user_creditcard
    retry_pay_pass = True
    while retry_pay_pass:
        print("\n(选择付款信用卡[B返回])")
        for index, value in enumerate(user_creditcard_list):
            print("信用卡%s %s" % (index, value))
        select_creditcard = input("Enter your choice: ")

        if select_creditcard == "B" or select_creditcard == "b":
            break
        if select_creditcard.isdigit():
            select_creditcard = int(select_creditcard)
            if select_creditcard >= 0 and select_creditcard < len(user_creditcard_list):
                creditcard_id = user_creditcard_list[select_creditcard]
                print(creditcard_id)
                #加载信用卡接口
                bank_creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()

                if creditcard_id in bank_creditcard_data_dic:
                    creditcard_lock_status = bank_creditcard_data_dic[creditcard_id]["status"]
                    if creditcard_lock_status == 0:
                        creditcard_pay_pass = bank_creditcard_data_dic[creditcard_id]["pay_passwd"]
                        credit_limit = bank_creditcard_data_dic[creditcard_id]["credit_limit"]
                        available_balance = bank_creditcard_data_dic[creditcard_id]["available_balance"]
                        repayment = bank_creditcard_data_dic[creditcard_id]["repayment"]
                        enroll_date = bank_creditcard_data_dic[creditcard_id]["enroll_date"]
                        expire_date = bank_creditcard_data_dic[creditcard_id]["expire_date"]
                        pay_day = bank_creditcard_data_dic[creditcard_id]["pay_day"]

                        retry_passwd = 0
                        while retry_passwd < 3:
                            passwd = input("输入信用卡支付密码: ")
                            if passwd == creditcard_pay_pass:
                                print("信用卡可用额度: %s" % available_balance)
                                if recharge_money <= available_balance:
                                    print("充值金额: %s" % recharge_money)
                                    wallet_balance = recharge_money + user_data["user_data"]["wallet_balance"]  # 充值后钱包余额
                                    available_balance = available_balance - recharge_money  # 支付后信用卡剩余

                                    repayment = repayment + recharge_money
                                    print("剩余: %s" % available_balance)

                                    bank_creditcard_data_dic[creditcard_id]["available_balance"] = available_balance
                                    bank_creditcard_data_dic[creditcard_id]["repayment"] = repayment

                                    update = myatm_creditcard.update_bank_creditcard_table(bank_creditcard_data_dic)
                                    if update:
                                        print("从信用卡扣款成功！")
                                        # print("充值后钱包余额: %s" % wallet_balance)
                                        user_data["user_data"]["wallet_balance"] = wallet_balance
                                        account_data_dic = myatm_accounts.load_account_data()
                                        account_data_dic[user_data["account_id"]]["wallet_balance"] = wallet_balance
                                        update_account_info = myatm_accounts.update_account_data(account_data_dic)
                                        if update_account_info:
                                            print("支付成功！返回")
                                            transaction_logger.info("用户:%s 信用卡:%s 交易类型:普通支付 交易扣款:%s 余额:%s 交易结果: 成功" % (
                                            user,creditcard_id, recharge_money,available_balance))
                                            time.sleep(2)
                                            return user_data
                                else:
                                    print("信用卡余额不足！")
                                    transaction_logger.info("用户:%s 信用卡:%s 交易类型:普通支付 交易扣款:%s 余额:%s 交易结果: 失败, 余额不足" % (
                                        user,creditcard_id, recharge_money, available_balance))
                                    break
                            else:
                                retry_passwd += 1
                                print("密码有误！")
                        else:
                            print("错误次数超过3次！")
                            retry_pay_pass = False
                    else:
                        print("信用卡已被冻结！")
                else:
                    print("找不到信用卡！")
            else:
                print("输入信用卡序号")


def request_withdrawal(user,user_data,commission_charge):  # 余额提现至银行卡
    ''''''
    user_data = set_wallet_pay_passwd(user_data)
    wallet_withdrawal_rate = commission_charge["wallet_withdrawal_rate"]  # 提现手续费
    withdrawal_prompt = """
    --------------提现--------------
          申请余额提现至银行卡
    Notice: 申请余额提现手续费为0.01
    (请在下面输入提现金额[B返回])
    提现金额: """
    while True:
        withdrawal_money = input(withdrawal_prompt)
        if withdrawal_money == "B" or withdrawal_money == "b":
            return user_data
        try:
            withdrawal_money = float(withdrawal_money)
        except ValueError as diag:
            print("请输入正确的金额!")
            continue

        wallet_balance = user_data["user_data"]["wallet_balance"]  # 取出钱包的剩余的金额
        pay_passwd = user_data["user_data"]["pay_passwd"]  # 读取支付密码

        user_bankcard = userBankcard.user_bankcard_info(user)
        user_bankcard_list = list(user_bankcard.keys())
        while True:
            print("\n(选择提现到银行卡[B返回])")
            for index, value in enumerate(user_bankcard_list):
                print("银行卡%s %s" % (index, value))
            select_bankcard = input("Enter your choice: ")
            if select_bankcard == "b" or select_bankcard == "B":
                return user_data
            if select_bankcard.isdigit():
                select_bankcard = int(select_bankcard)
                if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                    bankcard = user_bankcard_list[select_bankcard]
                    print(bankcard)
                    bankcard_balance = user_bankcard[bankcard]["balance"]

                    retry_passwd = 0
                    while retry_passwd < 3:
                        passwd = input("输入支付密码: ")
                        if passwd == pay_passwd:
                            print("钱包金额: %s" % wallet_balance)
                            print("提现金额: %s" % withdrawal_money)
                            if withdrawal_money <= wallet_balance:
                                wallet_balance = wallet_balance - withdrawal_money
                                service_charge = withdrawal_money * wallet_withdrawal_rate
                                wallet_balance = wallet_balance - service_charge
                                print("提现手续费: %s" % service_charge)

                                print("提现后钱包剩余: %s" % wallet_balance)
                                print("银行卡余额: %s" % bankcard_balance)
                                bankcard_balance = bankcard_balance + withdrawal_money
                                print("提现到账后银行卡余额: %s" % bankcard_balance)

                                bankcard_data_dic = userBankcard.load_bankcard_table()  # 加载银行卡数据
                                bankcard_data_dic[user_data["account_id"]][bankcard][
                                    "balance"] = bankcard_balance  # 更新余额

                                update = userBankcard.update_bankcard_table(bankcard_data_dic)
                                if update:
                                    user_data["user_data"]["wallet_balance"] = wallet_balance  # 钱包余额
                                    account_data_dic = myatm_accounts.load_account_data()  # 加载帐号信息
                                    account_data_dic[user_data["account_id"]][
                                        "wallet_balance"] = wallet_balance  # 更新钱包余额
                                    update_account_info = myatm_accounts.update_account_data(account_data_dic)
                                    if update_account_info:
                                        print("提现成功！")
                                        transaction_logger.info("用户:%s 交易类型:余额提现 提现金额:%s 手续费:%s 余额:%s 交易结果: 成功" % (
                                        user,withdrawal_money,service_charge,wallet_balance))
                                        time.sleep(2)
                                        return user_data
                            else:
                                print("钱包余额不足！")
                                transaction_logger.info("用户:%s 交易类型:余额提现 提现金额:%s 余额:%s 交易结果: 失败,余额不足" % (
                                    user, withdrawal_money,wallet_balance))
                                return user_data
                        else:
                            retry_passwd += 1
                            print("支付密码不正确！")
                    else:
                        print("支付密码错误超过3次！")
                        return user_data
                else:
                    print("找不到银行卡！")
            else:
                print("请选择提现到账的银行卡！")


def wallet_recharge(user,user_data):  # 钱包充值
    ''''''
    recharge_prompt = """
    -------------充值中心-------------
    注意: 单次最多只能充值10000.00(元)
    (请在下面输入充值金额[B返回])
    充值金额: """

    while True:
        recharge_money = input(recharge_prompt)  # 充值金额
        try:
            if recharge_money == "B" or recharge_money == "b" or recharge_money == "q" or recharge_money == "Q":
                return user_data
            recharge_money = float(recharge_money)
            print("%.2f" % recharge_money)
        except ValueError as diag:
            print("请输入正确的金额!")
            continue

        if recharge_money <= 10000:
            while True:
                pay_way = """
    --------选择支付方式--------
    1.银行卡
    2.信用卡
    3.返回
    ---------------------------
    Enter your choice: """
                choice = input(pay_way)
                if choice == "1":
                    bankcard_pay_way(user,user_data,recharge_money)
                elif choice == "2":
                    creditcard_pay_way(user,user_data,recharge_money)
                elif choice == "3":
                    break
                else:
                    continue
        else:
            print("超出限额")


def transfer_to_account(user,user_data,commission_charge):   #钱包转账到用户
    wallet_transfers_rate = commission_charge["wallet_transfers_rate"]
    prompt = "输入转账金额(元): "
    while True:
        transfer_money = input(prompt)
        if transfer_money == "b":
            break
        try:
            transfer_money = float(transfer_money)
            print("%.2f" % transfer_money)
        except ValueError as diag:
            print("请输入正确的金额!")
            continue

        while True:
            transfer_username = input("请输入对方收款账号名: ")
            if transfer_username == "b":
                break
            Test = myatm_accounts.check_account_id(transfer_username)
            if Test:
                if transfer_username == user:
                    print("不能转给自己！")
                    continue
            else:
                print("账号不存在！")
                continue

            print("转账给账号: %s" % transfer_username)
            while True:
                prompt = """
    选择扣款方式:
    1.余额
    2.银行卡
    Enter your choice: """
                transfer_way = input(prompt)
                if transfer_way == "3":
                    break
                elif transfer_way == "1":  # 从余额中转出
                    wallet_balance = user_data["user_data"]["wallet_balance"]  # 取出钱包的剩余的金额
                    pay_passwd = user_data["user_data"]["pay_passwd"]  # 读取支付密码
                    print("钱包余额: %s" % wallet_balance)

                    retry_passwd = 0
                    while retry_passwd < 3:
                        passwd = input("输入支付密码: ")
                        if passwd == pay_passwd:
                            if transfer_money <= wallet_balance:
                                print("从余额转出: %s" % transfer_money)
                                break
                            else:
                                print("余额不足！1")
                                return False
                        else:
                            print("支付密码错误！")
                            retry_passwd += 1
                    else:
                        print("支付失败！2")
                        return False

                    service_charge = transfer_money * wallet_transfers_rate
                    print("扣除手续费: %s" % service_charge)

                    deduct = transfer_money + service_charge
                    wallet_balance = wallet_balance - deduct
                    print("%s转出后钱包金额: %s" % (user, wallet_balance))
                    user_data["user_data"]["wallet_balance"] = wallet_balance  # 钱包余额

                    account_data_dic = myatm_accounts.load_account_data()  # 加载帐号信息

                    transfer_username_wallet_balance = account_data_dic[transfer_username]["wallet_balance"]
                    transfer_username_wallet_balance = transfer_username_wallet_balance + transfer_money
                    print("%s账号钱包金额: %s" % (transfer_username, transfer_username_wallet_balance))

                    account_data_dic[user]["wallet_balance"] = wallet_balance  # 更新转出账号的钱包余额
                    account_data_dic[transfer_username][
                        "wallet_balance"] = transfer_username_wallet_balance  # 更新转入账号的钱包余额
                    update_account_info = myatm_accounts.update_account_data(account_data_dic)
                    if update_account_info:
                        print("转出成功！")
                        transaction_logger.info("用户:%s 交易类型:转账 转账金额:%s 收入账户:%s 余额:%s 交易结果: 成功" % (
                            user,transfer_money,transfer_username,wallet_balance))
                        time.sleep(2)
                        return user_data

                elif transfer_way == "2":  # 从银行卡转出
                    user_bankcard = userBankcard.user_bankcard_info(user)
                    user_bankcard_list = list(user_bankcard.keys())
                    while True:
                        print("\n(选择扣款银行卡[B返回])")
                        for index, value in enumerate(user_bankcard_list):
                            print("银行卡%s %s" % (index, value))
                        select_bankcard = input("Enter your choice: ")

                        if select_bankcard.isdigit():
                            select_bankcard = int(select_bankcard)
                            if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                                bankcard = user_bankcard_list[select_bankcard]
                                print(bankcard)
                                pay_passwd = user_bankcard[bankcard]["pay_passwd"]
                                bankcard_balance = user_bankcard[bankcard]["balance"]
                                print("银行卡余额: %s" % bankcard_balance)

                                retry_passwd = 0
                                while retry_passwd < 3:
                                    passwd = input("输入银行卡支付密码: ")
                                    if passwd == pay_passwd:
                                        if transfer_money <= bankcard_balance:
                                            print("从银行卡转出: %s" % transfer_money)
                                            break
                                        else:
                                            print("余额不足！1")
                                            return False
                                    else:
                                        print("支付密码错误！")
                                        retry_passwd += 1
                                else:
                                    print("支付失败！2")
                                    return False

                                print("转出金额: %s" % transfer_money)

                                service_charge = transfer_money * wallet_transfers_rate
                                print("扣除手续费: %s" % service_charge)

                                deduct = transfer_money + service_charge
                                new_bankcard_balance = bankcard_balance - deduct

                                print("转出后银行卡剩余: %s" % new_bankcard_balance)

                                account_data_dic = myatm_accounts.load_account_data()  # 加载帐号信息

                                transfer_username_wallet_balance = account_data_dic[transfer_username]["wallet_balance"]
                                transfer_username_wallet_balance = transfer_username_wallet_balance + transfer_money
                                print("%s账号钱包金额: %s" % (transfer_username, transfer_username_wallet_balance))

                                account_data_dic[transfer_username][
                                    "wallet_balance"] = transfer_username_wallet_balance  # 更新转入账号的钱包余额
                                update_account_info = myatm_accounts.update_account_data(account_data_dic)
                                if update_account_info:
                                    bankcard_data_dic = userBankcard.load_bankcard_table()  # 加载银行卡数据
                                    bankcard_data_dic[user][bankcard]["balance"] = new_bankcard_balance
                                    update = userBankcard.update_bankcard_table(bankcard_data_dic)
                                    if update:
                                        print("转出成功！")
                                        time.sleep(2)
                                        transaction_logger.info("用户:%s 转出银行卡%s 交易类型:转账 转账金额:%s 收入账户:%s 余额:%s 交易结果: 成功" % (
                                            user,bankcard,transfer_money,transfer_username,new_bankcard_balance))
                                        return user_data


def transfer_to_bankcard(user,user_data,commission_charge):   #转账到银行卡
    ''''''
    wallet_transfers_rate = commission_charge["wallet_transfers_rate"]
    prompt = "输入转账金额(元): "
    while True:
        transfer_money = input(prompt)
        if transfer_money == "b":
            break
        try:
            transfer_money = float(transfer_money)
            print("%.2f" % transfer_money)
        except ValueError as diag:
            print("请输入正确的金额!")
            continue

        while True:
            bankcard_id = input("请输入对方收款银行卡: ")
            if bankcard_id == "b":
                break
            elif bankcard_id.isdigit():
                Test = userBankcard.check_bankcard_id(bankcard_id)
                if Test:
                    user_bankcard = userBankcard.user_bankcard_info(user)
                    if bankcard_id in user_bankcard:
                        print("不能转到给自己已绑定的银行卡！")
                        continue
            else:
                print("请输入对方银行卡号！")
                continue

            print("转账到银行卡: %s" % bankcard_id)

            transfer_username = []
            bankcard_data_dic = userBankcard.load_bankcard_table()
            users = bankcard_data_dic.keys()
            for name in users:
                for i in bankcard_data_dic[name]:
                    if i == bankcard_id:
                        transfer_username.append(name)
                        break

            print(transfer_username[0],bankcard_id)
            while True:
                prompt = """
        选择扣款方式:
        1.余额
        2.银行卡
        Enter your choice: """
                transfer_way = input(prompt)
                if transfer_way == "3":
                    break
                elif transfer_way == "1":  # 从余额中转出
                    wallet_balance = user_data["user_data"]["wallet_balance"]  # 取出钱包的剩余的金额
                    pay_passwd = user_data["user_data"]["pay_passwd"]  # 读取支付密码
                    print("钱包余额: %s" % wallet_balance)

                    retry_passwd = 0
                    while retry_passwd < 3:
                        passwd = input("输入支付密码: ")
                        if passwd == pay_passwd:
                            if transfer_money <= wallet_balance:
                                print("从余额转出: %s" % transfer_money)
                                break
                            else:
                                print("余额不足！1")
                                return False
                        else:
                            print("支付密码错误！")
                            retry_passwd += 1
                    else:
                        print("支付失败！2")
                        return False

                    service_charge = transfer_money * wallet_transfers_rate
                    print("扣除手续费: %s" % service_charge)

                    deduct = transfer_money + service_charge
                    wallet_balance = wallet_balance - deduct
                    print("%s转出后钱包金额: %s" % (user_data["account_id"], wallet_balance))
                    user_data["user_data"]["wallet_balance"] = wallet_balance  # 钱包余额
                    account_data_dic = myatm_accounts.load_account_data()  # 加载帐号信息
                    account_data_dic[user_data["account_id"]]["wallet_balance"] = wallet_balance  # 更新转出账号的钱包余额
                    update_account_info = myatm_accounts.update_account_data(account_data_dic)
                    if update_account_info:
                        # 更新对方银行卡余额
                        #bankcard_data_dic = userBankcard.load_bankcard_table()
                        transfer_username_bankcard_balance = bankcard_data_dic[transfer_username[0]][bankcard_id][
                            "balance"]
                        bankcard_data_dic[transfer_username[0]][bankcard_id][
                            "balance"] = transfer_money + transfer_username_bankcard_balance
                        update = userBankcard.update_bankcard_table(bankcard_data_dic)
                        if update:
                            print("转出成功！")
                            transaction_logger.info("用户:%s 交易类型:转账 转账金额:%s 手续费:%s 收入银行卡:%s 钱包余额:%s 交易结果: 成功" % (
                                user,transfer_money,service_charge,bankcard_id,wallet_balance))
                            time.sleep(2)
                            return user_data

                elif transfer_way == "2":  # 从银行卡转出
                    user_bankcard = userBankcard.user_bankcard_info(user)
                    user_bankcard_list = list(user_bankcard.keys())
                    while True:
                        print("\n(选择扣款银行卡[B返回])")
                        for index, value in enumerate(user_bankcard_list):
                            print("银行卡%s %s" % (index, value))
                        select_bankcard = input("Enter your choice: ")

                        if select_bankcard.isdigit():
                            select_bankcard = int(select_bankcard)
                            if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                                pay_bankcard = user_bankcard_list[select_bankcard]
                                print(pay_bankcard)
                                pay_passwd = user_bankcard[pay_bankcard]["pay_passwd"]
                                bankcard_balance = user_bankcard[pay_bankcard]["balance"]
                                print("银行卡余额: %s" % bankcard_balance)

                                retry_passwd = 0
                                while retry_passwd < 3:
                                    passwd = input("输入银行卡支付密码: ")
                                    if passwd == pay_passwd:
                                        if transfer_money <= bankcard_balance:
                                            print("从银行卡转出: %s" % transfer_money)
                                            break
                                        else:
                                            print("余额不足！1")
                                            return False
                                    else:
                                        print("支付密码错误！")
                                        retry_passwd += 1
                                else:
                                    print("支付失败！2")
                                    return False

                                print("转出金额: %s" % transfer_money)

                                service_charge = transfer_money * wallet_transfers_rate
                                print("扣除手续费: %s" % service_charge)

                                deduct = transfer_money + service_charge
                                new_bankcard_balance = bankcard_balance - deduct

                                print("转出后银行卡剩余: %s" % new_bankcard_balance)

                                bankcard_data_dic = userBankcard.load_bankcard_table()
                                transfer_username_bankcard_balance = bankcard_data_dic[transfer_username[0]][bankcard_id]["balance"]
                                transfer_username_bankcard_balance = transfer_username_bankcard_balance + transfer_money
                                print("转账到对方银行卡到账后金额: %s" % (transfer_username_bankcard_balance))
                                bankcard_data_dic[user][pay_bankcard]["balance"] = new_bankcard_balance  # 转出银行卡的余额
                                bankcard_data_dic[transfer_username[0]][bankcard_id]["balance"] = transfer_username_bankcard_balance  # 转入银行卡的余额
                                update = userBankcard.update_bankcard_table(bankcard_data_dic)
                                if update:
                                    print("转出成功！")
                                    time.sleep(2)
                                    transaction_logger.info("用户:%s 转出银行卡:%s 交易类型:转账 转账金额:%s 手续费:%s 收入银行卡:%s 余额:%s 交易结果: 成功" % (
                                        user,pay_bankcard,transfer_money,service_charge,bankcard_id,new_bankcard_balance))
                                    return user_data


def transfer_accounts(user,user_data,commission_charge):
    ''''''
    transfer_prompt = """
    -----------------转账-----------------
    转账说明:
        ①不能转给自己
        ②仅支持从余额或已绑定的银行卡中转出
        ③转账手续费为0.01

    1.转出到对方账户
    2.转出到对方银行卡
    3.返回
    --------------------------------------
    Enter your choice: """

    while True:
        transfer_option = input(transfer_prompt)
        if transfer_option == "3" or transfer_option == "b":
            break
        elif transfer_option == "1":
            transfer_to_account(user,user_data,commission_charge)
        elif transfer_option == "2":
            transfer_to_bankcard(user,user_data,commission_charge)


def creditcard_repayment(user,creditcard):
    ''''''
    creditcard_id = creditcard[0]
    credit_limit = creditcard[1]
    available_balance = creditcard[2]
    repayment = creditcard[3]
    repay_prompt = """
    -----------还款-----------
    还款信息:
    信用卡: {0}
    下月应还: {1}
    可用额度: {2}
    信用额度: {3}
    1.还款
    2.返回
    --------------------------
    Enter your choice: """.format(creditcard_id, repayment, available_balance, credit_limit)
    while True:
        repay_option = input(repay_prompt)
        if repay_option == "2":
            break
        elif repay_option == "1":
            user_bankcard = userBankcard.user_bankcard_info(user)
            user_bankcard_list = list(user_bankcard.keys())
            while True:
                print("\n(选择还款银行卡[B返回])")
                for index, value in enumerate(user_bankcard_list):
                    print("银行卡%s %s" % (index, value))
                select_bankcard = input("Enter your choice: ")

                if select_bankcard.isdigit():
                    select_bankcard = int(select_bankcard)
                    if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                        bankcard = user_bankcard_list[select_bankcard]
                        print(bankcard)
                        pay_passwd = user_bankcard[bankcard]["pay_passwd"]
                        bankcard_balance = user_bankcard[bankcard]["balance"]
                        print("银行卡余额: %s" % bankcard_balance)

                        retry_passwd = 0
                        while retry_passwd < 3:
                            passwd = input("输入银行卡支付密码: ")
                            if passwd == pay_passwd:
                                if repayment <= bankcard_balance:
                                    print("从银行卡扣款: %s" % repayment)
                                    break
                                else:
                                    print("余额不足！1")
                                    return False
                            else:
                                print("支付密码错误！")
                                retry_passwd += 1
                        else:
                            print("支付失败！2")
                            return False

                        print("扣除金额: %s" % repayment)
                        new_bankcard_balance = bankcard_balance - repayment  # 扣款后余额

                        bankcard_data_dic = userBankcard.load_bankcard_table()
                        bankcard_data_dic[user][bankcard]["balance"] = new_bankcard_balance
                        update_bankcard = userBankcard.update_bankcard_table(bankcard_data_dic)
                        if update_bankcard:
                            bank_creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
                            if creditcard_id in bank_creditcard_data_dic:
                                bank_creditcard_data_dic[creditcard_id]["available_balance"] = available_balance + repayment
                                bank_creditcard_data_dic[creditcard_id]["repayment"] = 0

                                update = myatm_creditcard.update_bank_creditcard_table(bank_creditcard_data_dic)
                                if update:
                                    print("还款成功！")
                                    transaction_logger.info("用户:%s 交易类型:信用卡还款 还款金额:%s 支付银行卡:%s 余额:%s 交易结果: 成功" % (
                                            user,repayment,bankcard,new_bankcard_balance))
                                    time.sleep(2)
                                    return True


def creditcard_withdraw(user,creditcard,commission_charge):
    creditcard_id = creditcard[0]
    credit_limit = creditcard[1]
    available_balance = creditcard[2]
    repayment = creditcard[3]
    pay_passwd = creditcard[4]
    withdraw_limit = int(credit_limit) / 2
    creditcard_withdrawal_rate = commission_charge["creditcard_withdrawal_rate"]
    withdraw_prompt = """
    -------------信用卡提现-------------
    注意: 信用卡提现收取0.05的手续费
    (请在下面输入提现金额[B返回])
    充值金额: """

    while True:
        withdraw_money = input(withdraw_prompt)
        if withdraw_money == "b" or withdraw_money == "B":
            break
        try:
            withdraw_money = float(withdraw_money)
            print("%.2f" % withdraw_money)
        except ValueError as diag:
            print("请输入正确的金额!")
            continue

        service_charge = creditcard_withdrawal_rate * withdraw_money
        print("可提现额度: %s" % withdraw_limit)

        user_bankcard = userBankcard.user_bankcard_info(user)
        user_bankcard_list = list(user_bankcard.keys())
        while True:
            print("\n(选择提现到银行卡[B返回])")
            for index, value in enumerate(user_bankcard_list):
                print("银行卡%s %s" % (index, value))
            select_bankcard = input("Enter your choice: ")

            if select_bankcard.isdigit():
                select_bankcard = int(select_bankcard)
                if select_bankcard >= 0 and select_bankcard < len(user_bankcard_list):
                    bankcard = user_bankcard_list[select_bankcard]
                    print(bankcard)
                    bankcard_balance = user_bankcard[bankcard]["balance"]
                    print("银行卡余额: %s" % bankcard_balance)

                    retry_passwd = 0
                    while retry_passwd < 3:
                        passwd = input("输入信用卡支付密码: ")
                        if passwd == pay_passwd:
                            print("信用卡可用额度: %s" % available_balance)
                            if withdraw_money <= withdraw_limit:  # 提现额度
                                if withdraw_money + service_charge <= available_balance:
                                    print("提现金额: %s" % withdraw_money)
                                    print("提现手续费: %s" % service_charge)
                                    new_bankcard_balance = withdraw_money + bankcard_balance  # 提现后银行卡余额
                                    new_available_balance = available_balance - withdraw_money - service_charge
                                    new_repayment = repayment + withdraw_money + service_charge

                                    bank_creditcard_data_dic = myatm_creditcard.load_bank_creditcard_table()
                                    if creditcard_id in bank_creditcard_data_dic:
                                        bank_creditcard_data_dic[creditcard_id]["available_balance"] = new_available_balance
                                        bank_creditcard_data_dic[creditcard_id]["repayment"] = new_repayment
                                        update_creditcard = myatm_creditcard.update_bank_creditcard_table(bank_creditcard_data_dic)
                                        if update_creditcard:
                                            bankcard_data = userBankcard.load_bankcard_table()
                                            bankcard_data[user][bankcard]["balance"] = new_bankcard_balance
                                            update_bankcard = userBankcard.update_bankcard_table(bankcard_data)
                                            if update_bankcard:
                                                print("提现成功！")
                                                transaction_logger.info(
                                                    "用户:%s 交易类型:信用卡提现 提现金额:%s 手续费:%s 提现银行卡:%s 交易结果: 成功" % (
                                                        user, withdraw_money, service_charge, bankcard))
                                                time.sleep(2)
                                                return True
                                else:
                                    print("信用卡可用余额不足！")
                                    return False
                            else:
                                print("超出限额！")
                                return False
                        else:
                            print("密码错误！")
                            retry_passwd += 1
                    else:
                        print("提现失败！")
                        return False
                else:
                    print("找不到银行卡！")


def wallet_creditcard(user,user_data,commission_charge):
    ''''''
    def view_creditcard():
        user_creditcard = myatm_creditcard.load_user_creditcard(user)
        if user_creditcard != None:
            user_creditcard_list = user_creditcard
            retry_pay_pass = True
            while retry_pay_pass:
                print("---------------------")
                print("(选择信用卡)")
                for index, value in enumerate(user_creditcard_list):
                    print("信用卡%s %s" % (index, value))
                print("---------------------")
                select_creditcard = input("Enter your choice: ")
                if select_creditcard == "b" or select_creditcard == "B":
                    break

                if select_creditcard.isdigit():
                    select_creditcard = int(select_creditcard)
                    if select_creditcard >= 0 and select_creditcard < len(user_creditcard_list):
                        creditcard_id = user_creditcard_list[select_creditcard]
                        print(creditcard_id)

                        #加载信用卡数据
                        bank_creditcard_data = myatm_creditcard.load_bank_creditcard_table()
                        if creditcard_id in bank_creditcard_data:
                            creditcard_lock_status = bank_creditcard_data[creditcard_id]["status"]
                            if creditcard_lock_status == 0:
                                creditcard_pay_pass = bank_creditcard_data[creditcard_id]["pay_passwd"]
                                credit_limit = bank_creditcard_data[creditcard_id]["credit_limit"]
                                available_balance = bank_creditcard_data[creditcard_id]["available_balance"]
                                repayment = bank_creditcard_data[creditcard_id]["repayment"]
                                enroll_date = bank_creditcard_data[creditcard_id]["enroll_date"]
                                expire_date = bank_creditcard_data[creditcard_id]["expire_date"]
                                pay_day = bank_creditcard_data[creditcard_id]["pay_day"]

                                return creditcard_id, credit_limit, available_balance, repayment, creditcard_pay_pass
                            else:
                                print("信用卡已被锁定！")
                                return None
        else:
            print("您没有绑定任何信用卡")
            time.sleep(1)
            return None

    creditcard = view_creditcard()
    if creditcard != None:
        creditcard_prompt = """
        ------------信用卡{0}------------
              注意: 每月22日为还款日
        额度: {1}
        可用额度: {2}
        下月应还: {3}

        1.还款
        2.提现
        3.返回
        ----------------------------------------
        Enter your choice: """.format(creditcard[0], creditcard[1], creditcard[2], creditcard[3])
        while True:
            select = input(creditcard_prompt)
            if select == "3" or select == "b":
                break
            elif select == "1":
                creditcard_repayment(user,creditcard)
            elif select == "2":
                creditcard_withdraw(user,creditcard,commission_charge)


@login_required
def shopping_wallet(user_data):    #我的钱包
    user_data = set_wallet_pay_passwd(user_data)
    user = user_data["account_id"]
    wallet_balance = user_data["user_data"]["wallet_balance"]
    wallet_prompt = """
-----我的钱包-----
      余额
账户余额(元): {0}
(1)充值
(2)提现
(3)转账
(4)银行卡
(5)信用卡
(6)返回(B)
------------------
Enter your choice: """.format(wallet_balance)

    while True:
        wallet_option = input(wallet_prompt)
        if wallet_option == "1":
            user_data = wallet_recharge(user,user_data)
            shopping_wallet(user_data)
        elif wallet_option == "2":
            user_data = request_withdrawal(user,user_data,commission_charge)
            shopping_wallet(user_data)
        elif wallet_option == "3":
            transfer_accounts(user,user_data,commission_charge)
        elif wallet_option == "4":
            binding_bankcard_account(user,user_data)
        elif wallet_option == "5":
            wallet_creditcard(user,user_data,commission_charge)
        elif wallet_option == "6":
            break
        elif wallet_option == "B" or wallet_option == "b":
            break
        else:
            continue






