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
        self.employee_data = []
        self.incomplete_data = []
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

    def get_darwin_data(self):
        try:
            url = "https://payu.darwinbox.in/masterapi/employee"
            api_key = "9caa60a7ce62d181c34beac524c463e3a5019a9c11bfd649535fe5ae18b37d362b22757eaa99e068a49836ae2f75566b0c76a65f452fcd137e7c52e52a319602"
            datasetKey = "6a64a1f89aad3c2e4fad545a0acdd5128924424ad38c5b0ea93f6a726441d5443b2adcbc29e7727e521026da734a1c7708b497cc25ca9927502c31b9ce589f2a"
            date_of_activation = date.today()
            date_of_activation = date_of_activation.strftime("%d-%m-%Y")
            # date_of_activation = "5-12-2022"
            print("Getting onboarding employee data from Darwin")
            body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "date_of_activation": date_of_activation})
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
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Darwin API error while fetching new joinee data"
            body = f"""
            Hi all, <br>
            {str(e)} <br>
            Kindly test the API credentials for more details.
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def validate_data(self):
        try:
            print("validating employee data fetched from Darwin")
            for employee in self.data:
                emp = {}
                if employee["first_name"] and employee["employee_id"] and employee["department"] \
                        and employee["designation"] and employee["group_company"] and employee["office_location"] \
                        and employee["direct_manager"] and not employee["company_email_id"]:
                    first_name = employee["first_name"].strip().split(" ")[0]
                    last_name = employee["last_name"].strip().split(" ")[0] if "last_name" in employee else ""
                    if last_name:
                        display_name = first_name + "." + last_name
                    else:
                        name = employee["first_name"].strip().split(" ")
                        if len(name) > 1:
                            name = name[0] + "." + name[1]
                        else:
                            name = name[0]
                        display_name = name
                    if len(display_name) <= 16:
                        employee["display_name"] = display_name
                        self.employee_data.append(employee)
                    else:
                        emp["Name"] = first_name + " " + last_name
                        emp["ID"] = employee["employee_id"]
                        emp["error"] = "The length of first name + last name exceeds 16 characters"
                        self.incomplete_data.append(emp)
                else:
                    if employee["company_email_id"]:
                        pass
                    else:
                        emp["Name"] = employee["first_name"]
                        emp["ID"] = employee["employee_id"]
                        emp["error"] = "Incomplete Employee data"
                        self.incomplete_data.append(emp)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Error while validating data"
            body = f"""
            Hi all,<br>

            {str(e)}<br>

            Kindly look at the validation script for more details.
            """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def get_all_emails(self):
        try:
            email_list = []
            total_entries = 0
            server = Server('ldap://10.100.65.21', port=389, use_ssl=False)
            conn = Connection(server, user='HRMS integration', password='#2k12@QazTgbIHjY%#S";P')
            conn.bind()
            print(conn.bind())
            conn.search(search_base="DC=IDC,DC=payugur,DC=com",
                        search_filter="(objectClass=*)",
                        search_scope=SUBTREE,
                        attributes=ALL_ATTRIBUTES,
                        get_operational_attributes=True,
                        paged_size=1000)
            total_entries += len(conn.response)
            for entry in conn.response:
                if 'attributes' in entry and 'userPrincipalName' in entry['attributes']:
                    email_list.append(entry['attributes']['userPrincipalName'])
            cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            while cookie:
                conn.search(
                    search_base="DC=IDC,DC=payugur,DC=com",
                    search_filter="(objectClass=*)",
                    search_scope=SUBTREE,
                    attributes=ALL_ATTRIBUTES,
                    get_operational_attributes=True,
                    paged_size=1000,
                    paged_cookie=cookie
                )
                total_entries += len(conn.response)
                cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
                for entry in conn.response:
                    if 'userPrincipalName' in entry['attributes']:
                        email_list.append(entry['attributes']['userPrincipalName'])
            conn.unbind()
            return email_list
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Error while connecting to AD"
            body = f"""
            Hi all,<br>

             {str(e)}<br>

             Kindly look at the AD for more details.
             """
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def push_data_to_ad(self, item):
        try:
            print(f"Pushing {item['first_name']} {item['last_name']} data to AD")
            server = Server('ldap://10.100.65.21', port=389, use_ssl=False)
            conn = Connection(server, user='HRMS integration', password='#2k12@QazTgbIHjY%#S";P')
            conn.bind()
            # for index, item in enumerate(self.employee_data):
            email = item['company_email_id']
            last_name = item['last_name'] if "last_name" in item else ""
            first_name = item['first_name']
            if 'num' in item:
                num = item['num']
                last_name = last_name + str(num)
            name = first_name + last_name
            full_name = first_name + " " + last_name
            full_name = full_name.strip(" ")
            dn = f"cn={full_name},ou=ISO_27000,DC=IDC,DC=payugur,DC=com"
            # attr = {'givenName': first_name, 'userPrincipalName': email, 'SamAccountName': name,
            #         'sn': last_name, 'mail': email, 'displayName': full_name, 'l': 'Bangalore',
            #         'telephoneNumber': 1234567890, 'title': 'SE',
            #         'manager': 'cn=OvertimeOT,ou=Upbhogyata,DC=Gurgaon,DC=local',
            #         'department': 'Cyber Security',
            #         'userAccountControl': 544}
            manager_email = item["direct_manager_email"]
            conn.search(
                search_base="DC=IDC,DC=payugur,DC=com",
                search_filter=f"(userPrincipalName={manager_email})",
                search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES,
                get_operational_attributes=True,
                paged_size=1000
            )
            response = conn.response[0]
            attr = {'givenName': first_name, 'userPrincipalName': email, 'SamAccountName': name,
                    'mail': email, 'displayName': full_name, 'company': item['group_company'],
                    'physicalDeliveryOfficeName': item['office_location'], 'EmployeeID': item['employee_id'],
                    'title': item['designation'], 'description': item['employee_id'],
                    'department': item['department'],
                    'userAccountControl': 544}
            if item['personal_mobile_no']:
                attr['telephoneNumber'] = item['personal_mobile_no']
            if last_name:
                attr['sn'] = last_name
            if 'dn' in response:
                manager_dn = response['dn']
                attr['manager'] = manager_dn
            response = conn.add(dn, object_class='user', attributes=attr)
            print(response)
            if response:
                print(f"{full_name} has been added to AD")
                self.successful_list.append(item)
            else:
                self.failed_list.append(item)
            # conn.modify(dn, {'userAccountControl': (MODIFY_REPLACE, [544])})
            conn.unbind()
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Error while updating data in AD"
            body = f"""
            Hi all,<br>

            {str(e)}<br>

            Kindly look at the script for more details."""
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def create_email_ids(self):
        try:
            if self.data and self.employee_data:
                for index, item in enumerate(self.employee_data):
                    email_list = self.get_all_emails()
                    if email_list:
                        email_list.sort()
                    emails = []
                    for email in email_list:
                        emails.append(email.split("@")[0])
                    matched_emails = []
                    display_name = item["display_name"].lower()
                    for email in emails:
                        if display_name in email:
                            matched_emails.append(email)
                    if len(matched_emails) == 0:
                        print(f"create a new mail id: {display_name}@payu.in")
                        email_id = display_name + "@payu.in"
                        self.employee_data[index]['company_email_id'] = email_id
                    else:
                        if len(matched_emails) == 1:
                            print(f"This is the mail id: {display_name}1@payu.in")
                            email_id = display_name + "1@payu.in"
                            self.employee_data[index]['num'] = '1'
                            self.employee_data[index]['company_email_id'] = email_id
                        else:
                            matched_emails.sort()
                            last_num = int(matched_emails[-1][-1]) + 1
                            print(f"Mail id is: {display_name}{str(last_num)}@payu.in")
                            email_id = display_name + str(last_num) + "@payu.in"
                            self.employee_data[index]['num'] = str(last_num)
                            self.employee_data[index]['company_email_id'] = email_id
                    self.push_data_to_ad(item)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Error while validating data"
            body = f"""
            Hi all,<br>

            {str(e)}<br>

            Kindly look at the script for more details."""
            message = self.message_creation(to_address, subject, body)
            to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            # to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)

    def push_to_darwin(self):
        try:
            print("Updating new email ID to Darwin")
            url = "https://payu.darwinbox.in/UpdateEmployeeDetails/update"
            api_key = "8e129378996a0dd4c57e001f819d37ff7e217eac3920e152df7a1b719b3b39b95e6232a314f8aa674b06a74e4ec246db8e6a88a0ef0efa05570a42ff22a5bd15"
            for employee in self.successful_list:
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
            if self.incomplete_list or self.incomplete_data or self.failed_list:
                darwin_fail_df = pd.json_normalize(self.incomplete_list)
                incomplete_data_df = pd.json_normalize(self.incomplete_data)
                ad_update_fail_df = pd.json_normalize(self.failed_list)
                subject = "Employees that are not updated"
                body = f"""
                Hi all,<br>
                Below is the list of users whose data is incomplete.<br><br>
                {incomplete_data_df.to_html()} <br>
                <br>
                Below is the list of users who were not updated in AD<br><br>
                {ad_update_fail_df.to_html()} <br>
                <br>
                Below is the list of users whose email id has not been updated to Darwin.<br><br>
                {darwin_fail_df.to_html()}<br>

                """
                to_address = "<ankita.mishra1@payu.in>, <sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, " \
                             "<infraadmin@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in>"
                message = self.message_creation(to_address, subject, body)
                to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                              "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in"]
                # to_address = ["sourabh.kulkarni@payu.in"]
                self.send_mail(message, to_address)
            if not self.data:
                subject = "No employees to Onboard"
                body = """
                Hi all,<br><br>
                There are no employees fetched from Darwin to Onboard.
                <br><br>
                Thanks and Regards,<br>
                HRMS Portal"""
                to_address = "<ankita.mishra1@payu.in>, <sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, " \
                             "<infraadmin@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in>"
                message = self.message_creation(to_address, subject, body)
                to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                              "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in"]
                self.send_mail(message, to_address)
            if self.completed_list:
                completed_df = pd.json_normalize(self.completed_list)
                subject = "Employees Onboarded list"
                body = f"""
                                Hi all,<br><br>
                                Below mentioned employees have been onboarded today.
                                <br><br>
                                {completed_df.to_html()} <br>
                                <br><br>
                                Thanks and Regards,<br>
                                HRMS Portal"""
                to_address = "<ankita.mishra1@payu.in>, <sourabh.kulkarni@payu.in>, <itsupport-pan-india@payu.in>, " \
                             "<infraadmin@payu.in>, <tushar.tewatia@payu.in>, <cheenu.tyagi@payu.in>"
                message = self.message_creation(to_address, subject, body)
                to_address = ["sourabh.kulkarni@payu.in", "itsupport-pan-india@payu.in", "infraadmin@payu.in",
                              "ankita.mishra1@payu.in", "tushar.tewatia@payu.in", "cheenu.tyagi@payu.in"]
                self.send_mail(message, to_address)
        except Exception as e:
            to_address = "<sourabh.kulkarni@payu.in>, <ravi.rai@payu.in>, <dharmender.banibal@payu.in>"
            subject = "Darwin API error while updating email ID to Darwin"
            body = f"""
            Hi all,<br>

            {str(e)}<br>
            Darwin failed to update the below mentioned employee list:<br>
            str({self.failed_list})<br>

            Kindly look at the API for more details.<br>
                    """
            message = self.message_creation(to_address, subject, body)
            # to_address = ["sourabh.kulkarni@payu.in", "ravi.rai@payu.in", "dharmender.banibal@payu.in"]
            to_address = ["sourabh.kulkarni@payu.in"]
            self.send_mail(message, to_address)


if __name__ == '__main__':
    start = time.time()
    ad = AD()
    # Get details from Darwin API
    ad.get_darwin_data()
    # Validate the data if it is in the right format
    ad.validate_data()
    # create a sample email id and check if it already exists
    ad.create_email_ids()
    # Now send the email id back to Darwin
    ad.push_to_darwin()

    print(time.time() - start)

