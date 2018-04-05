#/usr/bin/env python3
# _*_ coding: utf-8 _*_

from include import shopping_center
from include import personal_center
from include import shopping_wallet
from include import account_auth
from include import matm_management

login = {"login": "立即登录", "logout":"退出登录"}
user_data = {"account_id": None, "is_authenticated": False, "user_data": None}

main_prompt = """
-------欢迎访问我的商城！--------
    1.进入商城
    2.个人中心
    3.我的钱包
    4.{0}
    5.后台管理
    6.退出程序
-------------------------------
Enter your choice: """


class ShoppingMallsMenus(object):
    def __init__(self,user_data):
        self.userData = user_data
        self.loginUser = user_data["account_id"]
        self.loginAuth = user_data["is_authenticated"]
        self.loginData = user_data["user_data"]

    def shopping_center(self):   #进入商城
        shopping_center.shopping_center(self.userData)

    def personal_center(self):   #个人中心
        personal_center.personal_center(self.userData)

    def shopping_wallet(self):  #我的钱包
        shopping_wallet.shopping_wallet(self.userData)

    def matm_management(self):  #后台管理
        matm_management.matm_management(self.userData)

    def user_login(self):       #帐号登录
        account_auth.account_login(self.userData)

    def user_logout(self):      #退出登录
        account_auth.account_logout(self.userData)

    def exit(self):             #退出程序
        exit("Bye.")


shoppingMallsMenus = ShoppingMallsMenus(user_data)
def run():
    prompt_memu = ""
    login_s = False
    while True:
        if user_data["is_authenticated"] == False:
            prompt_memu = main_prompt.format(login.get("login"))
            login_s = False
        elif user_data["is_authenticated"] == True:
            prompt_memu = main_prompt.format(login.get("logout"))
            login_s = True
        choice = input(prompt_memu)
        menu_dic = {
            '1': shoppingMallsMenus.shopping_center,
            '2': shoppingMallsMenus.personal_center,
            '3': shoppingMallsMenus.shopping_wallet,
            '4': shoppingMallsMenus.user_login,
            '5': shoppingMallsMenus.matm_management,
            '6': shoppingMallsMenus.exit
        }
        if choice in menu_dic:
            if choice == "4":
                if login_s == True:
                    menu_dic[choice] = shoppingMallsMenus.user_logout
            menu_dic[choice]()
