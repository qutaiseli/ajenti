import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis
from ajenti.requirements import *


class UpstartServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['Debian', 'Ubuntu']

    def test(self):
        SoftwareRequirement(self.app, 'Upstart/init', 'service').test()
       
    def list_all(self):
        r = []
        found = []
                
        if os.path.exists('/etc/init'):        
            for s in os.listdir('/etc/init'):
                if len(s) > 5:
                    s = s[:-5]
                    svc = apis.services.Service()
                    svc.name = s
                    if 'start/running' in shell('service %s status' % s):
                        svc.status = 'running'
                        r.append(svc)
                        found.append(s)
                    elif 'stop/waiting' in shell('service %s status' % s):
                        svc.status = 'stopped'
                        r.append(svc)
                        found.append(s)
                    
        for s in shell('service --status-all').split('\n'):
            if len(s) > 3 and s[3] != '?':
                name = s.split()[3]
                if not name in found:
                    found.append(name)
                    svc = apis.services.Service()
                    svc.name = name
                    svc.status = 'running' if s[3] == '+' else 'stopped'
                    r.append(svc)
            
        return sorted(r, key=lambda s: s.name)

    def get_status(self, name):
        s = shell('service ' + name + ' status')
        if 'start/running' in s:
            return 'running'
        return 'running' if 'is running' in s else 'stopped'

    def start(self, name):
        shell('service ' + name + ' start')

    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
