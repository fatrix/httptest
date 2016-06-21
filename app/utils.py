def sendmail(self, recipient, subject, message):
    from boto.ses import connect_to_region

    conn = connect_to_region('us-east-1', aws_access_key_id=self.settings.AWS_KEY, aws_secret_access_key=self.settings.AWS_SECRET)
    result = conn.send_email(
            self.settings.EMAIL_SENDER, 
            subject,
            None,
            to_addresses=[recipient],
            format="html",
            html_body=message
        )

    return result

def get_test_url(self, id, version=None, fq=False):
    if not version:
        version=2
    if "FRONTEND_API_URL" in self.settings:
        url = "%s/test/?testid=%s&version=%s" % (self.settings.FRONTEND_BASE_URL, id, version)
    else:
        url = "/fastapp/httptest/static/test.html?testid=%s&version=%s" % (id, version)

    if fq and not url.startswith("http"):
        url=self.settings.BASE_URL+url

    return url


def send_report(self, id, email, name, run=None, subject=None):
    from django.utils.http import urlquote
    import requests
    html_url = get_test_url(self, id, fq=True)
    html_url+="&nonav&noform&nooverview&nobuttons"
    if run:
        html_url+="&runonly=%s" % urlquote(run)
    r = requests.get(html_url)
    if r.status_code != 200:
        raise Exception("Loading of URL '%s' failed with status_code %s" % (html_url, status_code))
    if not subject:
        subject = "HTTPTest - Report %s" % name
    result = sendmail(self, email, subject, r.text)
    return result
