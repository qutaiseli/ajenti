from ajenti.com import implements
from ajenti.api import *
from ajenti.ui import *
from backend import *

class DaemonsPlugin(CategoryPlugin):
    text = 'Daemons'
    icon = '/dl/daemons/icon.png'
    folder = 'apps'

    def on_init(self):
        self.mgr = Daemons(self.app)
        
    def on_session_start(self):
        self._editing = None
        self._items = []
        
    def get_ui(self):
        ui = self.app.inflate('daemons:main')
        ts = ui.find('list')

        lst = self.mgr.list_all()
        self._items = lst
        for svc in lst:
            running = svc.running
            fn = '/dl/core/ui/stock/status-' + ('running.png' if svc.running else 'stopped.png')
            row = UI.DataTableRow(
                    UI.Image(file=fn),
                    UI.Label(text=svc.name),
                    UI.DataTableCell(
                        UI.MiniButton(text='Start', id='start/' + svc.name)
                            if not running else None,
                        UI.MiniButton(text='Stop', id='stop/' + svc.name) 
                            if running else None,
                        UI.MiniButton(text='Restart', id='restart/' + svc.name)
                            if running else None,
                        UI.MiniButton(text='Edit', id='edit/' + svc.name),
                        hidden=True
                    )
                  )
            ts.append(row)
            
        if self._editing != None:
            dlg = self.app.inflate('daemons:edit')
            dmn = filter(lambda x:x.name==self._editing, lst)[0]
            for o in options: #backend.options
                if o in dmn.opts:
                    dlg.find(o).set('value', dmn.opts[o])
            dlg.find('name').set('value', dmn.name)
            if 'respawn' in dmn.opts:
                dlg.find('respawn').set('checked', True)
            ui.append('main', dlg)
            
        return ui

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            d = Daemon('new', '')
            self._items.append(d)
            self.mgr.save(self._items)
            self._editing = 'new'
        if params[0] == 'start':
            self.mgr.start(params[1])
        if params[0] == 'restart':
            self.mgr.restart(params[1])
        if params[0] == 'stop':
            self.mgr.stop(params[1])
        if params[0] == 'edit':
            self._editing = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'dlgEdit':
            if vars.getvalue('action', None) == 'OK':
                dmn = filter(lambda x:x.name==self._editing, self._items)[0]
                
                #name
                dmn.name = vars.getvalue('name', '')
                if dmn.name == '':
                    return
                    
                # respawn checkbox
                respawn = vars.getvalue('respawn', '') == '1'
                if respawn and 'respawn' not in dmn.opts:
                    dmn.opts['respawn'] = None
                if not respawn and 'respawn' in dmn.opts:
                    del dmn.opts['respawn']
                    
                # other opts
                for o in options:
                    v = vars.getvalue(o, None)
                    if o == '' or o == None:
                        if o in dmn.opts:
                            del dmn.opts[o]
                    else:
                        dmn.opts[o] = v
                        
                        
                Daemons(self.app).save(self._items)
            self._editing = None
            
