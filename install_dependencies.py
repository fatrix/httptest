def func(self):
        import os, sys
        installed = []
        #for module in ['python-tutum', 'python-firebase', 'ushlex']:
        for module in ['boto']:
                try:
                        import module
                        installed.append(module)
                except Exception:
                        pip = os.path.join(os.path.dirname(sys.executable), "pip")
                        installed.append(os.popen("%s install %s" % (pip, module)).read())
        return installed