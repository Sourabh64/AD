import time
import json
import smtplib
import requests
import pandas as pd
from datetime import timedelta, datetime, date
from requests.auth import HTTPBasicAuth
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE


class AD:
    def __init__(self):
        self.data = None
        self.lwd_data = None
        self.lwd = None
        self.employee_data = []
        self.incomplete_data = []
        self.inactive_users = []
        self.successful_list = []
        self.failed_list = []
        self.completed_list = []
        self.incomplete_list = []
        self.user_name = "payu_api"
        self.password = "3MzkqYPQJjNvQTX$By8km3Mm@4qdK8IHHYej3&QCav1g@imXh&MqonZSOVAAN9UN"
        self.server = "smtp.office365.com"
        self.sender = "HRMS.Notification@payu.in"
        self.server_password = "Dux63612"

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

    def get_inactive_users(self):
        try:
            print("Fetching users to be deactivated")
            url = "https://payu.darwinbox.in/masterapi/employee"
            api_key = "c4e198e1fbcf222e06de5b186b63379f80be9e7d13b5ef150a612fbcb40b92905408c99e85e93c9c6352aef6f568733a57a23b59af7a9c894928ee40530cf28f"
            datasetkey = "40ff43819f9100af9d938ba850d48d6af99dd7b2a3ed2c9f384d806b67924e7550394a3999884b3d017f062432f356edfa1b95ec52ffc514e5bd85a726cfb314"
            l_date = date.today()
            lwd = l_date - timedelta(days=1)
            self.lwd = lwd.strftime("%d-%m-%Y")
            body = json.dumps({"api_key": api_key, "datasetKey": datasetkey, "last_modified": self.lwd})
            response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
            if response.status_code == 200:
                result = response.json()
                if result["status"] == 1:
                    self.inactive_users = result["employee_data"]
                else:
                    self.inactive_users = {}
            else:
                raise Exception(
                    f"Darwin API has given response status code of <b>{response.status_code}</b> while fetching inactive users data")
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Darwin API error while fetching inactive users data"
            body = f"""
            Hi all,<br>

            {str(e)}<br>

            Kindly look at the API for more details.<br>
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            self.send_mail(message, to_address)

    def deactivate_users_ad(self):
        try:
            deactivated_list = []
            deactivate_failed_list = []
            for employee in self.inactive_users:
                if employee['date_of_exit'] >= self.lwd:
                    print(f"Deactivating {employee['full_name']} in AD")
                    server = Server('ldap://10.100.65.21', port=389, use_ssl=False)
                    conn = Connection(server, user='HRMS integration', password='#2k12@QazTgbIHjY%#S";P')
                    conn.bind()
                    conn.search(
                        search_base="DC=IDC,DC=payugur,DC=com",
                        search_filter=f"(userPrincipalName={employee['company_email_id']})",
                        # search_filter=f"(userPrincipalName=dilpreet.gill@payu.in)",
                        search_scope=SUBTREE,
                        attributes=ALL_ATTRIBUTES,
                        get_operational_attributes=True,
                        paged_size=1000
                    )
                    response = conn.response[0]
                    if 'dn' in response:
                        user_dn = response['dn']
                        response = conn.modify(user_dn, {'userAccountControl': (MODIFY_REPLACE, [514])})
                        if response:
                            deactivated_list.append(employee)
                        else:
                            deactivate_failed_list.append(employee)
                    conn.unbind()
                else:
                    print(employee)
            df = pd.json_normalize(deactivated_list)
            another_df = pd.json_normalize(deactivate_failed_list)
            to_address = "<sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, <infraadmin@payu.in>, " \
                         "<ankita.mishra1@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in> "
            subject = "Offboarded employee data"
            body = f"""
                                       Hi all,<br>
                                       The below accounts has been disabled:<br><br>
                                       {df.to_html()}<br>

                                        <br>
                                        Thanks and Regards,<br>
                                        HRMS Portal
                                        """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                          "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in"]
            self.send_mail(message, to_address)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Error while deactivating users in AD"
            body = f"""
             Hi all,<br>

             {str(e)}<br>

             Kindly look at the AD for more details.<br>
             """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            self.send_mail(message, to_address)


if __name__ == '__main__':
    start = time.time()
    ad = AD()
    # Check for inactive users from Darwin API
    ad.get_inactive_users()
    # Make inactive users inactive in AD
    ad.deactivate_users_ad()
    print(time.time() - start)

