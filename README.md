# SMTP-Email-Sender

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

SMTP-Email-Sender is a lightweight Python module that simplifies sending emails via SMTP. It supports plain text and HTML content, file attachments with proper RFC2231 encoding, multiple recipients (including CC), and even batch email sending using templates. Its built-in debug mode and detailed logging make testing and troubleshooting a breeze!

## Features

- **Simple Email Composition:** Create emails with plain text or HTML content.
- **File Attachments:** Easily attach files with correct encoding for diverse file names.
- **Multiple Recipients & CC:** Send emails to multiple recipients and include CC lists.
- **Template-Based Batch Emails:** Use dynamic placeholders to personalize bulk emails.
- **Debug Mode:** Log email content and recipients without sending, perfect for testing.
- **Robust Error Handling:** Clear, descriptive error messages and logging for easier debugging.

## Requirements

- **Python:** 3.6+
- **Standard Libraries:** `smtplib`, `email`, `logging`, `typing`

_No external dependencies are required!_

## Installation

You can install SMTP-Email-Sender using pip:

```bash
pip install smtp-email-sender
```

Alternatively, you can clone the repository and integrate it into your project:

```bash
git clone https://github.com/ErhanTurker01/SMTP-Email-Sender.git
```

Or, you can copy the source file into your project directory.

## Usage

### 1. Sending a Simple Email

Below is a basic example of sending a plain text email:

```python
from smtp_email_sender import EmailSender, email_text

# Initialize the EmailSender with your SMTP credentials.
sender = EmailSender(
    sender="your_email@example.com",
    password="your_password",
    smtp_server="smtp.example.com",
    smtp_port=587,
    use_tls=True,
    debug=True  # Set to False to actually send the email.
)

# Create and send the email message.
sender.create_message(
    receiver="recipient@example.com",
    subject="Hello from SMTP-Email-Sender"
).attach(
    email_text("This is a test email sent using SMTP-Email-Sender!", "plain")
).sendmail()

# Finalize and close the SMTP connection.
sender.finish()
```

### 2. Sending Emails Using a Template

Send personalized emails to multiple recipients with dynamic content:

```python
from smtp_email_sender import EmailSender

# Initialize the EmailSender.
sender = EmailSender(
    sender="your_email@example.com",
    password="your_password",
    smtp_server="smtp.example.com",
    smtp_port=587,
    use_tls=True,
    debug=True  # Toggle debug mode as needed.
)

# Define your email template with placeholders.
template = "Hi {name},\n\nWe are excited to invite you to {event}! See you there."

# Define the recipient data.
mails = ["alice@example.com", "bob@example.com"]
subjects = ["Invitation to Python Meetup", "Invitation to Python Meetup"]
placeholders = [
    {"name": "Alice", "event": "the Python Meetup"},
    {"name": "Bob", "event": "the Python Meetup"}
]

# Optionally, define CC lists and file attachments (here, none).

# Send the templated emails.
sender.sendmail_from_template(
    template=template,
    mails=mails,
    subjects=subjects,
    text_type="plain",
    placeholders=placeholders
)

# Finalize the process.
sender.finish()
```

### 3. Attaching Files

Attach files to your email with proper encoding:

```python
from smtp_email_sender import EmailSender, email_file, email_text

# Initialize the EmailSender.
sender = EmailSender(
    sender="your_email@example.com",
    password="your_password",
    smtp_server="smtp.example.com",
    smtp_port=587,
    use_tls=True,
    debug=True
)

# Create a message and attach both text content and a file.
sender.create_message("recipient@example.com", "Monthly Report") \
      .attach(email_text("Please find the monthly report attached.", "plain")) \
      .attach(email_file("path/to/report.pdf", "Monthly_Report.pdf")) \
      .sendmail()

# Close the connection.
sender.finish()
```

### 4. Using SMTP-Email-Sender with Gmail

#### Steps to Use Gmail with SMTP-Email-Sender:

1. **Enable 2-Step Verification:**  
   Sign in to your Google account and enable 2-Step Verification.

2. **Generate an App Password:**  
   After enabling 2-Step Verification, go to the [App Passwords](https://myaccount.google.com/apppasswords) section. Select the app (e.g., "Mail") and device (e.g., "Other" and name it "SMTP-Email-Sender") and generate an app password. Save this password securely.

3. **Update Your Code:**  
   Use your full Gmail address as the sender and the generated app password in your code. Here's an example:

```python
from smtp_email_sender import EmailSender, email_text

# Replace these values with your Gmail details.
gmail_address = "your_gmail@gmail.com"
app_password = "your_generated_app_password"

# Initialize the EmailSender using Gmail's SMTP server.
sender = EmailSender(
    sender=gmail_address,
    password=app_password,
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    use_tls=True,
    debug=True  # Set to False to send the email for real.
)

# Create and send the email message.
sender.create_message(
    receiver="recipient@example.com",
    subject="Hello from SMTP-Email-Sender via Gmail"
).attach(
    email_text("This email was sent using Gmail's SMTP server and an App Password.", "plain")
).sendmail()

# Finalize and close the SMTP connection.
sender.finish()
```

Follow these steps to securely send emails via Gmail using SMTP-Email-Sender.

## Logging & Debugging

SMTP-Email-Sender uses Python's built-in `logging` module to provide detailed feedback. When in debug mode (`debug=True`), the module logs the recipients, email content, and any errors without actually sending emails—ideal for development and testing.

Check your console or log files to see these detailed messages, which can help diagnose issues with SMTP connection, authentication, or file attachments.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please:
- Fork the repository.
- Create a new branch (`git checkout -b feature/YourFeature`).
- Commit your changes (`git commit -m 'Add some feature'`).
- Push to the branch (`git push origin feature/YourFeature`).
- Open a pull request.

Feel free to open issues for bug reports or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Happy emailing with **SMTP-Email-Sender**!
