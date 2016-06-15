def sendmail(self, recipient, subject, message):
    from boto.ses import connect_to_region

    conn = connect_to_region('us-east-1', aws_access_key_id=self.settings.AWS_KEY, aws_secret_access_key=self.settings.AWS_SECRET)
    conn.send_email(
            self.settings.EMAIL_SENDER, 
            subject,
            message, 
            [recipient]
        )
