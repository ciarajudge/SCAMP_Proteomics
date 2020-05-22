#!/usr/bin/env python

import smtplib  
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


fromaddr = "ribopipe@gmail.com"
toaddr = "judge.ciara@gmail.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "xyz"
body = "hello"
msg.attach(MIMEText(body, 'html'))
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "Ribosome")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
print "sent"


