#/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import sys
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modules import myatm_logger
from include import account_auth
from include.shopping_wallet import bankcard_pay_way
from include.shopping_wallet import creditcard_pay_way
from modules import myatm_accounts
from modules import myatm_shoppingcart

server_logger = myatm_logger.logger("server")
transaction_logger = myatm_logger.logger("transaction")

def view_shopping_list(user_data):
    user = user_data["account_id"]
    shopping_list = myatm_shoppingcart.load_product_table()
    shopping_cart = myatm_shoppingcart.load_shopping_cart()
    try:
        user_shopping_cart = shopping_cart[user]
    except KeyError as e:
        user_shopping_cart = {}

    while True:
        print("-----------商品列表-----------")
        product_type = []
        for index, value in shopping_list.items():
            product_type.append(index)
            print(index, value["TYPENAME"])
        print("4 返回")
        print("-----------------------------")
        choice = input("Enter your choice: ")
        if choice == "b" or choice == "4":
            break
        if choice in product_type:
            product_flag = False
            for key in shopping_list[choice]:
                product_flag = True
                break
            while True:
                if product_flag == True:
                    print("--------------------------------------------------------------")
                    print("序号\t商品编号\t价格    商品名称")
                    product_list = shopping_list[choice]["PRODUCT"]
                    for product in product_list:
                        print("%s\t\t%s\t\t%s    %s" % (
                        product["No"], product["CODE"], product["PRICE"], product["NAME"]))
                    print("--------------------------------------------------------------")
                    choice_product = input("输入商品序号加入购物车(b返回): ")
                    if user_data["account_id"] == None:
                        print("需要登录才能购买！正在为您跳转到登录页面...")
                        time.sleep(1)
                        user_data = account_auth.new_login(user_data)

                        return user_data
                    if choice_product == "b":
                        break
                    if choice_product.isdigit():
                        choice_product = int(choice_product)
                        if choice_product >= 0 and choice_product <= len(product_list):
                            for value in product_list:
                                if choice_product == value["No"]:
                                    print(value["No"])
                                    if value["CODE"] in user_shopping_cart:
                                        name = user_shopping_cart[value["CODE"]]["name"]
                                        price = user_shopping_cart[value["CODE"]]["price"]
                                        count = user_shopping_cart[value["CODE"]]["count"]
                                        total = user_shopping_cart[value["CODE"]]["total"]
                                        user_shopping_cart[value["CODE"]]["count"] = count + 1
                                        user_shopping_cart[value["CODE"]]["total"] = total + value["PRICE"]
                                    else:
                                        product_info = {"name": value["NAME"], "price": value["PRICE"], "count": 1,
                                                        "total": value["PRICE"]}
                                        user_shopping_cart[value["CODE"]] = product_info

                                    shopping_cart[user] = user_shopping_cart
                                    print(shopping_cart)
                                    myatm_shoppingcart.update_shopping_cart(shopping_cart)
                                    time.sleep(1)


def wallet_pay(user,user_data,pay_money):    #
    wallet_balance = user_data["user_data"]["wallet_balance"]
    wallet_passwd = user_data["user_data"]["pay_passwd"]
    retry_pass = 0
    while retry_pass < 3:
        password = input("请输入支付密码: ")
        if password == wallet_passwd:
            print("当前余额: %s" % wallet_balance)
            print("支付金额: %s" % pay_money)
            if pay_money < wallet_balance:
                new_wallet_balance = wallet_balance - pay_money
                print("支付后余额: %s" % new_wallet_balance)
                user_data["user_data"]["wallet_balance"] = new_wallet_balance
                account_data_dic = myatm_accounts.load_account_data()
                account_data_dic[user_data["account_id"]]["wallet_balance"] = new_wallet_balance
                update_account_info = myatm_accounts.update_account_data(account_data_dic)
                if update_account_info:
                    print("支付成功！")
                    transaction_logger.info("用户:%s 交易类型:购物支付 支付金额:%s 支付类型:钱包 支付结果:成功" % (user,pay_money))
                    time.sleep(2)
                    return True
            else:
                print("余额不足, 支付失败！")
                break
        else:
            print("密码错误！")
            retry_pass += 1
    else:
        print("密码错误, 支付失败！")


def pay(user,user_data, pay_money, user_shopping_cart, shopping_cart):
    purchased_product_dict = myatm_shoppingcart.load_purchased_product()
    if purchased_product_dict == {}:
        purchased_product_dict[user] = []
    if user not in purchased_product_dict:
        user_purchased_product_list = []
    else:
        user_purchased_product_list = purchased_product_dict[user]

    buy_product_dict = {"product": user_shopping_cart, "total": pay_money, "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    def pay_success():
        user_purchased_product_list.append(buy_product_dict)
        purchased_product_dict[user] = user_purchased_product_list
        update = myatm_shoppingcart.update_purchased_product(purchased_product_dict)
        user_shopping_cart.clear()
        shopping_cart[user] = user_shopping_cart
        myatm_shoppingcart.update_shopping_cart(shopping_cart)

    pay_prompt = """
    ------------支付------------
    购买商品: {0}
    共需支付: {1}元

    1.余额支付
    2.银行卡支付
    3.信用卡支付
    4.返回
    ----------------------------
    Enter your choice: """.format(user_shopping_cart, pay_money)
    while True:
        pay_option = input(pay_prompt)
        if pay_option == "4" or pay_option == "b":
            break
        elif pay_option == "1":
            result = wallet_pay(user,user_data,pay_money)
            if result:
                pay_success()
                break
        elif pay_option == "2":
            result = bankcard_pay_way(user,user_data,pay_money)
            if result:
                pay_success()
                break
        elif pay_option == "3":
            result = creditcard_pay_way(user,user_data,pay_money)
            if result:
                pay_success()
                break


def delete_product(user_shopping_cart, user):
    shopping_cart = myatm_shoppingcart.load_shopping_cart()
    while True:
        id = input("请输入要删除商品的商品编号(返回b): ")
        if id in user_shopping_cart:
            confirm = input("删除商品: %s [确认Y|y]? " % id)
            if confirm == "Y" or confirm == "y":
                del user_shopping_cart[id]
                shopping_cart[user] = user_shopping_cart
                myatm_shoppingcart.update_shopping_cart(shopping_cart)
                print("删除成功！")
                time.sleep(1)
                return True
            else:
                break
        elif id == "b":
            break


@account_auth.login_required
def view_shopping_cart(user_data):  # 用户购物车
    user = user_data["account_id"]
    shopping_cart = myatm_shoppingcart.load_shopping_cart()
    try:
        user_shopping_cart = shopping_cart[user]
    except KeyError as e:
        shopping_cart[user] = {}
        user_shopping_cart = shopping_cart[user]

    while True:
        print("--------------------------------------------------------------------------")
        print("商品编号\t商品价格\t购买数量\t商品总额\t商品名称")
        pay_money = 0
        for id, product in user_shopping_cart.items():
            name = user_shopping_cart[id]["name"]
            price = user_shopping_cart[id]["price"]
            count = user_shopping_cart[id]["count"]
            total = user_shopping_cart[id]["total"]
            pay_money += total
            print("%s\t\t%s\t\t\t%s\t\t\t%s\t\t\t%s" % (id, price, count, total, name))
        print("--------------------------------------------------------------------------")
        print("合计(元): %s" % pay_money)
        shop_option = input("1.结算\n2.删除商品\n3.返回\nEnter your choice: ")
        if shop_option == "3" or shop_option == "b":
            break
        elif shop_option == "1":
            if user_shopping_cart != {}:
                pay(user,user_data, pay_money, user_shopping_cart, shopping_cart)
            else:
                print("当前购物车没有商品！")
        elif shop_option == "2":
            delete_product(user_shopping_cart, user)

@account_auth.login_required
def shopping_history(user_data):
    user = user_data["account_id"]
    purchased_product_dict = myatm_shoppingcart.load_purchased_product()
    try:
        user_purchased_product_list = purchased_product_dict[user]
    except KeyError as e:
        purchased_product_dict[user] = []
        user_purchased_product_list = purchased_product_dict[user]

    print("--------------------------------------历史订单--------------------------------------")
    print("订单时间\t\t\t\t支付金额\t\t商品信息")
    for dict in user_purchased_product_list:
        print("%s\t\t%s\t\t\t\t%s" % (dict["date"],dict["total"],dict["product"]))



def shopping_center(user_data):

    print(user_data)
    prompt = """
    --------------购物中心--------------
    1. 商品列表
    2. 购物车
    3. 我的订单
    4. 返回首页
    -----------------------------------
    Enter your choice: """
    while True:
        shopping_option = input(prompt)
        if shopping_option == "4":
            break
        elif shopping_option == "1":
            view_shopping_list(user_data)
        elif shopping_option == "2":
            view_shopping_cart(user_data)
        elif shopping_option == "3":
            shopping_history(user_data)

