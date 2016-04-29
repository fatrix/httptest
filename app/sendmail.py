def func(self):
        import sys
        from boto.ses import connect_to_region

        conn = connect_to_region('us-east-1', aws_access_key_id=self.settings.AWS_KEY, aws_secret_access_key=self.settings.AWS_SECRET)
        conn.send_email(
        self.settings.EMAIL_SENDER,
        'apy.io: User is interested:',
        '%s | %s | %s' % (
                        self.GET.get('?name'),
                        self.GET.get('email'),
                        self.GET.get('why')),
        [self.settings.EMAIL_RECIPIENT])
        return self.responses.JSONResponse(json.dumps(self.GET))
