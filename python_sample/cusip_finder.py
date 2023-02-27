from blkdbi import DataObject
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

class CusipFinder:
    
    def __init__(self, search_table_name: str):
        self.search_table_name = search_table_name
        self.email_template_path = "templates/message.txt"
        self.smtp_host = "smtp.mycompany.com"
        self.dobj = DataObject("DEREAD")
        
    def parse_file(file_path: str):
        """read the file contains list of cusip and parse it to a list"""
        with open(file_path, "r") as f:
            cusip_list = [row.rstrip() for row in f.readlines()]
            
    def search_cusip(self, cusip_list: list) -> list:
        """search the cusip in the search table"""
        results = {}
        for cusip in cusip_list:
            sql = "SELECT cusip, cusip_type FROM %s WHERE cusip == %s" % (self.search_table_name, cusip)
            results[cusip] = self.dobj.do_sql(sql)
        return results
        
    def render_template(self, results: dict, cusip_list: list):
        # check if template exists
        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(self.email_template_path)
        return templ.render(name=self.receiver_name, results=results, cusip=cusip_list)
    
    def send_email(self, to, cc=None, bcc=None, subject=None, body=None):
        
        to_list = to + cc + bcc
        to_list = filter(None, to_list) # remove null emails

        msg = MIMEMultipart('alternative')
        msg['From']    = self.sender
        msg['Subject'] = subject
        msg['To']      = ','.join(to)
        msg['Cc']      = cc
        msg['Bcc']     = bcc
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(host=self.smtp_host)
        print(f"Send email from {self.sender} to {to}, cc: {cc}, bcc: {bcc}")
        server.sendmail(self.sender, to_list, msg.as_string())
        server.quit()
        
    def main_process(self, file_path: str, receiver: list, cc: list, bcc: list):
        cusip_list = self.parse_file(file_path)
        results = self.search_cusip(cusip_list)
        template = self.render_template(
            receiver=receiver, 
            results=results, 
            cusip_list=cusip_list
        )
        self.send_email(
            to=receiver, 
            cc=cc, 
            bcc=bcc, 
            subject="CUSIP Search Result", 
            body=template
        )
        