import smtplib
content="Hello World"
mail=smtplib.SMTP('smtp.ionos.de', 587)
mail.ehlo()
mail.starttls()
sender='zoho@cannoba.de'
recipient='hhxblnde@gmail.com'
mail.login('zoho@cannoba.de','Buntebluete0!')
mail.sendmail(sender, recipient, content)
mail.close()