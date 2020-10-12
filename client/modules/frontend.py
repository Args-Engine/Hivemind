import os
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import types
from typing import NoReturn

from client.session import Session
from common.module_base import ModuleBase
from common.update_returns import ApplicationExit
from messages.workspace_request import WorkspaceRequest


class FrontendModule(ttk.Frame, ModuleBase):
    def handle(self, message_name: str, message_value: WorkspaceRequest, session: Session) -> NoReturn:
        print("Frontend received message " + message_name)

    def __init__(self, master=tk.Tk()):
        ModuleBase.__init__(self, [])
        ttk.Frame.__init__(self, master)
        self.session: Session = None
        self.should_close = False

        if os.name == 'nt':
            ttk.Style().theme_use('vista')

        self.gui = types.SimpleNamespace()
        self.var = types.SimpleNamespace()
        self.atomic = types.SimpleNamespace()

        self.master = master
        self.pack()

        self.build_gui()
        self.configure_gui()
        self.pack_gui()

        self.config(height='200', width='200')
        self.pack(ipady='50', side='top')

        self.middleware = None

        self.bind('<Destroy>', self.on_destroy_event)

    def build_gui(self):
        self.var.address = tk.StringVar(self, "localhost")
        self.gui.address = ttk.Entry(self)

        self.var.location = tk.StringVar(self, "insert path")
        self.gui.location = ttk.Entry(self)

        self.atomic.connected = False
        self.var.connected = tk.BooleanVar(self, False)
        self.gui.connected = ttk.Checkbutton(self)

        self.gui.choose_dir = ttk.Button(self, command=self.on_choose_dir_pressed)
        self.gui.send_commands = ttk.Button(self, command=self.on_send_commands_pressed)
        self.gui.connect_client = ttk.Button(self, command=self.on_connect_client_pressed)

    def configure_gui(self):
        self.gui.address.config(takefocus=False, textvariable=self.var.address)
        self.gui.location.config(takefocus=False, textvariable=self.var.location)
        self.gui.connected.config(state='disabled', text='connected', var=self.var.connected)
        self.gui.choose_dir.config(text='Choose')
        self.gui.send_commands.config(text='Send')
        self.gui.connect_client.config(text="Connect")

    def pack_gui(self):
        self.gui.address.pack(anchor='n', ipadx='50', padx='20', pady='20', side='left')
        self.gui.location.pack(anchor='n', ipadx='50', padx='20', pady='20', side='left')
        self.gui.connected.pack(side='bottom')
        self.gui.choose_dir.pack(anchor='n', pady='20', side='left')
        self.gui.send_commands.pack(anchor='n', pady='20', side='left')
        self.gui.connect_client.pack(anchor='n', pady='20', side='left')

    def onRegister(self, modules, middleware):
        if getattr(middleware, 'addr', None) is not None:
            self.middleware = middleware

    def onUpdate(self):
        if not self.should_close:
            self.master.update()
        else:
            return ApplicationExit()

        for k, v in vars(self.atomic).items():
            if k in vars(self.var):
                vars(self.var)[k].set(v)

    def onConnect(self, session):
        self.atomic.connected = True
        self.session = session
        # self.gui.location.config(state='disabled')

    def on_destroy_event(self, event):
        self.should_close = True

    def on_choose_dir_pressed(self):
        name = filedialog.askdirectory()
        self.var.location.set(name)

    def on_send_commands_pressed(self):
        if self.session is not None:
            self.session.to_send.put(WorkspaceRequest())
            self.session['workspace-base-path'] = self.var.location.get()

    def on_connect_client_pressed(self):
        if self.middleware is not None:
            self.middleware.addr = self.var.address.get()
