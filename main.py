import time
import json
import smtplib
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE


class AD:
    def __init__(self):
        self.data = None
        self.employee_data = []
        self.incomplete_data = []
        self.inactive_users = []
        self.failed_list = []
        self.completed_list = []
        self.user_name = "PayU_Test"
        self.password = "PayU#123"
        self.server = "smtp.office365.com"
        self.sender = "test.saurabh@payu.in"
        self.server_password = "Yog43112"
        self.reciever = "sourabh.kulkarni@payu.in"

    def message_creation(self, to_address, subject, body):
        message = f"""From: From Person <test.saurabh@payu.in>\nTo: To Person <{to_address}>
        MIME-Version: 1.0\nContent-type: text/html\nSubject: {subject}\n{body}"""
        return message

    def send_mail(self, message):
        message = message
        try:
            smtpserver = smtplib.SMTP(self.server, 587)
            smtpserver.starttls()
            smtpserver.login(self.sender, self.server_password)
            smtpserver.sendmail(self.sender, self.reciever, message)
        except smtplib.SMTPException as e:
            print(e)

    def get_darwin_data(self):
        try:
            url = "https://gonorth.darwinbox.in/masterapi/employee"
            api_key = "6d1fa04e43a2993d6ea8810481066fd9a03117d15194c45130daee30812ca0a6b2142e835221d91f95208cd2d9378d2b31640e60d617587d37455facb5b989c6"
            datasetKey = "6d2cc2a7ee49689882f1cdfd2dde955e5090c5e9f0109fd93d635021debcd583a96a398b8f9e9fe08e8e385f5ff582909e2158319263fbac385552726960bf6f"
            date_of_activation = "18-10-2022 00:00:00"
            print("Getting onboarding employee data from Darwin")
            body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "date_of_activation": date_of_activation})
            response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
            if response.status_code == 200:
                result = response.json()
                self.data = result["employee_data"]
            else:
                raise Exception(
                    f"Darwin API has given response status code of <b>{response.status_code}</b> while fetching new joinee data")
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Darwin API error while fetching new joinee data"
            body = f"""
            Hi all,\n

            {str(e)} \n

            Kindly look at the API for more details.
            """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def validate_data(self):
        try:
            print("validating employee data fetched from Darwin")
            for employee in self.data:
                emp = {}
                if employee["first_name"] and employee["employee_id"]:
                    # if employee["first_name"] and employee["employee_id"] and employee["department"] and employee[
                    #     "designation"] \
                    #         and employee["office_mobile_no"] and employee["group_company"]:
                    first_name = employee["first_name"].strip().split(" ")[0]
                    last_name = employee["last_name"].strip().split(" ")[0] if "last_name" in employee else ""
                    if last_name:
                        full_name = first_name + "." + str(last_name)
                    else:
                        full_name = first_name
                    if len(full_name) <= 16:
                        employee["full_name"] = full_name
                        employee["first_name"] = first_name
                        employee["last_name"] = last_name
                        self.employee_data.append(employee)
                    else:
                        emp["Name"] = first_name + " " + last_name
                        emp["ID"] = employee["employee_id"]
                        emp["error"] = "The length of first name + last name exceeds 16 characters"
                        self.incomplete_data.append(emp)
                else:
                    emp["Name"] = employee["first_name"]
                    emp["ID"] = employee["employee_id"]
                    emp["error"] = "Incomplete Employee data"
                    self.incomplete_data.append(employee)
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Error while validating data"
            body = f"""
            Hi all,\n

            {str(e)}\n

            Kindly look at the script for more details.
            """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def get_all_emails(self):
        try:
            email_list = []
            total_entries = 0
            server = Server('ldap://10.100.98.197', port=389, use_ssl=False)
            conn = Connection(server, user='test kumar', password='india@123')
            conn.bind()
            conn.search(search_base="ou=Upbhogyata,DC=Gurgaon,DC=local",
                        search_filter="(objectClass=*)",
                        search_scope=SUBTREE,
                        attributes=ALL_ATTRIBUTES,
                        get_operational_attributes=True,
                        paged_size=1000)
            total_entries += len(conn.response)
            for entry in conn.response:
                if 'userPrincipalName' in entry['attributes']:
                    email_list.append(entry['attributes']['userPrincipalName'])
            cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            while cookie:
                conn.search(
                    search_base="cn=users,DC=Gurgaon,DC=local",
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
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Error while connecting to AD"
            body = f"""
            Hi all,\n

             {str(e)}\n

             Kindly look at the AD for more details.
             """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def push_data_to_ad(self, item):
        try:
            print(f"Pushing {item['first_name']} {item['last_name']} data to AD")
            server = Server('ldap://10.100.98.197', port=389, use_ssl=False)
            conn = Connection(server, user='test kumar', password='india@123')
            conn.bind()
            # for index, item in enumerate(self.employee_data):
            email = item['company_email_id']
            last_name = item['last_name']
            first_name = item['first_name']
            if 'num' in item:
                num = item['num']
                last_name = last_name + str(num)
            name = first_name + last_name
            full_name = first_name + " " + last_name
            dn = f"cn={name},ou=Upbhogyata,DC=Gurgaon,DC=local"
            attr = {'givenName': first_name, 'userPrincipalName': email, 'SamAccountName': name,
                    'sn': last_name, 'mail': email, 'displayName': full_name, 'l': 'Bangalore',
                    'telephoneNumber': 1234567890, 'title': 'SE',
                    'manager': 'cn=OvertimeOT,ou=Upbhogyata,DC=Gurgaon,DC=local',
                    'department': 'Cyber Security',
                    'userAccountControl': 544}
            # attr = {'givenName': first_name, 'userPrincipalName': email, 'SamAccountName': name,
            #         'sn': last_name, 'mail': email, 'displayName': full_name, 'l': item['group_company'],
            #         'telephoneNumber': item['office_mobile_no'], 'title': item['designation'],
            #         'department': item['department'], 'manager': 'cn=OvertimeOT3,ou=Upbhogyata,DC=Gurgaon,DC=local',
            #         'userAccountControl': 544}
            response = conn.add(dn, object_class='user', attributes=attr)
            if response:
                print(f"{full_name} has been added to AD")
            else:
                self.failed_list.append(item)
            # conn.modify(dn, {'userAccountControl': (MODIFY_REPLACE, [544])})
            conn.unbind()
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Error while updating data in AD"
            body = f"""
            Hi all,\n

            {str(e)}\n

            Kindly look at the script for more details."""
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def create_email_ids(self):
        try:
            # self.email_list.sort()
            # emails = []
            # for email in self.email_list:
            #     emails.append(email.split("@")[0])
            for index, item in enumerate(self.employee_data):
                email_list = self.get_all_emails()
                email_list.sort()
                emails = []
                for email in email_list:
                    emails.append(email.split("@")[0])
                matched_emails = []
                full_name = item["full_name"].lower()
                for email in emails:
                    if full_name in email:
                        matched_emails.append(email)
                if len(matched_emails) == 0:
                    print(f"create a new mail id: {full_name}@Gurgaon.local")
                    email_id = full_name + "@Gurgaon.local"
                    self.employee_data[index]['company_email_id'] = email_id
                else:
                    if len(matched_emails) == 1:
                        print(f"This is the mail id: {full_name}1@Gurgaon.local")
                        email_id = full_name + "1@Gurgaon.local"
                        self.employee_data[index]['num'] = '1'
                        self.employee_data[index]['company_email_id'] = email_id
                    else:
                        matched_emails.sort()
                        last_num = int(matched_emails[-1][-1]) + 1
                        print(f"Mail id is: {full_name}{str(last_num)}@Gurgaon.local")
                        email_id = full_name + str(last_num) + "@Gurgaon.local"
                        self.employee_data[index]['num'] = str(last_num)
                        self.employee_data[index]['company_email_id'] = email_id
                # call push_data_to_ad here
                self.push_data_to_ad(item)
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Error while validating data"
            body = f"""
            Hi all,\n

            {str(e)}\n

            Kindly look at the script for more details."""
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def push_to_darwin(self):
        try:
            print("Updating new email ID to Darwin")
            url = "https://gonorth.darwinbox.in/UpdateEmployeeDetails/update"
            api_key = "0e0392ac13aff55e4b109c357b82d68e72e7fcbcf23c7ab1a235b4d9299093bf0508067be0241f5a05500200c5b209102073465fc10936b483452c302ce7ef69"
            for employee in self.employee_data:
                emp = {}
                email_id = employee['company_email_id']
                employee_id = employee['employee_id']
                body = json.dumps({"api_key": api_key, "email_id": email_id, "employee_id": employee_id})
                response = requests.post(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
                if response.status_code == 200:
                    emp['full_name'] = employee['company_email_id'].split("@")[0]
                    emp['email_id'] = employee['company_email_id']
                    self.completed_list.append(emp)
                else:

                    self.failed_list.append(emp)
            df = pd.json_normalize(self.completed_list)
            to_address = "sourabh.kulkarni@payu.in"
            subject = "New onboarded employees"
            body = f"""
            Hi all,\n

            Below is the list of users whose email id have been created.\n

            {df.to_html()}"""
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)
            if self.failed_list or self.incomplete_data:
                new_df = pd.json_normalize(self.failed_list)
                another_df = pd.json_normalize(self.incomplete_data)
                subject = "Employees that are not updated"
                body = f"""
                Hi all,\n 

                Below is the list of users whose email id has not been updated.\n

                {new_df.to_html()}

                Below is the list of users whose data is incomplete.\n

                {another_df.to_html()}
                """
                message = self.message_creation(to_address, subject, body)
                self.send_mail(message)
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Darwin API error while updating email ID to Darwin"
            body = f"""
            Hi all,

            {str(e)}
            Darwin failed to update the below mentioned employee list:
            str({self.failed_list})

            Kindly look at the API for more details.
                    """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def get_inactive_users(self):
        try:
            print("Fetching users to be deactivated")
            url = "https://gonorth.darwinbox.in/masterapi/employee"
            api_key = "6f1060b75a2e17c6b24cada6ad019456f7641271483ed19bf5dbd1f9bed933c36fd1a6f65115f6b50916ba5855de6056460d8379ac1f9db5c420e98a4fb5e16c"
            datasetkey = "edaf5b4719cafd6c47d7692d189a06ee09663b296a8a5dc7dc1beea3a5a9d8de9577f203256051929cfa23c56016a2de52da7c09ec1bce595e852ee149b96d2e"
            body = json.dumps({"api_key": api_key, "datasetKey": datasetkey, "last_modified": "01-09-2022"})
            response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
            if response.status_code == 200:
                result = response.json()
                self.inactive_users = result["employee_data"]
            else:
                raise Exception(
                    f"Darwin API has given response status code of <b>{response.status_code}</b> while fetching inactive users data")
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Darwin API error while fetching inactive users data"
            body = f"""
            Hi all,

            {str(e)}

            Kindly look at the API for more details.
            """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)

    def deactivate_users_ad(self):
        try:
            print("Deactivating users in AD")
            server = Server('ldap://10.100.98.197', port=389, use_ssl=False)
            conn = Connection(server, user='test kumar', password='india@123')
            conn.bind()
            dn = f"cn=OvertimeOT1,ou=Upbhogyata,DC=Gurgaon,DC=local"
            conn.modify(dn, {'userAccountControl': (MODIFY_REPLACE, [514])})
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Offboarded employee data"
            body = f"""
                    \nHi all,\n
                    The below account has been disabled:\n
                    Overtime OT1\n"""
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)
        except Exception as e:
            to_address = "sourabh.kulkarni@payu.in"
            subject = "Error while deactivating users in AD"
            body = f"""
             Hi all,\n

             {str(e)}\n

             Kindly look at the AD for more details.
             """
            message = self.message_creation(to_address, subject, body)
            self.send_mail(message)


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
    # Check for inactive users from Darwin API
    # ad.get_inactive_users()
    # # Make inactive users inactive in AD
    # ad.deactivate_users_ad()
    print(time.time() - start)
