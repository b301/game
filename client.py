import requests
import time
import sys
import os
import re


class Game:
    HOST = "localhost"
    PORT = 20000
    AUTHENTICATION_ENDPOINT = "http://{}:{}/authentication"

    SETTINGS = """%%%%%%%%% SETTINGS %%%%%%%%%
    HOST: {}
    PORT: {}
    AUTHENTICATION ENDPOINT: {}
%%%%%%%%% SETTINGS %%%%%%%%%"""
    MENU = """%%%%%%%%%%% MENU %%%%%%%%%%%
    PICK AN OPTION

     PLAY
     LOGIN
     REGISTER
     STATUS
     SETTINGS
    
    ENTER `EXIT` TO QUIT
%%%%%%%%%%% MENU %%%%%%%%%%%"""
    STATUS = """%%%%%%%%%% STATUS %%%%%%%%%%

    Logged: {}
    Authentication: {}

PRESS ENTER TO LEAVE
%%%%%%%%%% STATUS %%%%%%%%%%"""

    def __init__(self) -> None:
        self.platform = sys.platform
        self.login_status = False
        self.auth_token = None
        self.__menu__()

    def __authenticate__(self, mode: str) -> None:
        while True:
            self.__clear__()
            print(f"%%%%%%%%%%% {mode.upper()} %%%%%%%%%%%")
            cont = True
            username = input("Enter username: ")
            if username.upper() == "EXIT":
                return

            password = input("Enter password: ")
            if password.upper() == "EXIT":
                return

            if mode == "register":
                confirm = input("Confirm Password: ")
                if confirm.upper() == "EXIT":
                    return

                if password != confirm:
                    print("THE PASSWORDS DO NOT MATCH")
            
            if cont:
                try:
                    request = requests.get(
                        url=f"{self.AUTHENTICATION_ENDPOINT.format(self.HOST,self.PORT)}?type={mode}&username={username}&password={password}")
                except:
                    print("AUTHENTICATION SERVICE IS CURRENTLY DOWN")
                    break

                if request.status_code not in range(200, 300):
                    print("AUTHENTICATION SERVICE IS CURRENTLY DOWN")
                    break
                
                response = eval(request.text)
                if response["response"] == "success":
                    self.auth_token = response["auth_token"]
                    print("LOGGED IN SUCCESSFULLY")
                    self.login_status = True
                    break

            print(f"%%%%%%%%%%% {mode.upper()} %%%%%%%%%%%")

        time.sleep(3)


    def __play__(self):
        pass

    def __menu__(self):
        while True:
            self.__clear__()
            print(self.MENU)
            uinput = input().upper()

            if uinput not in ["PLAY", "LOGIN", "REGISTER", "STATUS", "EXIT", "SETTINGS"]:
                print("THERE IS NO SUCH OPTION")

            elif uinput == "SETTINGS":
                self.__settings__()

            elif uinput == "EXIT":
                break

            elif uinput == "STATUS":
                self.__clear__()
                print(self.STATUS.format(self.login_status, self.auth_token))
                input()

            elif uinput == "REGISTER":
                self.__authenticate__(mode="register")

            elif uinput == "LOGIN":
                self.__authenticate__(mode="login")

            elif uinput == "PLAY":
                self.__play__()

    def __settings__(self) -> None:
        nHOST = self.HOST
        nPORT = self.PORT

        while True:
            disallow = False
            self.__clear__()
            print(self.SETTINGS.format(nHOST, nPORT, self.AUTHENTICATION_ENDPOINT.format(nHOST, nPORT)))
            uinput = input("DO YOU WISH TO MODIFY THE SETTINGS? (Y/N): ").upper()

            if uinput not in ["Y", "N", "YES", "NO", "EXIT"]:
                print("THERE IS NO SUCH OPTION")
            
            elif uinput in ["Y", "YES"]:
                self.__clear__()
                print("%%%%%%%%% SETTINGS %%%%%%%%%")
                nHOST = input("Enter `Host`: ")
                if nHOST == "EXIT":
                    return

                nPORT = input("Enter `Port`: ")
                if nPORT == "EXIT":
                    return

                if not re.match(r"\b[a-zA-Z\.\-]*$", nHOST):
                    print("HOST NAME MAY ONLY CONTAIN ALPHABETICAL CHARACTERS, A DOT (.) OR A DASH (-)")
                    disallow = True
                
                try:
                    nPORT = int(nPORT)
                except:
                    print("PORT HAS TO BE AN INTEGER")
                    disallow = True

                if nPORT not in range(1, 65566):
                    print("PORT HAS TO BE AN INTEGER IN THE RANGE (1, 65565)")
                    disallow = True
                
                if not disallow:
                    print("SUCCESS! MODIFIED THE SETTINGS")
                    self.PORT = nPORT
                    self.HOST = nHOST

                print("%%%%%%%%% SETTINGS %%%%%%%%%")
                time.sleep(2)
 
            elif uinput in ["N", "NO", "EXIT"]:
                return


    def __clear__(self) -> None:
        if self.platform == "win32":
            os.system("cls")
        elif self.platform == "linux":
            os.system("clear")


if __name__ == "__main__":
    Game()