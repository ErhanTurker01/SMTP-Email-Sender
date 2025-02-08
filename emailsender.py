import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import encode_rfc2231
from typing import Union

def email_text(text: str, format_type: str = "plain") -> MIMEText:
    """Create a MIMEText object for plain or HTML text."""
    return MIMEText(text, format_type)

def email_file(path: str, attachment_file_name: str) -> MIMEBase:
    """
    Create a MIMEBase object for an attachment.

    :param path: The path to the file.
    :param attachment_file_name: The name of the attachment as it will appear in the email.
    :raises ValueError: If the file is not found.
    :return: A MIMEBase object representing the file.
    """
    try:
        with open(path, "rb") as f:
            file = MIMEBase("application", "octet-stream")
            file.set_payload(f.read())
            encoders.encode_base64(file)

            encoded_attachment_name = encode_rfc2231(attachment_file_name, charset="utf-8")
            file.add_header(
                "Content-Disposition",
                f"attachment; filename*={encoded_attachment_name}"
            )
    except FileNotFoundError:
        raise ValueError(f"File {path} not found!")
    return file

class EmailSender:
    def __init__(self, sender: str, password: str, debug: bool = False) -> None:
        """
        Initialize the EmailSender by connecting to the Gmail SMTP server.
        
        :param sender: The sender's email address.
        :param password: The sender's password or app-specific password.
        :param debug: If True, email sending is simulated with logging.
        """
        self.sender = sender
        self.password = password
        self.debug = debug
        self.message = None
        self.receiver = None
        self.cc = None 
        self.errors = []
        try:
            self.server = smtplib.SMTP("smtp.gmail.com", 587)
            self.server.starttls()
            self.server.login(self.sender, self.password)
            if self.debug:
                print("[DEBUG] Connected to SMTP server and logged in successfully.")
        except Exception as e:
            print(f"Error during SMTP connection or login: {e}")
            raise e
    
    def create_message(
        self,
        receiver: str,
        subject: str,
        cc: list[str] = None,
        html_content: str = None
    ):
        """
        Create a new email message.
        
        :param receiver: The primary recipient's email address.
        :param subject: The subject of the email.
        :param cc: Optional list of email addresses for CC.
        :param html_content: Optional HTML content to include as the body.
        :return: self (for method chaining).
        """
        self.message = MIMEMultipart("mixed")
        self.message["From"] = self.sender
        self.message["To"] = receiver
        self.message["Subject"] = subject

        if cc:
            self.cc = cc
            self.message["Cc"] = ", ".join(cc)

        self.receiver = receiver

        if html_content:
            self.message.attach(MIMEText(html_content, "html"))
        return self
    
    def attach(self, attachment: Union[MIMEText, MIMEBase]):
        """
        Attach an additional part (text or file) to the email.
        
        :param attachment: The attachment to add.
        :return: self (for method chaining).
        :raises ValueError: If the message is not yet created.
        """
        if self.message is None:
            raise ValueError("Message is not created!")
        self.message.attach(attachment)
        return self
        
    def sendmail(self) -> None:
        """
        Send the email message. In debug mode, the email is not actually sent but its details are logged.
        
        :raises ValueError: If the message is not created.
        """
        if self.message is None:
            raise ValueError("Message is not created!")
        
        recipients = [self.receiver]
        if self.cc:
            if isinstance(self.cc, list):
                recipients.extend(self.cc)
            else:
                recipients.append(self.cc)
        
        try:
            if self.debug:
                print(f"[DEBUG] Email would be sent to: {', '.join(recipients)}")
                print("[DEBUG] Email content:")
                print(self.message.as_string())
            else:
                self.server.sendmail(self.sender, recipients, self.message.as_string())
                print(f"E-mail successfully sent to {', '.join(recipients)}")
            self.message = None
        except Exception as e:
            print("An error occurred while sending email:", str(e))
            self.errors.append(self.receiver)
    
    def finish(self):
        """
        Finalize the email sending process, report any errors, and close the SMTP connection.
        """
        if not self.errors:
            print("All mails sent successfully")
        else:
            print(f"Error occurred while sending to: {self.errors}")
        self.server.quit()
