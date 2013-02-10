import wx
from sil_dialogs import *

SilhouettoVersion = "0.0.1"


DIALOG_SIZE = wx.Size(1024,768)
ID_ADD_OBJECT_BUTTON = 1002


class SilhouettoApp(wx.App):
    def OnInit(self):
        self.dlg = SilhouettoMainDialog(None, -1 )
        self.dlg.Show(True) 
        self.SetTopWindow(self.dlg)
        return True
  
if __name__ == "__main__":
    app = SilhouettoApp(0)
    app.MainLoop()
    app.Destroy()