# import time
# import logging
# import json
# from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE
# from ldap3.utils.log import set_library_log_detail_level, EXTENDED
#
#
# class AD:
#     def __init__(self):
#         self.employee_data = None
#
#     def get_darwin_data(self):
#         pass
#
#     def validate_data(self, employee_data):
#         employee_names = ['test.kumar', 'sourabh.kulkarni', 'ab.cd']
#         return employee_names
#
#     def get_all_emails(self):
#         # logging.basicConfig(filename='client_application_2.log', level=logging.ERROR)
#         # set_library_log_detail_level(EXTENDED)
#         total_entries = 0
#         server = Server('ldap://10.100.98.197', port=389, use_ssl=False)
#         conn = Connection(server, user='test kumar', password='Payu@1234')
#         conn.bind()
#         print(conn.bind())
#         conn.search(search_base="ou=Upbhogyata,DC=Gurgaon,DC=local",
#                     search_filter="(objectClass=*)",
#                     search_scope=SUBTREE,
#                     attributes=ALL_ATTRIBUTES,
#                     get_operational_attributes=True,
#                     paged_size=1000)
#         total_entries += len(conn.response)
#         email_list = []
#         for entry in conn.response:
#             if 'userPrincipalName' in entry['attributes']:
#                 email_list.append(entry['attributes']['userPrincipalName'])
#                 print(entry['attributes']['userPrincipalName'])
#         while True:
#             if 'controls' in conn.result and conn.result['controls']:
#                 cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#                 if cookie:
#                     conn.search(
#                         search_base="cn=users,DC=Gurgaon,DC=local",
#                         search_filter="(objectClass=*)",
#                         search_scope=SUBTREE,
#                         attributes=ALL_ATTRIBUTES,
#                         get_operational_attributes=True,
#                         paged_size=1000,
#                         paged_cookie=cookie
#                     )
#                     total_entries += len(conn.response)
#                     for entry in conn.response:
#                         if 'userPrincipalName' in entry['attributes']:
#                             email_list.append(entry['attributes']['userPrincipalName'])
#                             print(entry['attributes']['userPrincipalName'])
#                 else:
#                     break
#             else:
#                 break
#         conn.unbind()
#         return email_list
#
#     def create_email_ids(self, email_list, employee_data):
#         email_list.sort()
#         emails = []
#         new_email_ids = []
#         for email in email_list:
#             emails.append(email.split("@")[0])
#         for employee in employee_data:
#             matched_emails = []
#             for email in emails:
#                 if employee in email:
#                     matched_emails.append(email)
#             if len(matched_emails) == 0:
#                 print(f"create a new mail id: {employee}@Gurgaon.local")
#                 # new_email_ids.append()
#             else:
#                 if len(matched_emails) == 1:
#                     print(f"This is the mail id: {employee}1@Gurgaon.local")
#                     # new_email_ids.append()
#                 else:
#                     matched_emails.sort()
#                     last_num = matched_emails[-1][-1] + 1
#                     print(f"Mail id is: {employee}{last_num}@Gurgaon.local")
#                     # new_email_ids.append()
#         return new_email_ids
#
#     def push_data_to_ad(self, employee_data):
#         server = Server('ldap://10.100.98.197', port=389, use_ssl=False)
#         conn = Connection(server, user='test kumar', password='Payu@1234')
#         conn.bind()
#         print(conn.bind())
#         dn = "cn=testnew3,ou=Upbhogyata,DC=Gurgaon,DC=local"
#         attr = {'givenName': 'test', 'userPrincipalName': 'test.new3@Gurgaon.local', 'SamAccountName': 'test.new3',
#                 'sn': 'new3'}
#         response = conn.add(dn, object_class='user', attributes=attr)
#         conn.modify(dn, {'userAccountControl': (MODIFY_REPLACE, [544])})
#         print(response)
#         conn.unbind()
#         return response
#
#     def push_to_darwin(self):
#         pass
#
#
# if __name__ == '__main__':
#     start = time.time()
#     ad = AD()
#     # Get details from Darwin API
#     new_employees = ad.get_darwin_data()
#     # Validate the data if it is in the right format
#     output = ad.validate_data(new_employees)
#     # Get all the employee email ids
#     emails = ad.get_all_emails()
#     # create a sample email id and check if it already exists
#     email_ids = ad.create_email_ids(emails, output)
#     # Push data to AD
#     result = ad.push_data_to_ad(new_employees)
#     # Now send the email id back to Darwin
#     response = ad.push_to_darwin()
#     print(time.time()-start)
#
# import requests
from requests.auth import HTTPBasicAuth
# import json
# url = "https://payu.darwinbox.in/masterapi/employee"
# api_key = "c4e198e1fbcf222e06de5b186b63379f80be9e7d13b5ef150a612fbcb40b92905408c99e85e93c9c6352aef6f568733a57a23b59af7a9c894928ee40530cf28f"
# datasetKey = "40ff43819f9100af9d938ba850d48d6af99dd7b2a3ed2c9f384d806b67924e7550394a3999884b3d017f062432f356edfa1b95ec52ffc514e5bd85a726cfb314"
# date_of_activation = "18-10-2022 00:00:00"
# user_name = "payu_api"
# password = "3MzkqYPQJjNvQTX$By8km3Mm@4qdK8IHHYej3&QCav1g@imXh&MqonZSOVAAN9UN"
# print("Getting onboarding employee data from Darwin")
# body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "last_modified": date_of_activation})
# response = requests.get(url, auth=HTTPBasicAuth(user_name, password), data=body)
# if response.status_code == 200:
#     result = response.json()
#     print()
from datetime import timedelta, datetime, date
l_date = '05-Apr-2023'
another_date = date.today()
today = datetime.now()
s = datetime.strptime(l_date, "%d-%b-%Y").date()
if datetime.strptime(l_date, "%d-%b-%Y").date() >= another_date:
    print("Yes")
print(date.today())
l_date = datetime.strptime(l_date, "%d-%m-%Y")
# print(l_date-another_date)
lwd = l_date - timedelta(days=30)
print(l_date - timedelta(days=30))
if today >= lwd:
    print("Yes")
else:
    print("No")
data = {}
if not data:
    print("Sure")
else:
    print("No")

