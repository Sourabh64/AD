def get_lwd_details(self):
    try:

        url = "https://payu.darwinbox.in/masterapi/employee"
        api_key = "9caa60a7ce62d181c34beac524c463e3a5019a9c11bfd649535fe5ae18b37d362b22757eaa99e068a49836ae2f75566b0c76a65f452fcd137e7c52e52a319602"
        datasetKey = "6a64a1f89aad3c2e4fad545a0acdd5128924424ad38c5b0ea93f6a726441d5443b2adcbc29e7727e521026da734a1c7708b497cc25ca9927502c31b9ce589f2a"
        last_modified = "3-09-2022 00:00:00"
        print("Getting onboarding employee data from Darwin")
        body = json.dumps({"api_key": api_key, "datasetKey": datasetKey, "last_modified": last_modified})
        response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), data=body)
        print(response.status_code)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == 1:
                self.lwd_data = result["employee_data"]
                for employee in self.lwd_data:
                    if employee['is_on_notice_period'] == 'Yes':
                        date = employee['separation_agreed_last_date']
                        date = datetime.strptime(date, "%d-%m-%Y")
                        lwd = date - timedelta(days=30)
                        current_date = datetime.now()
                        if current_date >= lwd:
                            manager_email = employee['direct_manager_email']
                            print(manager_email)
                            hrbp_email = employee['hrbp_email_id']
                            print(hrbp_email)
                            manager_email = 'shrikant.ware@payu.in'
                            hrbp_email = 'sourabh.kulkarni@payu.in'
                            to_address = "<" + manager_email + ">" + ", " + "<" + hrbp_email + ">"
                            subject = "Employee Last working day less than 15 days"
                            body = f"""
                                    Hi all,<br>
                                    The here mentioned {employee['full_name']}'s last working day is falling less than 15 days.<br>
                                    kindly take necessary action in the Darwinbox portal.<br>
                                    <br>
                                    Thanks and Regards,<br>
                                    HRMS Portal
                                    """
                            message = self.message_creation(to_address, subject, body)
                            to_address = [manager_email, hrbp_email]
                            self.send_mail(message, to_address)

            else:
                self.lwd_data = {}
        else:
            raise Exception(
                f"Darwin API has given error while fetching new joining employee data <br>response status code: <b>{response.status_code}</b> <br>error: <b>{response.text}</b>")
    except Exception as e:
        to_address = "sourabh.kulkarni@payu.in"
        subject = "Darwin API error while fetching new joinee data"
        body = f"""
                    Hi all, <br>
                    {str(e)} <br>
                    Kindly test the API credentials for more details.
                    """
        message = self.message_creation(to_address, subject, body)
        self.send_mail(message, to_address)