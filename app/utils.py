def sendmail(self, recipients, subject, message):
    from boto.ses import connect_to_region

    self.debug(self.rid, "sendmail to: "+str(recipients))

    conn = connect_to_region('us-east-1', aws_access_key_id=self.settings.AWS_KEY, aws_secret_access_key=self.settings.AWS_SECRET)
    result = conn.send_email(
            self.settings.EMAIL_SENDER, 
            subject,
            None,
            to_addresses=recipients,
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
        url = "/userland/%s/httptest/static/test.html?testid=%s&version=%s" % (self.settings.RUNTIME_USER, id, version)

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

    self.debug(self.rid, "get report from url: "+str(html_url))

    r = requests.get(html_url)
    if r.status_code != 200:
        raise Exception("Loading of URL '%s' failed with status_code %s" % (html_url, status_code))
    if not subject:
        subject = "HTTPTest - Report %s" % name
    if type(email) is not list:
        email = [email]
    result = sendmail(self, email, subject, r.text)
    return result

def get_ssl_info(self, host, port):
        """
        http://unix.stackexchange.com/questions/104623/how-to-get-servers-ssl-certificate-in-a-human-readable-form
        HOST, PORT
        """
        import socket
        import ssl

        self.debug(self.rid, "get_ssl_info for %s:%s" % (host, port))

        CA_CERTS = "/etc/pki/tls/certs/ca-bundle.trust.crt"

        def getcert(addr, timeout=None):
                """Retrieve server's certificate at the specified address (host, port)."""
                # it is similar to ssl.get_server_certificate() but it returns a dict
                # and it verifies ssl unconditionally, assuming create_default_context does
                sock = socket.create_connection(addr, timeout=timeout)
                sslsock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED,
                                                                           ca_certs=CA_CERTS,
                                                                           ciphers=("HIGH:-aNULL:-eNULL:"
                                                                                                "-PSK:RC4-SHA:RC4-MD5"))
                cert = sslsock.getpeercert()
                sock.close()
                return cert

        cert = getcert((host, int(port)))
        from datetime import datetime
        expire_date = datetime.strptime(cert['notAfter'],
                                            "%b %d %H:%M:%S %Y %Z")
        daysLeft = expire_date - datetime.now()

        for subject_item in cert['subject']:
#            print subject_item[0]
            if subject_item[0][0] == "commonName":
                commonName = subject_item[0][1]

        cert_dict = {}
        cert_dict['notBefore'] = cert['notBefore']
        cert_dict['notAfter'] = cert['notAfter']
        cert_dict['serialNumber'] = cert['serialNumber']
        cert_dict['issuer'] = cert['issuer'][2][0][1]
        #cert_dict['subject'] = cert['subject'][0][0][1]
        #cert_dict['fullSubject'] = cert['subject']
        cert_dict['daysLeft'] = daysLeft.days
        #cert_dict['fullCert'] = cert
        cert_dict['commonName'] = commonName
        return cert_dict

