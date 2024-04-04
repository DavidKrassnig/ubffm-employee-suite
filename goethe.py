import keyring
import getpass
import pexpect
import argparse

def save_password(username=None):
    service_name = 'goethe-vpn'

    if username is None:
        username = input("Username: ")

    if not username:
        print("No user name was entered. Please enter user name.")
        return
    
    password = getpass.getpass("Enter password: ")

    if not password:
        print("Password cannot be empty.")
        return

    keyring.set_password(service_name, username, password)

    print("Password saved successfully.")

def retrieve_password(username=None):
    if not username:
        print("No user name was entered. Please enter user name.")
        return

    service_name = 'goethe-vpn'

    password = keyring.get_password(service_name, username)

    if password:
        return(password)
    else:
        print("No password found for the provided service and username.")

def vpn_connect(username=None,password=None):
    if password:
        try:
            child = pexpect.spawn("/opt/cisco/anyconnect/bin/vpn connect vpn-einwahl.uni-frankfurt.de")

            # Wait for the "Username:" prompt and send username
            child.expect("Username:")
            child.sendline(username)

            # Wait for the "Password:" prompt and send password
            child.expect("Password:")
            child.sendline(password)

            # Wait for the process to finish
            child.expect(pexpect.EOF)

            # Check last non-empty line for status
            output_lines = child.before.decode().split('\n')
            last_non_empty_line = next((line.strip() for line in reversed(output_lines) if line.strip()), None)
            if last_non_empty_line and "state: Connected" in last_non_empty_line:
                print("VPN connection established.")
            else:
                print("Some error has occured. Printing output from anyconnect:")
                print("-"*6)
                print(child.before.decode())
                print("-"*6)
        except pexpect.exceptions.ExceptionPexpect as e:
            print("Exception occurred:", e)
    else:
        print("No password found for the provided username.")

def vpn_disconnect():
    try:
        child = pexpect.spawn("/opt/cisco/anyconnect/bin/vpn disconnect")

        # Wait for the process to finish
        child.expect(pexpect.EOF)

        # Check last non-empty line for status
        output_lines = child.before.decode().split('\n')
        last_non_empty_line = next((line.strip() for line in reversed(output_lines) if line.strip()), None)
        if last_non_empty_line and "state: Disconnected" in last_non_empty_line:
            print("VPN disconnected.")
        elif last_non_empty_line and "The VPN client is not connected." in last_non_empty_line:
            print("Error: No VPN to disconnect.")
        else:
            print("Some error has occured. Printing output from anyconnect:")
            print("-"*6)
            print(child.before.decode())
            print("-"*6)
    except pexpect.exceptions.ExceptionPexpect as e:
        print("Exception occurred:", e)

def useInternet(username=None,password=None,myFunction=None):
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    
    driver.get('https://gleitzeit.verwaltung.uni-frankfurt.de/primemobile/login')

    # Find the username and password input fields and submit the form
    webusername = driver.find_element(By.NAME, "username")
    webpassword = driver.find_element(By.NAME, "password")

    webusername.send_keys(username)
    webpassword.send_keys(password)

    webpassword.submit()

    wait = WebDriverWait(driver, 10)  # You can adjust the timeout as needed

    if myFunction == "saldo":
        goToBooking = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Salden')]")))
        goToBooking.click()

        balance_element = driver.find_element(By.XPATH, "//tr[@class='sub-balance history-link'][@balance_id='0']")

        # Find the nested balance value element and print its text
        balance_value_element = balance_element.find_element(By.XPATH, ".//td[@class='balance-value']")
        balance_value = balance_value_element.text
        print("Balance value:", balance_value)
    
    if myFunction == "clockin":
        goToBooking = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Jetzt buchen')]")))
        goToBooking.click()

        booking_icon = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Kommen')]")))
        booking_icon.click()
        booking_icon.submit()
        print('Successfully clocked in!')
    
    if myFunction == "clockout":
        goToBooking = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Jetzt buchen')]")))
        goToBooking.click()

        booking_icon = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Gehen')]")))
        booking_icon.click()
        booking_icon.submit()
        print('Successfully clocked out!')

    driver.quit()

def main():
    username = 'krassnig'
    password = retrieve_password(username)

    parser = argparse.ArgumentParser(description="VPN Connection")
    parser.add_argument("action", choices=["connect", "disconnect","saldo","clockin","clockout","credentials"])
    args = parser.parse_args()

    if args.action == "connect":
        vpn_connect(username,password)

    if args.action == "disconnect":
        vpn_disconnect()

    if args.action == "saldo":
        useInternet(username,password,args.action)

    if args.action == "clockin":
        useInternet(username,password,"clockin")

    if args.action == "clockout":
        useInternet(username,password,"clockout")

    if args.action == "credentials":
        save_password()

if __name__ == "__main__":
    main()
