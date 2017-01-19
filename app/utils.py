import pprint
from collections import OrderedDict

def debug():
    from remote_pdb import RemotePdb
    RemotePdb('127.0.0.1', 4444).set_trace()

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
                context = ssl._create_stdlib_context()
                context.set_ciphers(("HIGH:-aNULL:-eNULL:-PSK:RC4-SHA:RC4-MD5"))
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_verify_locations(CA_CERTS)

                sock = socket.create_connection(addr, timeout=timeout)
                sslsock = context.wrap_socket(sock, server_hostname=addr[0])
                cert = sslsock.getpeercert()
                sock.close()
                return cert

        cert = getcert((host, int(port)))
        from datetime import datetime
        expire_date = datetime.strptime(cert['notAfter'],
                                            "%b %d %H:%M:%S %Y %Z")
        daysLeft = expire_date - datetime.now()

        for subject_item in cert['subject']:
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


class TableStructure(object):
    """
    #structure = {
    #    'row1':
    #        {$
    #            'col1':
    #                [ 
    #                    "content1",
    #                    "content2"
    #                ]
    #        }
    #}

    >>> table = TableStructure()
    >>> table.add_column("col1")
    >>> table.add_column("col2")
    >>> table.add_row("row1")
    >>> table.add_row("row2")
    >>> table.add_cell("row1", "col1", "row1/col1")
    >>> table.add_cell("row1", "col1", "row1/col1/cell2")
    >>> table.add_cell("row1", "col2", "row1/col2")
    >>> table.add_cell("row2", "col1", "row2/col1")
    >>> table.add_cell("row2", "col2", "row2/col2")
    >>> print(table.rows)
    OrderedDict([('row1', OrderedDict([('col1', ['row1/col1', 'row1/col1/cell2']), ('col2', ['row1/col2'])])), ('row2', OrderedDict([('col1', ['row2/col1']), ('col2', ['row2/col2'])]))])
    >>> print table.html()
    <table class="table"><thead><tr><th>Name</th><th>col1</th><th>col2</th></tr></thead><tbody><tr><td>row1</td><td>row1/col1 | row1/col1/cell2</td><td>row1/col2</td></tr><tr><td>row2</td><td>row2/col1</td><td>row2/col2</td></tr></tbody></table>
    >>> # new
    >>> table = TableStructure()
    >>> table.add_columns(["col1", "col2"])
    >>> table.add_rows(["row1", "row2"])
    >>> placeholder = "placeholder"
    >>> table.add_cell("row1", "col1", "row1/col1", placeholder=placeholder)
    >>> table.add_cell("row1", "col1", "row1/col1/cell2", placeholder=placeholder)
    >>> table.add_cell("row1", "col2", "row1/col2", placeholder=placeholder)
    >>> table.add_cell("row2", "col1", "row2/col1", placeholder=placeholder)
    >>> table.add_cell("row2", "col2", "row2/col2", placeholder=placeholder)
    >>> #table.get_cell("row1", "col1")
    >>> #table.get_cell("row2", "col1")
    >>> #table.get_cell("row1", "col2")
    >>> #table.get_cell("row2", "col2")
    """
    def __init__(self):
        #self.data = {}
        self.headers = ['Name',]
        self.rows = OrderedDict()

    def add_column(self, name):
        #print  "add column for %s (placeholder)" % name
        if name not in self.headers:
            self.headers.append(name)

    def add_columns(self, names):
        for name in names:
            self.add_column(name)

    def add_row(self, name):
        if name not in self.rows.keys():
            self.rows.update({name: OrderedDict()})

    def add_rows(self, names):
        for name in names:
            self.add_row(name)

    def add_cell(self, row_name, column, data, placeholder=None):
        row = self.rows.get(row_name, OrderedDict())
        if column not in row.keys():
            self.rows[row_name].update({column: [data]})
        else:
            self.rows[row_name][column].append(data)
        if placeholder:
            #print "try placeholder for row=%s column=%s" % (row_name, column)
            #for col in self.rows[row_name].keys():
            for col in self.headers:
                if col == "Name":
                    pass
                elif column == col:
                    #print "skip placeholder for row=%s column=%s to row=%s column=%s" % (row_name, column, row_name, col)
                    pass
                else:
                    #print "add placeholder for row=%s column=%s to row=%s column=%s" % (row_name, column, row_name, col)
                    r1 = self.rows[row_name].get(col, [])
                    r1.append(placeholder)


    def get_cell(self, row, column):
        row = self.rows.get(row)
        if column in row.keys():
            return row.get(column)
        else:
            raise Exception("cell does not exist")

    def html(self):
        headers = ""
        for header in self.headers:
            headers += "<th>%s</th>" % header
        rows = ""
        for row_k, row_v in self.rows.items():
            rows += "<tr>"
            rows += "<td>"+str(row_k)+"</td>"
            for col_k, col_v in row_v.items():
                rows += "<td>"
                for idx, cell_content in enumerate(col_v):
                    if idx > 0:
                        rows += " | "+cell_content
                    else:
                        rows += cell_content
                rows += "</td>"
            rows += "</tr>".format(row_name=row_k)
        table = '<table class="table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'.format(headers=headers, rows=rows)
        #print self.rows

        return table

if __name__ == "__main__":
        import doctest
        #doctest.testmod(raise_on_error=True)
        doctest.testmod()
