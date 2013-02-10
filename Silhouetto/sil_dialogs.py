import numpy
import os 
import re
NEWLINE = "\n"  
separator = "\t"

import wx
from sil_image_control import *
from PIL import Image, ImageEnhance
from numpy import fft
#from wx import *
#import wx
#import wx.grid as  gridlib

DIALOG_SIZE = wx.Size(1024,768) 
SMALL_BUTTON_SIZE = wx.Size(20,20) 

ID_CALIBRATION_OKAY_BUTTON = 1001
ID_CALIBRATION_CANCEL_BUTTON = 1002

class SilObject( wx.Object ):
    def __init__(self):
        self.object_name = ""
        self.image_filename = ""
        self.chaincode = []
        self.point_list = []

    def SetName(self, name):
        self.object_name = name

    def SetChaincode(self, chaincode):
        self.chaincode = chaincode

    def SetPointList(self, point_list):
        self.point_list = point_list

class UnitCalibrationDialog( wx.Dialog ):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self,parent,id,'Calibration Unit', size = (320,180))
        self.panel = panel = wx.Panel( self, -1 )
        self.maintext = wx.StaticText(panel, -1, 'Enter length in millimeter:', style=wx.ALIGN_LEFT)
        self.length = wx.TextCtrl(panel,-1,'1')
        self.unittext = wx.StaticText( panel, -1, 'mm', style=wx.ALIGN_LEFT )
        
        self.okButton = wx.Button( panel, ID_CALIBRATION_OKAY_BUTTON, 'OK' )
        self.cancelButton = wx.Button( panel, ID_CALIBRATION_CANCEL_BUTTON , 'Cancel' )
        self.Bind( wx.EVT_BUTTON, self.OnOk, id=ID_CALIBRATION_OKAY_BUTTON )
        self.Bind( wx.EVT_BUTTON, self.OnCancel, id=ID_CALIBRATION_CANCEL_BUTTON )

        rowHeight = 22
        controlWidth = ( 150, 30, 20 )
        controls = ( self.maintext, self.length, self.unittext )
        x = 60
        y = 50
        for i in range( len( controls ) ):
            controls[i].SetSize( ( controlWidth[i], rowHeight ) )
            controls[i].SetPosition( ( x, y ) )
            x+= controlWidth[i]
        
        x = 110
        y = 100
        buttonWidth = ( 45, 45)
        buttons = ( self.okButton, self.cancelButton )
        for i in range( len( buttons ) ):
            buttons[i].SetSize( ( buttonWidth[i], rowHeight ) )
            buttons[i].SetPosition( ( x, y ) )
            x += buttonWidth[i] 
        
        panel.Fit()
        #self.Show()
        self.length.SetFocus()
        #self.forms['objname'] = wx.TextCtrl(panel, -1, '')
        
    def OnOk(self,event):
        self.EndModal(wx.ID_OK)   
    
    def OnCancel(self,event):
        self.EndModal(wx.ID_CANCEL)
    
    def GetValue(self):
        return self.length.GetValue()

ID_BNC_OK_BUTTON = 1001
ID_BNC_CANCEL_BUTTON = 1002

class BrightnessAndContrastDialog( wx.Dialog ):
    def __init__(self,parent,wid):
        wx.Dialog.__init__(self,parent,wid,'Brightness & Contrast', size = (360,360))
        self.panel = panel = wx.Panel( self, -1 )
        
        sizer1 = wx.BoxSizer( wx.HORIZONTAL )
        sizer2 = wx.BoxSizer( wx.HORIZONTAL )
        sizer3 = wx.BoxSizer( wx.HORIZONTAL )
        sizer4 = wx.BoxSizer( wx.VERTICAL )

        
        self.brightnessLabel= wx.StaticText( panel, -1, 'Brightness', style=wx.ALIGN_CENTER)
        self.brightness= wx.Slider( panel, -1, 0, -100, 100 )
        self.contrastLabel= wx.StaticText( panel, -1, 'Contrast', style=wx.ALIGN_CENTER)
        self.contrast = wx.Slider( panel, -1, 0, -100, 100 )

        sizer1.Add( self.brightnessLabel )
        sizer1.Add( self.brightness )
        sizer1.Add( self.contrastLabel )
        sizer1.Add( self.contrast )
        
        self.Bind(wx.EVT_SCROLL, self.OnSlide)
        #self.Bind( wx.EVT_PAINT, self.OnPaint )
        
        self.thumbview = wx.StaticBitmap( panel, -1, wx.BitmapFromImage( wx.EmptyImage( 320,240 )) )
        #self.thumbview.SetSize( ( 320, 240 ) )
        
        self.okButton = wx.Button( panel, ID_BNC_OK_BUTTON, 'OK' )
        self.cancelButton = wx.Button( panel, ID_BNC_CANCEL_BUTTON , 'Cancel' )
        self.Bind( wx.EVT_BUTTON, self.OnOk, id=ID_BNC_OK_BUTTON )
        self.Bind( wx.EVT_BUTTON, self.OnCancel, id=ID_BNC_CANCEL_BUTTON )
        
        sizer3.Add( self.okButton )
        sizer3.Add( self.cancelButton )

        sizer4.Add( sizer1, 0, wx.EXPAND|wx.ALL, 5 )
        #sizer4.Add( sizer2, 0, wx.EXPAND|wx.ALL, 10)
        sizer4.Add( self.thumbview, 0, wx.EXPAND|wx.ALL, 5 )
        sizer4.Add( sizer3, 0, wx.EXPAND|wx.ALL, 5 )
        #x = self.GetSize().width / 2 
        #y = self.GetSize().height/ 2 
        
        #self.DrawToBuffer()
        panel.SetSizer(sizer4)    
        panel.Fit()

        
        #img = wx.EmptyImage(320,240)
        ##self.thumbnail = img
        #self.buffer = wx.BitmapFromImage( self.thumbnail )
        #self.DrawToBuffer()
        #self.Show()
        #self.length.SetFocus()
        #self.forms['objname'] = wx.TextCtrl(panel, -1, '')
    def SetThumbnail(self,thumbnail):
        wx.BeginBusyCursor()
        self.thumbnail = thumbnail
        self.thumbview.SetBitmap( wx.BitmapFromImage( thumbnail ) )
        wx.EndBusyCursor()
        #self.thumbview.Refresh()
        
    def OnOk(self,event):
        self.EndModal(wx.ID_OK)
        #self.SetReturnCode( wx.ID_OK )
        #self.Close()
        #self.TwoDViewer.SetFocus()
        #self.End(wx.ID_OK)   
    

    def OnCancel(self,event):
        self.EndModal(wx.ID_CANCEL)
    
    def GetValues(self):
        return self.brightness.GetValue(), self.contrast.GetValue()

    def OnSlide(self,evt):
        bright = self.brightness.GetValue()
        contrast = self.contrast.GetValue()
        #print "brightness and contrast", bright, contrast
        thumbnail = self.thumbnail
        adjusted_thumb = self.AdjustBrightnessAndContrast( thumbnail, ( bright / 200.0 ) + 1.0, ( contrast / 200.0 ) + 1.0 )
        #print adjusted_thumb
        adjusted_bitmap = wx.BitmapFromImage(  adjusted_thumb ) 
        #print adjusted_bitmap
        self.thumbview.SetBitmap( adjusted_bitmap )
        #self.thumbview.
        #print "B&C", bright, contrast
        return
    def AdjustBrightnessAndContrast( self, image, brightness, contrast ):
        #print "brightness, contrast"
        img = imagetopil( image )
        #print image.GetData()
        #print img.convert( "RGB").tostring()
        br_enhancer = ImageEnhance.Brightness( img )
        new_img = br_enhancer.enhance( brightness )
        #print new_img.convert( "RGB").tostring()
        cont_enhancer = ImageEnhance.Contrast( new_img )
        new_img = cont_enhancer.enhance( contrast )
        #print new_img.convert( "RGB").tostring()
        new_wximg = piltoimage( new_img )
        return new_wximg 

class BlackAndWhiteDialog( wx.Dialog ):
    def __init__(self,parent,wid):
        wx.Dialog.__init__(self,parent,wid,'Convert to B&W', size = (360,360))
        self.panel = panel = wx.Panel( self, -1 )
        
        sizer1 = wx.BoxSizer( wx.HORIZONTAL )
        sizer3 = wx.BoxSizer( wx.HORIZONTAL )
        sizer4 = wx.BoxSizer( wx.VERTICAL )

        
        self.thresholdLabel= wx.StaticText( panel, -1, 'Threshold', style=wx.ALIGN_CENTER)
        self.threshold = wx.Slider( panel, -1, 127, 0, 255)

        sizer1.Add( self.thresholdLabel )
        sizer1.Add( self.threshold )
        
        self.Bind(wx.EVT_SCROLL, self.OnSlide)
        
        self.thumbview = wx.StaticBitmap( panel, -1, wx.BitmapFromImage( wx.EmptyImage( 320,240 )) )
        #self.thumbview.SetSize( ( 320, 240 ) )
        
        self.okButton = wx.Button( panel, ID_BNC_OK_BUTTON, 'OK' )
        self.cancelButton = wx.Button( panel, ID_BNC_CANCEL_BUTTON , 'Cancel' )
        self.Bind( wx.EVT_BUTTON, self.OnOk, id=ID_BNC_OK_BUTTON )
        self.Bind( wx.EVT_BUTTON, self.OnCancel, id=ID_BNC_CANCEL_BUTTON )
        
        sizer3.Add( self.okButton )
        sizer3.Add( self.cancelButton )

        sizer4.Add( sizer1, 0, wx.EXPAND|wx.ALL, 5 )
        #sizer4.Add( sizer2, 0, wx.EXPAND|wx.ALL, 10)
        sizer4.Add( self.thumbview, 0, wx.EXPAND|wx.ALL, 5 )
        sizer4.Add( sizer3, 0, wx.EXPAND|wx.ALL, 5 )
        #x = self.GetSize().width / 2 
        #y = self.GetSize().height/ 2 
        
        #self.DrawToBuffer()
        panel.SetSizer(sizer4)    
        panel.Fit()

        
        #img = wx.EmptyImage(320,240)
        ##self.thumbnail = img
        #self.buffer = wx.BitmapFromImage( self.thumbnail )
        #self.DrawToBuffer()
        #self.Show()
        #self.length.SetFocus()
        #self.forms['objname'] = wx.TextCtrl(panel, -1, '')

    def SetThumbnail(self,thumbnail):
        wx.BeginBusyCursor()
        self.thumbnail = thumbnail
        self.thumbview.SetBitmap( wx.BitmapFromImage( thumbnail ) )
        self.ApplyThreshold( self.GetValues() )
        wx.EndBusyCursor()
        #self.thumbview.Refresh()
        
    def OnOk(self,event):
        self.EndModal(wx.ID_OK)
        #self.SetReturnCode( wx.ID_OK )
        #self.Close()
        #self.TwoDViewer.SetFocus()
        #self.End(wx.ID_OK)   
    

    def OnCancel(self,event):
        self.EndModal(wx.ID_CANCEL)
    
    def GetValues(self):
        return self.threshold.GetValue()


    def ApplyThreshold(self, threshold):
        thumbnail = self.thumbnail
        adjusted_thumb = self.ConvertToBlackAndWhite( thumbnail, threshold )
        #print adjusted_thumb
        adjusted_bitmap = wx.BitmapFromImage(  adjusted_thumb ) 
        #print adjusted_bitmap
        self.thumbview.SetBitmap( adjusted_bitmap )

    def OnSlide(self,evt):
        threshold = self.threshold.GetValue()
        self.ApplyThreshold( threshold )
        return
    
    def ConvertToBlackAndWhite( self, image, threshold):
        #print "brightness, contrast"
        img = imagetopil( image )
        out = img.point(lambda i: i > threshold and 255)        
        new_img = out.convert("P").convert("1")
        new_wximg = piltoimage( new_img )
        return new_wximg 

    

ID_LOAD_IMAGE_BUTTON = 1001
ID_ADD_OBJECT_BUTTON = 1002
ID_FFT_BUTTON = 1009
ID_BNC_BUTTON = 1003
ID_CALIBRATION_BUTTON = 1004
ID_BNW_BUTTON = 1005
ID_SELECT_BUTTON = 1006
ID_UNDO_BUTTON = 1007
ID_REDO_BUTTON = 1008
ID_DILATION_BUTTON = 1009
ID_EROSION_BUTTON = 1010
ID_GET_SEGMENTS_BUTTON = 1011
ID_REMOVE_NOISE_BUTTON = 1012

ID_OK_BUTTON = 1021
ID_CANCEL_BUTTON = 1022


class SilhouettoOutlineDialog( wx.Dialog ):
    def __init__( self, parent, wid ):
        wx.Dialog.__init__( self, parent, wid, 'Outline', size=DIALOG_SIZE)
        panel = wx.Panel(self, -1)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        subSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ppmm = 0
        self.forms = dict()
        self.forms['objname'] = wx.TextCtrl(panel, -1, '')

        loadImageButton= wx.Button(panel, ID_LOAD_IMAGE_BUTTON, 'Load')
        self.Bind(wx.EVT_BUTTON, self.LoadImage, id=ID_LOAD_IMAGE_BUTTON)

        self.point_list = []
        self.TwoDViewer = SilImageControl(panel,-1)
        self.TwoDViewer.calibration_dialog = UnitCalibrationDialog(self, -1)

        sizer1 = wx.BoxSizer( wx.HORIZONTAL )
        sizer2 = wx.BoxSizer( wx.HORIZONTAL )

        sizer1.Add( self.forms['objname'], 0, wx.EXPAND|wx.ALL, 10)
        sizer1.Add( loadImageButton )

        ''' Calibration'''
        calibrationButton= wx.Button(panel, ID_CALIBRATION_BUTTON, 'Calib.')
        self.Bind(wx.EVT_BUTTON, self.Calibrate, id=ID_CALIBRATION_BUTTON)
        sizer1.Add( calibrationButton )

        ''' Brightness and Contrast''' 
        BrightnessAndContrastButton= wx.Button(panel, ID_BNC_BUTTON, 'Bright/Cont')
        self.Bind(wx.EVT_BUTTON, self.OnBrightnessAndContrast, id=ID_BNC_BUTTON)
        sizer1.Add( BrightnessAndContrastButton )

        ''' Black and white''' 
        BlackAndWhiteButton= wx.Button(panel, ID_BNW_BUTTON, 'B&W')
        self.Bind(wx.EVT_BUTTON, self.OnBlackAndWhite, id=ID_BNW_BUTTON)
        sizer1.Add( BlackAndWhiteButton )

        ''' Select region ''' 
        SelectRegionButton= wx.Button(panel, ID_SELECT_BUTTON, 'Select')
        self.Bind(wx.EVT_BUTTON, self.OnSelectRegion, id=ID_SELECT_BUTTON)
        sizer1.Add( SelectRegionButton )

        ''' Undo Image Operation'''
        undoButton= wx.Button(panel, ID_UNDO_BUTTON, 'Undo')
        self.Bind(wx.EVT_BUTTON, self.Undo, id=ID_UNDO_BUTTON)
        sizer1.Add( undoButton )

        ''' Redo Image Operation'''
        redoButton= wx.Button(panel, ID_REDO_BUTTON, 'Redo')
        self.Bind(wx.EVT_BUTTON, self.Redo, id=ID_REDO_BUTTON)
        sizer1.Add( redoButton )

        ''' Dilation '''
        dilationButton= wx.Button(panel, ID_DILATION_BUTTON, 'Dilation')
        self.Bind(wx.EVT_BUTTON, self.OnDilation, id=ID_DILATION_BUTTON)
        sizer2.Add( dilationButton )

        ''' Erosion '''
        erosionButton= wx.Button(panel, ID_EROSION_BUTTON, 'Erosion')
        self.Bind(wx.EVT_BUTTON, self.OnErosion, id=ID_EROSION_BUTTON)
        sizer2.Add( erosionButton )


        ''' GetSegments'''
        getSegmentsButton= wx.Button(panel, ID_GET_SEGMENTS_BUTTON, 'Get Segments')
        self.Bind(wx.EVT_BUTTON, self.OnGetSegments, id=ID_GET_SEGMENTS_BUTTON)
        sizer2.Add( getSegmentsButton )

        ''' RemoveNoise'''
        removeNoiseButton= wx.Button(panel, ID_REMOVE_NOISE_BUTTON, 'Remove Noise')
        self.Bind(wx.EVT_BUTTON, self.OnRemoveNoise, id=ID_REMOVE_NOISE_BUTTON)
        sizer2.Add( removeNoiseButton )

        sizer3 = wx.BoxSizer( wx.HORIZONTAL )

        ''' OK '''
        okButton= wx.Button(panel, ID_OK_BUTTON, 'OK')
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=ID_OK_BUTTON)
        sizer3.Add( okButton )
        ''' Cancel '''
        cancelButton= wx.Button(panel, ID_CANCEL_BUTTON, 'CANCEL')
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=ID_CANCEL_BUTTON)
        sizer3.Add( cancelButton )

        mainSizer.Add( sizer1, 0, wx.EXPAND|wx.ALL, 10)
        mainSizer.Add( sizer2, 0, wx.EXPAND|wx.ALL, 10)
        mainSizer.Add( self.TwoDViewer, 0, wx.EXPAND|wx.ALL, 10)
        mainSizer.Add( sizer3, 0, wx.EXPAND|wx.ALL, 10)

        self.TwoDViewer.sil_object = self.sil_object = SilObject()

        panel.SetSizer(mainSizer)
        panel.Fit()
        return

    def GetObject(self):
        return self.sil_object

    def ClearPointList(self):
        return

    def AppendPoint(self, x, y ):
        self.point_list.append( [ x, y ] )
        #print x, y
        print self.point_list

    def Undo(self,evt):
        self.TwoDViewer.UndoImageOperation()
    
    def Redo(self,evt):
        self.TwoDViewer.RedoImageOperation()
    
    def OnSelectRegion(self,evt):
        self.TwoDViewer.SetMode( ID_SELECT_REGION_MODE )
        return

    def OnGetSegments(self,event):
        wx.BeginBusyCursor()
        segment_list = self.TwoDViewer.GetSegments2()
        wx.EndBusyCursor()
        
        print "GetAreas done"
    def OnRemoveNoise(self,event):
        segment_list = self.TwoDViewer.segment_list
        sum = 0
        for s in segment_list:
            print s.index, s.area, s.color
            sum += s.area
        average = sum / len( segment_list )
        print average
        
        wx.BeginBusyCursor()
        self.TwoDViewer.RemoveSmallSegments( average )
        wx.EndBusyCursor()
                
    
    def OnBrightnessAndContrast(self,evt):
        bncDlg = BrightnessAndContrastDialog(self,-1)
        bncDlg.SetThumbnail( self.TwoDViewer.thumbnail )
        ret = bncDlg.ShowModal()
        if ret == wx.ID_OK:
            brightness, contrast = bncDlg.GetValues()
            bncDlg.Destroy()
            self.TwoDViewer.SetBrightness( brightness )
            self.TwoDViewer.SetContrast( contrast )
    
            wx.BeginBusyCursor()
            self.TwoDViewer.ApplyBrightnessAndContrast()
            self.TwoDViewer.RefreshImage()
            wx.EndBusyCursor()
        self.TwoDViewer.SetFocus()
            #self.pixels_per_millimeter = float( actual_dist )/ float( length )
            
        return
    
    def OnBlackAndWhite(self,evt):
        bnwDlg = BlackAndWhiteDialog(self,-1)
        bnwDlg.SetThumbnail( self.TwoDViewer.thumbnail )
        ret = bnwDlg.ShowModal()
        if ret == wx.ID_OK:
            threshold = bnwDlg.GetValues()
            bnwDlg.Destroy()
            self.TwoDViewer.SetThreshold( threshold)
    
            wx.BeginBusyCursor()
            self.TwoDViewer.ApplyThreshold()
            self.TwoDViewer.RefreshImage()
            wx.EndBusyCursor()
        self.TwoDViewer.SetFocus()

    def LoadImage(self,evt):
        wildcard = "JPEG file (*.jpg)|*.jpg|" \
                   "BMP file (*.bmp)|*.bmp|" \
                   "TIF file (*.tif)|*.tif|" \
                   "All files (*.*)|*.*"
    
        dialog_style = wx.OPEN 
    
        selectfile_dialog = wx.FileDialog(self, "Select File to Load...", "", "", wildcard, dialog_style )
        if selectfile_dialog.ShowModal() == wx.ID_OK:
            #self.ConfirmClearLandmark()
            self.importpath = selectfile_dialog.GetPath()
            #( unc, pathname ) = splitunc( self.importpath )
            pathname = self.importpath
            #print pathname
            ( pathname, fname ) = os.path.split( pathname )
          
        #print pathname
        #print fname
          
            ( fname, ext ) = os.path.splitext( fname )
            #if( self.forms['objname'].GetValue() == '' ):
            self.forms['objname'].SetValue( fname )
            self.sil_object.SetName( fname )
            wx.BeginBusyCursor()
            self.TwoDViewer.LoadImageFile(self.importpath)
            wx.EndBusyCursor()
        selectfile_dialog.Destroy()
        return

    def Calibrate(self,evt):
        self.TwoDViewer.SetMode( ID_CALIBRATION_MODE )
        return

    def ApplyCalibrationResult(self):
        #print "apply calib"
        self.ppmm = self.TwoDViewer.pixels_per_millimeter
        #print "ppmm", ppmm
        # self.twoDppmm.SetValue( ppmm )
        #temp_list = []
        #temp_list[::] = self.landmark_list[::]
        #self.ClearLandmarkList() 
        #for lm in temp_list:
        #    self.AppendLandmark(lm[0], lm[1], lm[2], lm[3])
            #chkShowCoordsInMillimeter()
    '''
    def OnSlide(self,event):
        bright = self.slBright.GetValue()
        contrast = self.slContrast.GetValue()
        #print "B&C", bright, contrast
        self.TwoDViewer.SetBrightness( bright )
        self.TwoDViewer.SetContrast( contrast )
        self.TwoDViewer.DrawToBuffer()
    #print bright, contrast
    '''
        
    def get_kernel(self):
        kernel = []
        aa = [ -1, 0, 1 ]
        for i in range(3):
            for j in range(3):
                kernel.append( [ aa[i], aa[j] ] )
        #kernel = [ [ -1, -1 ], [0, -1], [1, -1], [ -1, 0], [ 0, 0 ], [ 1, 0 ], [ -1, 1], [0, 1], [1, 1] ] 
        return kernel
    
    def OnDilation(self,evt):
        wx.BeginBusyCursor()
        self.TwoDViewer.SetKernel( self.get_kernel() )
        self.TwoDViewer.ApplyKernel( 255 )
        wx.EndBusyCursor()
        
    def OnErosion(self,evt):
        wx.BeginBusyCursor()
        self.TwoDViewer.SetKernel( self.get_kernel() )
        self.TwoDViewer.ApplyKernel( 0 )
        wx.EndBusyCursor()
    
    def OnOk(self,evt):
        self.EndModal( wx.ID_OK )
    
    def OnCancel(self,evt):
        self.EndModal( wx.ID_CANCEL )

class SilhouettoMainDialog( wx.Frame ): 
    def __init__( self, parent, wid ):
        wx.Frame.__init__( self, parent, wid, 'Silhouetto', size=DIALOG_SIZE)
        #return
        panel = wx.Panel(self, -1)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.forms = {}

        addObjectButton= wx.Button(panel, ID_ADD_OBJECT_BUTTON, 'Add')
        self.Bind(wx.EVT_BUTTON, self.AddObject, id=ID_ADD_OBJECT_BUTTON)

        fftButton= wx.Button(panel, ID_FFT_BUTTON, 'FFT')
        self.Bind(wx.EVT_BUTTON, self.OnFFT, id=ID_FFT_BUTTON)

        self.forms['objectlist'] = wx.ListBox( panel, -1, choices = [], size=(100,300), style=wx.LB_EXTENDED )
        mainSizer.Add( self.forms['objectlist'], 0, wx.EXPAND|wx.ALL, 10)
        mainSizer.Add( addObjectButton, 0, wx.EXPAND|wx.ALL, 10)
        mainSizer.Add( fftButton, 0, wx.EXPAND|wx.ALL, 10)
        panel.SetSizer(mainSizer)
        panel.Fit()
        self.object_list = []
        return

    def AddObject(self,evt):
        dlg = SilhouettoOutlineDialog(None, -1 )
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            sil_object = dlg.GetObject()
            self.object_list.append( sil_object )
            print sil_object.chaincode
        dlg.Destroy()

        return
    def OnFFT0(self,evt):
        x_list = []
        y_list = []
        chaincode = [ 1, 1, 1, 7, 2, 2, 0, 6, 6, 6, 7, 6, 6,6, 4, 4, 4, 4, 4, 4, 2, 2, 2 ]
        x = y = 0
        for d in chaincode:
            x += DIRECTION_MATRIX[d][0]
            y += DIRECTION_MATRIX[d][1]
            x_list.append( x )
            y_list.append( y )
        print x_list
        print y_list
        x_fft_result = fft.rfft( x_list )
        y_fft_result = fft.rfft( y_list )
        print x_fft_result
        print y_fft_result
            
    def OnFFT(self,evt):
        self.FFT()
        return

    def FFT(self):
        for o in self.object_list:
            x_list = []
            y_list = []
            #print o.chaincode
            print "----"
            print o.object_name + "_1 " + str( o.point_list[0][0] ) + " " + str( o.point_list[0][1] ) + " 1 1"
            for d in o.chaincode:
                print d,
            print "-1"
            print "----"
            x = y = 0
            for d in o.chaincode:
                x += DIRECTION_MATRIX[d][0]
                y -= DIRECTION_MATRIX[d][1]
                x_list.append( x )
                y_list.append( y )
            n_point = len( x_list )
            x_fft_result = fft.rfft( x_list )
            y_fft_result = fft.rfft( y_list )
            for i in range(20):
                x = x_fft_result[i]
                y = y_fft_result[i]
                print "%e %e %e %e" % ( x.real, x.imag, y.real, y.imag )
                
            x_list_2 = fft.irfft(x_fft_result[0:10], n_point )
            y_list_2 = fft.irfft(y_fft_result[0:10], n_point )
            
            print "x"
            print x_list
            print x_list_2
            print "y"
            print y_list
            print y_list_2