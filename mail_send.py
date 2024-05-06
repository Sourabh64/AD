import smtplib

server = "smtp.office365.com"
sender = "HRMS.Notification@payu.in"
reciever = ["sourabh.kulkarni@payu.in"]
cc = ['sourabh.kulkarni@payu.in']
attach = "code.txt"
message = f"""From: From Person <HRMS.Notification@payu.in>
To: Sourabh Kulkarni <sourabh.kulkarni@payu.in>
CC: Sourabh Kulkarni <sourabh.kulkarni@payu.in>
Content-type: text/html
Subject: SMTP HTML e-mail test

This is an e-mail message to be sent in HTML format

<b>This is HTML message.</b>
<h1>This is headline.</h1>
<p> ignore this mail </p>
"""

try:
    smtpserver = smtplib.SMTP(server, 587)
    # smtpserver.ehlo()
    smtpserver.starttls()
    # smtpserver.ehlo()
    smtpserver.login("HRMS.Notification@payu.in", "Dux63612")
    recievers = reciever + cc
    smtpserver.sendmail(sender, recievers, message, attach)
    print("sent")
except smtplib.SMTPException as e:
    print("Here"+str(e))
# a = ["ab.cd", "ab.cd1", "ab.cd2", "sample"]
# b = "ab"
# for i in a:
#     if b in i:
#         print(b, i)
