import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import encode_rfc2231
from typing import Union
import logging

logger = logging.getLogger(__name__)

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
            mime_file = MIMEBase("application", "octet-stream")
            mime_file.set_payload(f.read())
            encoders.encode_base64(mime_file)

            encoded_attachment_name = encode_rfc2231(attachment_file_name, charset="utf-8")
            mime_file.add_header(
                "Content-Disposition",
                f"attachment; filename*={encoded_attachment_name}"
            )
    except FileNotFoundError as e:
        msg = f"File '{path}' not found! Please verify the path and check file permissions."
        logger.error(msg)
        raise ValueError(msg) from e
    return mime_file

class EmailSender:
    def __init__(
        self,
        sender: str,
        password: str,
        smtp_server: str,
        smtp_port: int = 587,
        use_tls: bool = True,
        debug: bool = False
    ) -> None:
        """
        Initialize the EmailSender by connecting to an SMTP server.
        
        :param sender: The sender's email address.
        :param password: The sender's password or app-specific password.
        :param smtp_server: The address of the SMTP server (e.g., "smtp.example.com").
        :param smtp_port: The port of the SMTP server. Default is 587.
        :param use_tls: Whether to use TLS encryption. Default is True.
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
            self.server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                self.server.starttls()
            self.server.login(self.sender, self.password)
            if self.debug:
                logger.debug("Connected to SMTP server (%s:%s) and logged in successfully.", smtp_server, smtp_port)
        except Exception as e:
            msg = ("Error during SMTP connection or login. Please verify your SMTP settings, "
                   "ensure that your sender credentials are correct, and check your network connectivity.")
            logger.error("%s Exception: %s", msg, e)
            raise e
    
    def create_message(
        self,
        receiver: str,
        subject: str,
        cc: list[str] = None,
    ):
        """
        Create a new email message.
        
        :param receiver: The primary recipient's email address.
        :param subject: The subject of the email.
        :param cc: Optional list of email addresses for CC.
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
        
        return self
    
    def attach(self, attachment: Union[MIMEText, MIMEBase]):
        """
        Attach an additional part (text or file) to the email.
        
        :param attachment: The attachment to add.
        :return: self (for method chaining).
        :raises ValueError: If the message is not yet created.
        """
        if self.message is None:
            msg = "Message is not created! Please call create_message() before attaching content."
            logger.error(msg)
            raise ValueError(msg)
        self.message.attach(attachment)
        return self
        
    def sendmail(self) -> None:
        """
        Send the email message. In debug mode, the email is not actually sent but its details are logged.
        
        :raises ValueError: If the message is not created.
        """
        if self.message is None:
            msg = "Message is not created! Please create a message before sending."
            logger.error(msg)
            raise ValueError(msg)
        
        recipients = [self.receiver]
        if self.cc:
            if isinstance(self.cc, list):
                recipients.extend(self.cc)
            else:
                recipients.append(self.cc)
        
        try:
            if self.debug:
                logger.debug("Email would be sent to: %s", ", ".join(recipients))
                logger.debug("Email content:\n%s", self.message.as_string())
            else:
                self.server.sendmail(self.sender, recipients, self.message.as_string())
                logger.info("E-mail successfully sent to %s", ", ".join(recipients))
            self.message = None
        except Exception as e:
            msg = ("An error occurred while sending the email. "
                   "Please check your network connection and ensure that the SMTP server is accessible.")
            logger.error("%s Exception: %s", msg, str(e))
            self.errors.append(self.receiver)
    
    def sendmail_from_template(
        self,
        template: str,
        mails: list[str],
        subjects: list[str],
        text_type: str = "plain",
        placeholders: list[dict[str, str]] = None,
        ccs: list[list[str]] = None,
        files: list[list[tuple[str, str]]] = None
    ):
        """
        Send emails based on a template to multiple recipients.

        This method iterates over the lists of emails, subjects, optional placeholders, CC lists, and file attachments.
        For each recipient, the email content is generated by formatting the template with the provided placeholders 
        (if any). If in debug mode, the email details are logged rather than being sent.

        Note: This method may propagate exceptions raised by create_message, attach, or sendmail.
        If an error occurs for one email, it is logged with its index and recipient email, and the method continues 
        to the next email.

        :param template: The email body template, which can include format placeholders.
        :param mails: A list of recipient email addresses.
        :param subjects: A list of subjects corresponding to each email.
        :param text_type: The type of text (e.g., "plain" or "html") for the email content.
        :param placeholders: An optional list of dictionaries for template formatting for each email.
        :param ccs: An optional list of CC lists corresponding to each email.
        :param files: An optional list of lists of tuples, where each tuple contains (file_path, attachment_file_name),
                      corresponding to each email.
        :raises ValueError: If the lengths of the provided lists do not match or if a required parameter is invalid.
        """
        if files and len(files) != len(mails):
            msg = "Number of file attachment lists do not match the number of mails!"
            logger.error(msg)
            raise ValueError(msg)
        
        if subjects and len(subjects) != len(mails):
            msg = "Number of subjects do not match the number of mails!"
            logger.error(msg)
            raise ValueError(msg)
        
        if ccs and len(ccs) != len(mails):
            msg = "Number of CC lists do not match the number of mails!"
            logger.error(msg)
            raise ValueError(msg)
        
        if placeholders and len(placeholders) != len(mails):
            msg = "Number of placeholders do not match the number of mails!"
            logger.error(msg)
            raise ValueError(msg)
        
        def ensure_list(lst, length):
            """If lst is None, return a list of None values of given length."""
            return lst if lst is not None else [None] * length
        
        placeholders = ensure_list(placeholders, len(mails))
        ccs = ensure_list(ccs, len(mails))
        subjects = ensure_list(subjects, len(mails))
        files = ensure_list(files, len(mails))
                
        for idx, (mail, placeholder, cc, subject, file) in enumerate(zip(mails, placeholders, ccs, subjects, files), start=1):
            try:
                if not mail:
                    msg = f"Email address at index {idx} is empty! Please check your mails list."
                    logger.error(msg)
                    raise ValueError(msg)
                
                if not subject:
                    msg = f"Subject at index {idx} is empty! Please check your subjects list."
                    logger.error(msg)
                    raise ValueError(msg)
                
                self.create_message(mail, subject, cc)
                
                if placeholder:
                    try:
                        content = template.format_map(placeholder)
                    except Exception as e:
                        msg = (f"Error formatting template for email at index {idx} with recipient '{mail}'. "
                               "Please verify that your placeholder keys match the template.")
                        logger.error("%s Exception: %s", msg, e)
                        raise ValueError(msg) from e
                    self.attach(email_text(content, text_type))
                else:
                    self.attach(email_text(template, text_type))
                
                if file:
                    for path, file_name in file:
                        self.attach(email_file(path, file_name))
                
                self.sendmail()
            except Exception as e:
                logger.error("Error processing email at index %d for recipient '%s': %s. "
                             "Please check the input values and SMTP configuration.", idx, mail, e)
                self.errors.append(mail)
        
    
    def finish(self):
        """
        Finalize the email sending process, report any errors, and close the SMTP connection.
        """
        if not self.errors:
            logger.info("All mails sent successfully")
        else:
            logger.error("Errors occurred while sending emails to: %s", self.errors)
        try:
            self.server.quit()
        except Exception as e:
            logger.error("An error occurred while closing the SMTP connection: %s", e)
