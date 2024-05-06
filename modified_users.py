from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE
import time
import json
import smtplib
import requests
import pandas as pd
from datetime import timedelta, datetime, date
from requests.auth import HTTPBasicAuth


class ad_modify:
    def __init__(self):
        self.data = None
        self.user_name = "payu_api"
        self.password = "3MzkqYPQJjNvQTX$By8km3Mm@4qdK8IHHYej3&QCav1g@imXh&MqonZSOVAAN9UN"
        self.server = "smtp.office365.com"
        self.sender = "HRMS.Notification@payu.in"
        self.server_password = "Dux63612"

    def ldap_login(self):
        server = Server('ldaps://10.100.65.21', port=636, use_ssl=False)
        conn = Connection(server, user='HRMS integration', password='#2k12@QazTgbIHjY%#S";P')
        conn.bind()
        print(conn.bind())
        return conn

    def ldap_search(self, conn, mail):
        conn.search(
            search_base="DC=IDC,DC=payugur,DC=com",
            search_filter=f"(userPrincipalName={mail})",
            search_scope=SUBTREE,
            attributes=ALL_ATTRIBUTES,
            get_operational_attributes=True,
            paged_size=1000)
        print(conn.response)
        response = conn.response[0]
        return response

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

    def modified_user_data(self):

        try:
            url = "https://payu.darwinbox.in/masterapi/employee"
            api_key = "9caa60a7ce62d181c34beac524c463e3a5019a9c11bfd649535fe5ae18b37d362b22757eaa99e068a49836ae2f75566b0c76a65f452fcd137e7c52e52a319602"
            datasetKey = "6a64a1f89aad3c2e4fad545a0acdd5128924424ad38c5b0ea93f6a726441d5443b2adcbc29e7727e521026da734a1c7708b497cc25ca9927502c31b9ce589f2a"
            date_of_activation = date.today()
            date_of_activation = date_of_activation.strftime("%d-%m-%Y")
            # date_of_activation = "5-12-2022"
            print("Getting onboarding employee data from Darwin")
            body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "last_modified": date_of_activation})
            response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
            print(response.status_code)
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
            {str(e)} <br>
            Kindly test the API credentials for more details.
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def modify_ad_user(self):
        try:
            for employee in self.data:
                conn = self.ldap_login()
                employee_mail = employee["company_email_id"]
                response = self.ldap_search(conn, employee_mail)
                if 'dn' in response:
                    user_dn = response['dn']
                    if 'attributes' in response:
                        user_details = response['attributes']
                        print(response['attributes'])

                        if 'department' in user_details and user_details['department'] != employee['department']:
                            conn.modify(user_dn, {'department': (MODIFY_REPLACE, [employee['department']])})
                        if 'title' in user_details and user_details['title'] != employee['designation']:
                            conn.modify(user_dn, {'title': (MODIFY_REPLACE, [employee['designation']])})
                        if 'telephoneNumber' in user_details and user_details['telephoneNumber'] != employee[
                            'personal_mobile_no']:
                            conn.modify(user_dn, {'designation': (MODIFY_REPLACE, [employee['telephoneNumber']])})
                        if 'manager' in user_details and user_details['manager'] != employee['designation']:
                            conn.modify(user_dn, {'designation': (MODIFY_REPLACE, employee['manager'])})
                        if 'designation' in user_details and user_details['designation'] != employee['designation']:
                            conn.modify(user_dn, {'designation': (MODIFY_REPLACE, employee['designation'])})
                        if 'designation' in user_details and user_details['designation'] != employee['designation']:
                            conn.modify(user_dn, {'designation': (MODIFY_REPLACE, employee['designation'])})
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>"
            subject = "Darwin API error while fetching new joinee data"
            body = f"""
            Hi all, <br>
            {str(e)} <br>
            Kindly test the API credentials for more details.
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)


if __name__ == '__main__':
    ad_modify = ad_modify()
    ad_modify.modified_user_data()
    ad_modify.modify_ad_user()

        # attr = {'company': item['group_company'], 'physicalDeliveryOfficeName': item['office_location'],
        #         'title': item['designation']
        #         'department': item['department'],
        #         'userAccountControl': 544}
