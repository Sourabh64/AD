import time
import json
import smtplib
import requests
import pandas as pd
from datetime import datetime, date
from requests.auth import HTTPBasicAuth
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE


class Activate:
    def __init__(self):
        self.data = None
        self.completed_list = []
        self.incomplete_list = []
        self.user_name = "payu_api"
        self.password = "3MzkqYPQJjNvQTX$By8km3Mm@4qdK8IHHYej3&QCav1g@imXh&MqonZSOVAAN9UN"
        self.server = "smtp.office365.com"
        self.sender = "HRMS.Notification@payu.in"
        self.server_password = "Joz44358"

    def message_creation(self, to_address, subject, body):
        message = f"""From: HRMS Notification <HRMS.Notification@payu.in>\nTo:{to_address}
        MIME-Version: 1.0\nContent-type: text/html\nSubject: {subject}\n{body}"""
        return message

    def send_mail(self, message, to_address):
        message = message
        try:
            smtpserver = smtplib.SMTP(self.server, 587)
            smtpserver.starttls()
            smtpserver.login(self.sender, self.server_password)
            smtpserver.sendmail(self.sender, to_address, message)
        except smtplib.SMTPException as e:
            print(e)

    def get_darwin_data(self):
        try:
            url = "https://payu.darwinbox.in/masterapi/employee"
            api_key = "9caa60a7ce62d181c34beac524c463e3a5019a9c11bfd649535fe5ae18b37d362b22757eaa99e068a49836ae2f75566b0c76a65f452fcd137e7c52e52a319602"
            datasetKey = "6a64a1f89aad3c2e4fad545a0acdd5128924424ad38c5b0ea93f6a726441d5443b2adcbc29e7727e521026da734a1c7708b497cc25ca9927502c31b9ce589f2a"
            date_of_activation = date.today()
            date_of_activation = date_of_activation.strftime("%d-%m-%Y")
            date_of_activation = "28-2-2023"
            print("Getting onboarding employee data from Darwin")
            body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "date_of_activation": date_of_activation})
            response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
            if response.status_code == 200:
                result = response.json()
                if result["status"] == 1:
                    self.data = result["employee_data"]
                else:
                    self.data = {}
            else:
                raise Exception(
                    f"Darwin API has given error while fetching new joining employee data <br>response status code: <b>{response.status_code}</b> <br>error: <b>{response.text}</b>")
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>"
            subject = "Darwin API error while fetching new joinee data"
            body = f"""
            Hi all, <br>

            This error occured while fetching employee data to be activated.
            {str(e)} <br>
            Kindly test the API credentials for more details.
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def update_activate(self):
        try:
            if self.data:
                for employee in self.data:
                    emp_id = employee['employee_id']
                    company_email_id = employee['company_email_id']
                    server = Server('ldap://10.100.65.21', port=389, use_ssl=False)
                    conn = Connection(server, user='HRMS integration', password='#2k12@QazTgbIHjY%#S";P')
                    conn.bind()
                    conn.search(
                        search_base="DC=IDC,DC=payugur,DC=com",
                        search_filter=f"(userPrincipalName={company_email_id})",
                        search_scope=SUBTREE,
                        attributes=ALL_ATTRIBUTES,
                        get_operational_attributes=True,
                        paged_size=1000
                    )
                    response = conn.response[0]
                    if 'dn' in response:
                        user_dn = response['dn']
                        userpswd = "setsomethinghere"
                        conn.extend.microsoft.modify_password(user_dn, userpswd)
                        conn.modify(user_dn, {'EmployeeID': [(MODIFY_REPLACE, [emp_id])],
                                              'description': [(MODIFY_REPLACE, [emp_id])],
                                              'userAccountControl': [(MODIFY_REPLACE, [512])],
                                              'pwdLastSet': [(MODIFY_REPLACE, [0])]})
                        manager_email = employee['direct_manager_email']
                        hrbp_email = employee['hrbp_email_id']
                        to_address = "<" + manager_email + ">," + "<" + hrbp_email + ">"
                        subject = "New onboarded employee"
                        body = f"""
                                     Hi all,<br><br>
                                     New Joining Employee - {employee['full_name']} email id has been created.<br>
                                     <br> The Employee's email ID is: {employee['company_email_id']}.
                                     <br>
                                     Thanks and Regards,<br>
                                     HRMS Portal
                                     """
                        message = self.message_creation(to_address, subject, body)
                        to_address = [manager_email, hrbp_email]
                        # to_address = ["sourabh.kulkarni@payu.in"]
                        self.send_mail(message, to_address)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>"
            subject = "Error while activating employees"
            body = f"""
                        Hi all,<br>

                        {str(e)}<br>

                        Kindly look at the script for more details."""
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def update_darwin(self):
        try:
            url = "https://payu.darwinbox.in/UpdateEmployeeDetails/update"
            api_key = "8e129378996a0dd4c57e001f819d37ff7e217eac3920e152df7a1b719b3b39b95e6232a314f8aa674b06a74e4ec246db8e6a88a0ef0efa05570a42ff22a5bd15"
            for employee in self.data:
                emp = {}
                email_id = employee['company_email_id']
                employee_id = employee['employee_id']
                body = json.dumps({"api_key": api_key, "email_id": email_id, "employee_id": employee_id})
                response = requests.post(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
                if response.status_code == 200:
                    emp['full_name'] = employee['company_email_id'].split("@")[0]
                    emp['email_id'] = employee['company_email_id']
                    manager_email = employee['direct_manager_email']
                    hrbp_email = employee['hrbp_email_id']
                    to_address = "<" + manager_email + ">," + "<" + hrbp_email + ">"
                    subject = "New onboarded employee"
                    body = f"""
                            Hi all,<br><br>
                            New Joining Employee - {emp['full_name']} email id has been created.<br>
                            <br> The Employee's email ID is: {emp['email_id']}.
                            <br>
                            Thanks and Regards,<br>
                            HRMS Portal
                            """
                    message = self.message_creation(to_address, subject, body)
                    to_address = [manager_email, hrbp_email]
                    # to_address = ["sourabh.kulkarni@payu.in"]
                    self.send_mail(message, to_address)
                    self.completed_list.append(employee)
                else:
                    self.incomplete_list.append(employee)
            if self.incomplete_list:
                darwin_fail_df = pd.json_normalize(self.incomplete_list)
                subject = "Employees that are not updated to Darwin"
                body = f"""
                Hi all,<br>
                Below is the list of users whose email ID is not updated to Darwin.<br><br>
                {darwin_fail_df.to_html()} <br>
                <br> <br>
                <br><br><br>
                 Thanks and Regards,<br>
                 HRMS Portal
                """
                to_address = "<ankita.mishra1@payu.in>, <sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, " \
                             "<infraadmin@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in>, " \
                             "<bhaskar.jayanna@payu.in> "
                message = self.message_creation(to_address, subject, body)
                to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                              "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in",
                              "bhaskar.jayanna@payu.in"]
                # to_address = ["sourabh.kulkarni@payu.in"]
                self.send_mail(message, to_address)
            if not self.data:
                subject = "No employees to be updated to Darwin"
                body = """
                Hi all,<br><br>
                There are no employees fetched from Darwin to Onboard.
                <br><br>
                Thanks and Regards,<br>
                HRMS Portal"""
                to_address = "<ankita.mishra1@payu.in>, <sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, " \
                             "<bhaskar.jayanna@payu.in>," "<suresh.sharma@payu.in> ", \
                             "<infraadmin@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in>, "
                message = self.message_creation(to_address, subject, body)
                to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                              "bhaskar.jayanna@payu.in",
                              "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in",
                              "suresh.sharma@payu.in"]
                self.send_mail(message, to_address)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>"
            subject = "Darwin API error while updating email ID to Darwin"
            body = f"""
            Hi all,<br>

            {str(e)}<br>
            Darwin failed to update the below mentioned employee list:<br>
            str({self.incomplete_list})<br>

            Kindly look at the API for more details.<br>
                    """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)


if __name__ == '__main__':
    start = time.time()
    activate = Activate()
    # Get details from Darwin API
    activate.get_darwin_data()
    # Validate the data if it is in the right format
    activate.update_activate()
    # Update Darwin with the email ID
    activate.update_darwin()
