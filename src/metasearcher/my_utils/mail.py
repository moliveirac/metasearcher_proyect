import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse


def send_mail(destiny_mail, subject, body):
    # Account
    notifier_account = 'metasearcher.notifier@gmail.com'
    notifier_p = 'rhwsgelgyphqjgus'

    # Mail object
    mail_to_send = MIMEMultipart()
    mail_to_send['From'] = notifier_account
    mail_to_send['To'] = destiny_mail
    mail_to_send['Subject'] = subject
    mail_to_send.attach(MIMEText(body, 'plain'))

    # Establish connection to server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(notifier_account, notifier_p)

    # Send mail
    server.sendmail(mail_to_send['From'], mail_to_send['To'], mail_to_send.as_string())

    # Close connection
    server.quit()

def notify_new_results(full_name, queries, destiny_mail):
    # Mail data
    subject = "New results on your saved queries!"

    queries_listed = ""

    for source, query in queries:
        queries_listed += "\n\t\"" + query + "\" (http://localhost:8080/notifier/saved_query_results/?query=" + urllib.parse.quote(query) + "&source=" + urllib.parse.quote(source) + ")"

    body = "Hi, " + full_name + "!\n\n" + "We have some new results for your queries, listed bellow: " + queries_listed + "\n\nCome see them!\n\n\nMetasearcher notifier application system."

    send_mail(destiny_mail, subject, body)