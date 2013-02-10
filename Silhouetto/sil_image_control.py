import wx 
import os
import math
import time
import numpy

from wx.lib.colourchooser.canvas import Canvas #@warning: 
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources  
#import sys
from PIL import Image, ImageEnhance

ID_SAVE_BUTTON = 2000
ID_DELETE_BUTTON = 2001
ID_CLOSE_BUTTON = 2002 
ID_SHOW_BUTTON = 2003

ID_COMBO_DSNAME = 2004

ID_LM_GRID_CTRL = 2010
ID_LM_PASTE_BUTTON = 2011
ID_LM_ADD_BUTTON  = 2012
ID_LM_DELETE_BUTTON  = 2013
ID_COORD_ADD_BUTTON  = 2014
ID_XCOORD = 2015
ID_YCOORD = 2016
ID_ZCOORD = 2017

ID_IMAGE_LOAD_BUTTON  = 2018
ID_IMAGE_COPY_BUTTON  = 2023
ID_IMAGE_PASTE_BUTTON  = 2024
ID_CHK_COORDS_IN_MILLIMETER = 2025

ID_POINT_BUTTON  = 2021
ID_CALIBRATION_BUTTON  = 2022
ID_WIREFRAME_BUTTON  = 2026
ID_BASELINE_BUTTON  = 2027
ID_MISSING_DATA_BUTTON  = 2028

ID_CHK_AUTO_ROTATE = 2031
ID_CHK_SHOW_INDEX = 2032
ID_CHK_SHOW_WIREFRAME = 2033
ID_CHK_SHOW_BASELINE = 2034

ID_POINT_MODE = 4003
ID_CALIBRATION_MODE = 4004 
ID_POINT_EDIT_MODE = 4005
ID_WIREFRAME_MODE = 4006
ID_WIREFRAME_EDIT_MODE = 4007
ID_BASELINE_MODE = 4008
ID_BASELINE_EDIT_MODE = 4009
ID_SELECT_REGION_MODE = 4010 

LM_MISSING_VALUE = -99999

DIALOG_SIZE = wx.Size(1024,768)

DIRECTION_MATRIX = [ [ 0, -1 ], [ 1, -1 ], [ 1, 0 ], [ 1, 1 ], [ 0, 1 ], [ -1, 1 ], [ -1, 0 ], [ -1, -1 ] ]

''' per Kuhl and Giardina 1982 '''
DIRECTION_MATRIX = [ [ 1, 0 ], [ 1, 1 ], [ 0, 1 ], [ -1, 1 ], [ -1, 0 ], [ -1, -1 ], [ 0, -1 ], [ 1, -1 ] ]

class SegmentObject( object ):
    def __init__(self):
        self.area = 0
        self.point_list = []
        self.color = -1
        self.parent = None
        self.parent_index = -1
        self.active = True
        return

    def merge_into_parent(self):
        self.parent.append_point_list( self.point_list )

    def append_point_list(self, point_list):
        self.point_list.extend( point_list )
        self.calculate_area()
    

    def calculate_area(self):
        self.area = len( self.point_list )
        #for p in self.point_list:
            


pointSeqWidth = 40
pointCoordWidth = 60
pointCoordHeight = 22

class SilThumbControl( wx.Window ): 
    def __init__(self,parent,wid,w=320,h=240): 
        wx.Window.__init__(self,parent,wid)
        self.SetBackgroundColour('#aaaaaa')
        self.width = w
        self.height = h
        self.SetSize( (w,h) )
    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(self.width,self.height)
        dc = wx.BufferedDC( None, self.buffer )
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        
    def SetThumbnail(self, thumbnail ):
        self.thumbnail = thumbnail
        self.buffer = wx.BitmapFromImage( self.thumbnail)
        self.DrawToBuffer()
    def DrawToBuffer(self):
        dc = wx.BufferedDC( wx.ClientDC(self), self.buffer )
    def OnPaint(self,event):
        dc = wx.BufferedPaintDC(self, self.buffer)
        
class SilImageControl( wx.Window ): 
    def __init__(self,parent,wid,w=640,h=480): 
        wx.Window.__init__(self,parent,wid)
        #self.Bind( wx.EVT_MOUSEWHEEL, self.OnWheel )
        #self.LoadBitmap( wx.BitmapFromImage(self.img) )
        self.Bind( wx.EVT_MOUSEWHEEL, self.OnWheel )
        self.Bind( wx.EVT_PAINT, self.OnPaint )
        self.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
        self.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
        self.Bind( wx.EVT_ENTER_WINDOW, self.OnMouseEnter )
        self.Bind( wx.EVT_MOTION, self.OnMotion )
        self.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
        self.Bind( wx.EVT_KEY_UP, self.OnKeyUp )
        # should be left click
        self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightDown )
        self.Bind( wx.EVT_RIGHT_UP, self.OnRightUp )
        #self.Bind( wx.EVT_LEAVE_WINDOW, self.OnMouseLeave )
        self.SetBackgroundColour('#aaaaaa')
        #self.SetCursor( wx.StockCursor(wx.CURSOR_CROSS ) )
        self.width = w
        self.height = h
        self.SetSize( (w,h) )
        
        self.border_point_list = []
        self.point_list = []
        self.in_motion = False
        self.is_dragging_image = False
        self.is_dragging_point = False
        self.is_dragging_wire = False
        self.is_dragging_baseline = False
        self.is_calibrating = False
        self.show_index = False
        self.show_wireframe = True
        self.show_baseline = False
        self.pixels_per_millimeter = -1
        self.parent_dialog = self.GetParent().GetParent()
        self.SetMode( ID_POINT_MODE )
        self.ClearImage()
        #self.currimg = self.img = self.origimg = wx.EmptyImage(640,480)
        #self.buffer = wx.BitmapFromImage( self.img )
        #self.RefreshImage()
        self.has_image = False
        #self.LoadImageFile( "trilobite1.jpg" )
        self.cmd_down = False
        self.alt_down = False
        self.temp_point_list = []
        self.deleted_point_list = []
        self.begin_wire_idx = -1
        self.end_wire_idx = -1
        self.begin_baseline_idx = -1
        self.end_baseline_idx = -1
        self.cursor_on_idx = -1
        self.hovering_edge = []
        self.threshold = 127
        self.image_list = []
        self.redo_list = []
    
    def EndAutoRotate(self):
        return
    
    def BeginAutoRotate(self):
        return
    
    def SetMode(self,mode):
        #print "set mode:", mode
        self.mode = mode
        if mode == ID_POINT_MODE:
            self.SetCursor( wx.StockCursor( wx.CURSOR_CROSS ) )
            self.curr_point_idx = -1
        elif mode == ID_CALIBRATION_MODE:
            self.SetCursor( wx.StockCursor( wx.CURSOR_SIZEWE ) )
        elif mode == ID_POINT_EDIT_MODE:
            self.SetCursor( wx.StockCursor( wx.CURSOR_HAND ) )
        elif mode == ID_WIREFRAME_MODE:
            #print "wireframe"
            self.SetCursor( wx.StockCursor( wx.CURSOR_SIZEWE ) )
        elif mode == ID_WIREFRAME_EDIT_MODE:
            self.SetCursor( wx.StockCursor( wx.CURSOR_HAND ) )
        elif mode == ID_BASELINE_MODE:
            #print "baseline"
            self.SetCursor( wx.StockCursor( wx.CURSOR_SIZEWE ) )
        elif mode == ID_BASELINE_EDIT_MODE:
            self.SetCursor( wx.StockCursor( wx.CURSOR_HAND ) )
        return
    
    def ClearImage(self):
        self.has_image = False
        img = wx.EmptyImage(self.width,self.height)
        img.SetRGBRect(wx.Rect(0,0,self.width,self.height), 128, 128, 128) 
        self.SetImage(img, True)
        self.buffer = wx.BitmapFromImage( self.img )
        return
    
    def SetImage(self,img, empty_image=False):
        if self.has_image: 
            self.image_list.append( self.origimg )

        if not empty_image:
            self.has_image = True
        
      
        
        self.currimg = self.img = self.origimg = img
      
        self.ResetImage()
        self.MakeThumbnail()
    
    def MakeThumbnail(self):
        img = self.origimg
        _w = 320
        _h = 240
        w = img.GetWidth()
        h = img.GetHeight()
        if w / h > _w / _h :
            h = _h * ( w / _w )
            w = _w
        else:
            h = _h
            w = _w * ( h / _h )
            
        self.thumbnail = img.Scale( w, h )
        
    def LoadImageFile(self, filename):
        img = wx.Image( filename )
        img = img.ConvertToGreyscale()
        self.SetImage( img )
        #print filename
        #self.currimg = self.img = self.origimg = wx.Image( filename )
        #print self.img.ClassName 
        #self.RefreshImage()
        return

    def OnRightDown(self, event):
        # should be a callback function
        if self.mode == ID_POINT_EDIT_MODE:
            confirmDlg = wx.MessageDialog(self, "Delete point?", "Modan", wx.YES_NO|wx.YES_DEFAULT )
            ret = confirmDlg.ShowModal()
            if ret != wx.ID_YES:
                return
            #print self.temp_point_list
            deleted_point = self.temp_point_list.pop(self.curr_point_idx-1)
            #print self.temp_point_list
            self.deleted_point_list.append( ( self.curr_point_idx, deleted_point ) )
            #parent = self.GetParent().GetParent()
            self.parent_dialog.ClearPointList()
            for i in range( len( self.temp_point_list ) ):
                p = self.temp_point_list[i]
                self.parent_dialog.AppendPoint( p[0], p[1] )
            self.DrawToBuffer()
        elif self.mode == ID_WIREFRAME_EDIT_MODE and self.hovering_edge != []:
            confirmDlg = wx.MessageDialog(self, "Delete this edge?", "Modan", wx.YES_NO|wx.YES_DEFAULT )
            ret = confirmDlg.ShowModal()
            if ret != wx.ID_YES:
                return
            self.parent_dialog.DeleteWire( self.hovering_edge[0], self.hovering_edge[1] )
            self.DrawToBuffer()
            self.SetMode( ID_WIREFRAME_MODE )
        else:
            self.is_dragging_image = True
            self.CaptureMouse()
            self.x, self.y = self.lastx, self.lasty = event.GetPosition()
        
    def OnRightUp(self, event):
        if self.is_dragging_image:
            self.EndDragging(event)
    
    def OnKeyDown(self,event):
        self.cmd_down = event.CmdDown()
        self.alt_down = event.AltDown()
    #    if self.alt_down and self.mode == ID_2D_POINT_EDIT_MODE:
    #      self.SetCursor()
    
    def OnKeyUp(self,event):
        self.cmd_down = event.CmdDown()
        self.alt_down = event.AltDown()
    
    def OnLeftDown(self,event):
        #print "down"
        if not self.has_image:
            return
        if self.mode == ID_POINT_MODE:
            if self.img_x < 0 or self.img_y < 0:
                return
            self.parent_dialog.AppendPoint( self.img_x, self.img_y )
            self.DrawToBuffer()
        elif self.mode == ID_CALIBRATION_MODE:
            self.x, self.y = self.lastx, self.lasty = event.GetPosition()
            self.calib_x1, self.calib_y1 = self.x, self.y 
            self.calib_x2, self.calib_y2 = self.x, self.y 
            #self.calib_y1 = self.y
            self.DrawToBuffer()
            self.is_calibrating = True
            self.CaptureMouse()
        elif self.mode == ID_POINT_EDIT_MODE:
            self.x, self.y = self.lastx, self.lasty = event.GetPosition()
            self.point_being_moved = self.parent_dialog.point_list[self.curr_point_idx-1]
            self.is_dragging_point = True
            self.CaptureMouse()
        elif self.mode == ID_WIREFRAME_EDIT_MODE:
            self.x, self.y = self.lastx, self.lasty = event.GetPosition()
            self.is_dragging_wire = True
            self.CaptureMouse()
        elif self.mode == ID_BASELINE_EDIT_MODE:
            self.x, self.y = self.lastx, self.lasty = event.GetPosition()
            hit, point_idx = self.IsCursorOnPoint()
            if hit:
                self.begin_baseline_idx = point_idx
                self.is_dragging_baseline = True
                self.CaptureMouse() 
        elif self.mode == ID_SELECT_REGION_MODE:
            self.x, self.y = event.GetPosition()
            self.GetRegion( self.x, self.y )
            return
        
    def GetRegion(self,screen_x,screen_y):
        ''' find top '''
        image_x, image_y = self.ScreenXYtoImageXY(screen_x, screen_y)
        
        val = self.GetPixelValue( image_x, image_y )
        #print "start", image_x, image_y, val 
        
        color = val
        while val == color and image_y > 0 :
            image_y -= 1
            val = self.GetPixelValue( image_x, image_y )
        if image_y == 0:
            print "hit image border"
            return
        image_y += 1
        
        #print image_x, image_y
        self.TraceBorder( image_x, image_y, color )

    def TraceBorder(self, image_x, image_y, color ):
        curr_x = image_x
        curr_y = image_y
        x = y = -1
        val = 0
        point_list = []
        chaincode = []
        #point_list.append( [ start_x, start_y ] )
        dir_idx = 0
        prev_dir_idx = 0
        
        '''DIRECTION_MATRIX = [ [ 1, 0 ], [ 1, 1 ], [ 0, 1 ], [ -1, 1 ], [ -1, 0 ], [ -1, -1 ], [ 0, -1 ], [ 1, -1 ] ]'''
        while( [ curr_x, curr_y ] not in point_list ):
            #found = False
            #print "curr:", curr_x, curr_y
            point_list.append( [ curr_x, curr_y ] )
            if int( prev_dir_idx / 2 ) == prev_dir_idx:
                prev_dir_idx -= 1
            else:
                prev_dir_idx -= 2
            for i in range( len( DIRECTION_MATRIX ) ):
                #dir_idx = ( prev_dir_idx + i - len( DIRECTION_MATRIX ) / 4 )  % len( DIRECTION_MATRIX )
                dir_idx = ( prev_dir_idx + i )  % len( DIRECTION_MATRIX )
                direction = DIRECTION_MATRIX[dir_idx]
                x = curr_x + direction[0]
                y = curr_y + direction[1]                
                val = self.GetPixelValue( x, y )
                #print "  looking at", prev_val, dir_idx, x, y, val
                if val == color :
                    #fount = True
                    #print "    find next place!", x, y, dir_idx
                    curr_x = x
                    curr_y = y
                    chaincode.append( dir_idx )
                    prev_dir_idx = dir_idx
                    #print x, y, dir_idx
                    break
            #print "i", i, curr_x, curr_y, found
            #print curr_x, curr_y
        #print chain_code_list
        #print point_list
        self.chaincode = chaincode
        self.border_point_list = point_list
        if len( point_list ) > 0:
            self.RefreshImage()
        #self.GetPixelValue( image_x, image_y)
        self.sil_object.SetChaincode( chaincode )
        self.sil_object.SetPointList( point_list )

    
    def GetSegments2(self):
        img = self.origimg
        width = img.GetWidth()
        height = img.GetHeight()

        img_array = numpy.zeros( (height, width) )
        segment_array = numpy.zeros( (height, width) )
        segment_array -= 1
        
        for x in range( width ):
            for y in range( height ):
                img_array[y,x] = self.GetPixelValue(x, y)

        pixel_count = width * height 
        segment_list = []
        connectivity_list = []

        prev_val = -1
        max_seg_idx = 0
        
        DIR_MATRIX = [ [ -1, 0 ], [ -1, -1 ], [ 0, -1 ], [ 1, -1 ] ]
        DIR_MATRIX = [ [ -1, 0 ], [ 0, -1 ] ]
        s = SegmentObject()
        seg_idx = s.index = max_seg_idx
        adjacent_list = []

        for y in range( height ):
            for x in range( width ):
                val = img_array[y,x]
                found = False
                found_segment_index_list = []
                adjacent_segment_index_list = []
                for dir in DIR_MATRIX:
                    check_x = x + dir[0]
                    check_y = y + dir[1]
                    if check_x < 0 or check_y < 0:
                        continue
                    check_val = img_array[check_y,check_x]
                    if check_val == val:
                        #print "connected:", x, y, val, "to", check_x, check_y, check_val 
                        found = True
                        found_segment_index_list.append( segment_array[check_y,check_x] )
                        if segment_array[y,x] < 0:
                            segment_array[y,x] = seg_idx = int( segment_array[check_y,check_x] )
                    else:
                        adjacent_segment_index_list.append( segment_array[ check_y, check_x] )
                if found == False:
                    s = SegmentObject()
                    s.adjacent_segment_index_list = []
                    s.point_list.append( [ x, y ] )
                    s.index = seg_idx = max_seg_idx
                    segment_list.append( s )
                    segment_array[y,x] = max_seg_idx
                    #print "new segment at", x, y, "with seg idx", seg_idx
                    #print "new", x, y, seg_idx
                    max_seg_idx += 1
                else:
                    #print "added", x, y, seg_idx
                    segment_list[seg_idx].point_list.append( [ x, y ] )
                    #print x, y, "added to seg idx", seg_idx
                    found_segment_index_list.sort()
                    #print found_segment_index_list
                    #found_segment_index_list = list( set( found_segment_index_list ) )
                    for i in range( len( found_segment_index_list ) - 1 ):
                        a = int(found_segment_index_list[i])
                        for j in range( i+1, len( found_segment_index_list ) ):
                            b = int(found_segment_index_list[j])
                            if a != b:
                                pair = [ a, b ] 
                                if pair not in connectivity_list:
                                    connectivity_list.append( pair )
                for idx in adjacent_segment_index_list:
                    segment_list[seg_idx].adjacent_segment_index_list.append( int( idx ) )

        log_str = ""
        for y in range(height):
            for x in range(width):
                log_str += str( int( segment_array[y,x] ) ) + "\t"
            log_str += "\n"
        #print log_str

        print "segment_list"
        for s in segment_list:
            print s.index, len( s.point_list )
            
        #print "connectivity_list", connectivity_list
        
        for c in connectivity_list:
            c.sort()
        #print "connectivity_list", connectivity_list
        connectivity_list.sort()
        cluster_list = []
        found = True

        cluster_list, segment_map = self.get_cluster_from_edge( len( segment_list ), connectivity_list )
        '''
        while found:
            found = False
            connectivity_list.sort()
            cluster_list = []
            for con in connectivity_list:
                handled = False
                for clu in cluster_list:
                    for c in con:
                        if c in clu:
                            found = True
                            handled = True
                            break
                    if found:
                        for co in con:
                            if co not in clu:
                                clu.append(co)
                if not handled:
                    cluster_list.append( con )
            connectivity_list = cluster_list[:]
        '''
        for clu in cluster_list:
            clu.sort()
            print clu

        ''' merge small segments into large segments '''
        ''' merge adjacent segment index lists from small segments into large adjacent segment index list '''
        
        ''' head list : list of new, large segments '''
        head_list = []  
        
        for clu in cluster_list:
            head = clu.pop(0)
            head_segment = segment_list[head]
            adjacent_seg_idx_list = []
            adjacent_seg_idx_list.extend( head_segment.adjacent_segment_index_list )
            for c in clu:
                body_segment = segment_list[c]
                body_segment.parent = head_segment
                body_segment.merge_into_parent()
                adjacent_seg_idx_list.extend( body_segment.adjacent_segment_index_list )
            head_segment.adjacent_segment_index_list = adjacent_seg_idx_list
            head_list.append( head_segment )
            
        ''' adjacent segment index list update according to clustered segment index '''
        for s in head_list:
            new_adj_idx_list = []
            for adj_idx in s.adjacent_segment_index_list:
                new_idx = segment_map[adj_idx]
                if new_idx != s.index:
                    new_adj_idx_list.append( new_idx )
            s.adjacent_segment_index_list = new_adj_idx_list
        
        for s in head_list:
            if s.active == True:
                print s.index, len( s.point_list )
                print "adjacent segments:", s.adjacent_segment_index_list
                for p in s.point_list:
                    segment_array[p[1],p[0]] = s.index

        log_str = ""
        for y in range(height):
            for x in range(width):
                log_str += str( int( segment_array[y,x] ) ) + "\t"
            log_str += "\n"
        #print log_str
        
        self.segment_list = head_list
                        
                        
    def get_cluster_from_edge(self,num_vertex, edge_list):
        vertex_edge_list = []
        segment_map = []

        for k in range( num_vertex ):
            vertex_edge_list.append( [] )
            segment_map.append(-1)

        for e in edge_list:
            v1 = e[0]
            v2 = e[1]
            vertex_edge_list[v1].append( v2 )
            vertex_edge_list[v2].append( v1 )

        
        cluster_list = []
        visited_vertex = {}
        current_cluster = []
        for current_vertex in range( num_vertex ):
            if visited_vertex.has_key( current_vertex ):
                continue
            print "start new cluster", current_vertex
            current_cluster = []
            current_cluster = self.traverse_edge( vertex_edge_list, current_vertex, visited_vertex, current_cluster, segment_map )
            cluster_list.append( current_cluster )
        
        print "traverse edge done"
        for c in cluster_list:
            print "cluster:", c

        print "segment map:", segment_map
        return cluster_list, segment_map

    def traverse_edge(self, vertex_edge_list, current_vertex, visited_vertex, current_cluster, segment_map ):
        print "current_vertex", current_vertex
        current_cluster.append( current_vertex )
        segment_map[current_vertex] = current_cluster[0]
        visited_vertex[current_vertex] = 1
        next_vertex_list = vertex_edge_list[current_vertex]
        for next_vertex in next_vertex_list:
            if visited_vertex.has_key( next_vertex ):
                print "already "
                continue
            current_cluster = self.traverse_edge( vertex_edge_list, next_vertex, visited_vertex, current_cluster, segment_map )
        return current_cluster

    def GetSegments(self):
        img = self.origimg #.Copy()
        width = img.GetWidth()
        height = img.GetHeight()
        
        img_array = numpy.zeros( (width, height) )
        segment_array = numpy.zeros( (width, height) )
        segment_array -= 1
        
        for x in range( width ):
            for y in range( height ):
                img_array[x,y] = self.GetPixelValue(x, y)

        pixel_count = width * height 
        segment_list = []
        current_segment_pixel = []
        current_segment_candidate_pixel = []
        investigated_pixel = []
        to_be_investigated_pixel = []
        parent_segment_index_list = []
        curr_x = 0 
        curr_y = 0
        #current_area_pixel.append( [curr_x,curr_y] )
        to_be_investigated_pixel.append( [curr_x,curr_y] )
        parent_segment_index_list.append( -1 )
        investigated_pixel_count = 0
        print "WxH", width, height
        
        segment_index = -1

        while investigated_pixel_count < pixel_count:
            if len( current_segment_candidate_pixel ) == 0 and len( to_be_investigated_pixel ) > 0:
                #to_be_investigated_pixel = list( set( to_be_investigated_pixel ) )
                new_pixel = to_be_investigated_pixel.pop(0) 
                parent_segment_index = parent_segment_index_list.pop(0)
                while segment_array[ new_pixel[0], new_pixel[1] ] > 0:
                    new_pixel = to_be_investigated_pixel.pop(0)
                    parent_segment_index = parent_segment_index_list.pop(0)
                #print "new pixel", new_pixel
                curr_color = img_array[ new_pixel[0], new_pixel[1] ]
                current_segment_candidate_pixel.append( new_pixel )
                segment_index += 1
                segment = SegmentObject()
                segment.index = segment_index
                segment.parent_index = parent_segment_index
                segment.color = curr_color
                if segment.parent_index >= 0:
                    segment.parent = segment_list[segment.parent_index]
                #area.parent = Area
                segment.point_list = current_segment_pixel = []
                segment_list.append( segment )

            while len( current_segment_candidate_pixel ) > 0:
                curr_pixel = current_segment_candidate_pixel.pop(0)
                curr_x = curr_pixel[0]
                curr_y = curr_pixel[1]
                #print "current:", curr_x, curr_y
                #curr_color = self.GetPixelValue(curr_x, curr_y)
                current_segment_pixel.append( curr_pixel )
                investigated_pixel.append( curr_pixel )
                segment_array[ curr_x, curr_y] = segment_index
                for i in range( len( DIRECTION_MATRIX ) ):
                    direction = DIRECTION_MATRIX[i]
                    x = curr_x + direction[0]
                    y = curr_y + direction[1]
                    if x < 0 or y < 0 or x >= width or y >= height:
                        continue
                    if segment_array[x,y] >= 0:
                        continue
                    val = img_array[x,y]
                    if val == curr_color:
                        if [x,y] not in current_segment_candidate_pixel:
                            current_segment_candidate_pixel.append( [x,y] )
                            #print "candidate added", x, y
                    else:
                        if [x,y] not in to_be_investigated_pixel:
                            #print "next area?", x, y 
                            to_be_investigated_pixel.append( [x,y] )
                            parent_segment_index_list.append( segment_index )
                            #print "to be investigated added", x, y
                #print "current area candidate pixel:", current_area_candidate_pixel
            investigated_pixel_count += len(current_segment_pixel)
            segment.calculate_area()
            #print investigated_pixel_count, len()
            print len( investigated_pixel ), len( current_segment_pixel ), len( to_be_investigated_pixel )
            #print "to be investigated:", to_be_investigated_pixel
            
        log_str = ""
        for x in range(width):
            for y in range(height):
                log_str += str( int( segment_array[x,y] ) )
            log_str += "\n"
        print log_str
        
        self.segment_list = segment_list
        return segment_list

    def RemoveSmallSegments(self, area_threshold):
        self.segment_list.sort( key=lambda s: s.area )
        new_segment_list = []
        for s in self.segment_list:
            if s.area < area_threshold:
                s.merge_into_parent()
            else:
                new_segment_list.append( s )
                #print s.index, s.area, s.color

        self.segment_list = new_segment_list

        for s in self.segment_list:
            #print s.index, s.area, s.color
            for p in s.point_list:
                self.SetPixelValue( p[0], p[1], s.color )
        self.RefreshImage()
    
    def GetPixelValue(self, x, y ):
        #print x, y
        img = self.origimg
        val = img.GetBlue( x, y )
        #print x, y, val
        return val

    def SetPixelValue(self, x, y, color ):
        #print x, y
        color = int( color )
        img = self.origimg
        img.SetRGB( x, y, color, color, color)
        return
        if color == 255:
            img.SetRGB( x, y, 255, 255, 255 )
        else:
            img.SetRGB( x, y, 0, 0, 0 )
        #return val

    def IsImageInside(self):
        x1 = y1 = 0
        x2 = self.origimg.GetWidth()
        y2 = self.origimg.GetHeight()
        scr_x, scr_y = self.ImageXYtoScreenXY(x1, y1)
        #print scr_x, scr_y
        if scr_x > self.GetSize().width or scr_y > self.GetSize().height :
            #print "not inside 1"
            return False
        scr_x, scr_y = self.ImageXYtoScreenXY(x2, y2)
        #print scr_x, scr_y
        if scr_x < 0 or scr_y < 0 :
            #print "not inside 2"
            return False
        return True
              
      
    def OnLeftUp(self, event):
        #print "up"
        if self.is_dragging_image:
            self.EndDragging(event)
        elif self.is_calibrating:
            self.EndCalibration(event)
        elif self.is_dragging_point:
            self.is_dragging_point = False
            self.ReleaseMouse()
        elif self.is_dragging_wire:
            self.x, self.y = event.GetPosition()
            hit, point_idx = self.IsCursorOnPoint()
            if hit:
                self.parent_dialog.AppendWire( self.begin_wire_idx, self.end_wire_idx ) 
            self.is_dragging_wire = False
            self.begin_wire_idx = self.end_wire_idx
            self.end_wire_idx = -1
            self.ReleaseMouse()
        elif self.is_dragging_baseline:
            self.x, self.y = event.GetPosition()
            hit, point_idx = self.IsCursorOnPoint()
            if hit:
                if point_idx == self.begin_baseline_idx:
                    if len( self.parent_dialog.baseline_points ) == 2:
                        self.parent_dialog.ClearBaseline()
                    self.parent_dialog.AppendBaselinePoint( point_idx )
                else:
                    self.parent_dialog.ClearBaseline()
                    self.parent_dialog.AppendBaselinePoint( self.begin_baseline_idx )
                    self.parent_dialog.AppendBaselinePoint( point_idx )
                
            self.is_dragging_baseline = False
            self.begin_baseline_idx = self.end_baseline_idx
            self.end_baseline_idx = -1
            self.ReleaseMouse()
          
            #self.SetMode( ID_2D_POINT_MODE )
            #self.SetCursor( wx.StockCursor( wx.CURSOR_CROSS ) )
    
    def EndCalibration(self,event):
        if self.is_calibrating:
            self.is_calibrating = False
            self.in_motion = False
            self.x, self.y = event.GetPosition()
            self.calib_x2, self.calib_y2 = self.x, self.y
            #self.calib_y2 = self.y
            self.ReleaseMouse()
            #print self.calib_x1, self.calib_y1, self.calib_x2, self.calib_y2
            #x2 = float( self.calib_x2 - self.calib_x1 ) ** 2.0
            #y2 = float( self.calib_y2 - self.calib_y1 ) ** 2.0
            dist = self.get_distance( self.calib_x1, self.calib_y1, self.calib_x2, self.calib_y2 )
            #dist = ( ( self.calib_x2 - self.calib_x1 ) ** 2 + ( self.calib_y2 - self.calib_y1 ) ** 2 ) ** 1/2
            actual_dist = dist / self.zoom
            #print x2, y2, dist, actual_dist
            #print 
            
            res = self.calibration_dialog.ShowModal()
            if res == wx.ID_OK:
                length = self.calibration_dialog.GetValue()
                self.pixels_per_millimeter = float( actual_dist )/ float( length )
                #print self.pixels_per_millimeter, "pixels in 1 mm" 
            self.calibration_dialog.Hide()
            #self.calibDlg.Destroy()
            self.DrawToBuffer()
            self.parent_dialog.ApplyCalibrationResult()
            self.SetMode( ID_POINT_MODE )
            #self.mode = ID_2D_POINT_MODE
            #self.Refresh(False)
    
    def EndDragging(self,event):
        if self.is_dragging_image:
            self.in_motion = False
            self.is_dragging_image = False
            self.x, self.y = event.GetPosition()
            self.img_left = self.img_left + (self.x - self.lastx)
            self.img_top = self.img_top+ self.y - self.lasty
            self.lastx = self.x
            self.lasty = self.y
            self.ReleaseMouse()
            #self.AdjustObjectRotation()
            self.Refresh(False)
    
    def OnMotion(self,event):
        #t0 = time.time()
        #print self.mode
        #print "motion"
        self.x, self.y = event.GetPosition()
        #self.x = max( 0, self.x )
        #self.x = min( self.GetSize().width, self.x )
        #self.y = max( 0, self.y )
        #self.y = min( self.GetSize().height, self.y )
        #print self.mode, ID_POINT_MODE
          
        if self.is_dragging_image: #event.Dragging() and event.LeftIsDown():
            #print "dragging image"
            #print "img_left", self.img_left
            #print "img_top", self.img_top
            #print "self.x", self.x
            #print "self.y", self.y
            #print "self.lastx", self.lastx
            #print "self.lasty", self.lasty
            if not self.in_motion:
                self.in_motion = True
                #self.SetCursor( wx.StockCursor( wx.CURSOR_HAND ) )
            old_left = self.img_left
            old_top = self.img_top
            self.img_left = self.img_left + self.x - self.lastx 
            self.img_top = self.img_top + self.y - self.lasty
            if not self.IsImageInside():
                self.img_left = old_left
                self.img_top = old_top
                return
            self.crop_x1, self.crop_y1 = self.ScreenXYtoImageXY( 0, 0 )
            self.crop_x2, self.crop_y2 = self.ScreenXYtoImageXY( self.GetSize().width, self.GetSize().height )
            #if crop_x1 < 
            self.lastx = self.x
            self.lasty = self.y
            self.RefreshImage()
        elif self.is_calibrating:
            #print "calibrating"
            self.calib_x2, self.calib_y2 = self.x, self.y
            self.calib_x2 = self.x
            self.calib_y2 = self.y
            self.DrawToBuffer()
        elif self.mode == ID_POINT_MODE:
            #print "point mode"
            hit, point_idx = self.IsCursorOnPoint()
            if hit:
                self.SetMode( ID_POINT_EDIT_MODE )
                #self.cursor_on_idx = point_idx
                self.curr_point_idx = point_idx
                self.temp_point_list = []
                self.temp_point_list[::] = self.point_list[::]
        elif self.mode == ID_POINT_EDIT_MODE :
            #print "point edit mode"
            
            if self.is_dragging_point:
                #print "curr_point_idx", self.curr_point_idx-1
                #print "zoom", self.zoom
                p = self.point_being_moved
                #print "xdiff", self.x, self.lastx, ( self.x - self.lastx ), (self.x - self.lastx ) / self.zoom 
                
                self.parent_dialog.point_list[self.curr_point_idx-1] = [ p[0] + math.floor( ( self.x - self.lastx) / self.zoom + 0.5 ), p[1] + math.floor( ( self.y - self.lasty ) / self.zoom + 0.5 )]
            hit, point_idx = self.IsCursorOnPoint()
            if not hit:
                self.SetMode( ID_POINT_MODE )
                self.curr_point_idx = -1
        elif self.mode == ID_WIREFRAME_MODE :
            print "wireframe_mode"
            hit, point_idx = self.IsCursorOnPoint()
            if hit:
                self.SetMode( ID_WIREFRAME_EDIT_MODE )
                self.begin_wire_idx = point_idx
                self.hovering_edge = []
            else:
                #print "0"
                hit, edge = self.IsCursorOnWireframe()
                #print "result:", hit, edge
                if hit:
                    self.SetMode( ID_WIREFRAME_EDIT_MODE )
                    self.hovering_edge = edge
                    #print "edge:",edge
                else:
                    self.hovering_edge = []
            #self.DrawToBuffer()
        elif self.mode == ID_WIREFRAME_EDIT_MODE :
            print "wireframe_edit_mode"
            hit, point_idx = self.IsCursorOnPoint()
            #print hit, point_idx, self.begin_wire_idx, self.end_wire_idx
            if not hit:
                #print "not hit"
                self.end_wire_idx = -1
                if self.is_dragging_wire:
                    self.wire_to_x = self.x
                    self.wire_to_y = self.y
                else:
                    hit, edge = self.IsCursorOnWireframe()
                    if hit:
                        self.hovering_edge = edge
                    else:
                        self.SetMode( ID_WIREFRAME_MODE )
                        self.begin_wire_idx = -1
                        # draw dangling wire
            else:
                #print "begin_wire", self.begin_wire_idx, "curr_idx", point_idx
                if self.begin_wire_idx == -1:
                    self.begin_wire_idx = point_idx
                self.hovering_edge = []
                if self.begin_wire_idx != point_idx:
                    #to_lm = self.GetParent().GetParent().point_list[lm_idx]
                    #self.wire_to_x, self.wire_to_y = self.ImageXYtoScreenXY(to_lm[1],to_lm[2])
                    self.end_wire_idx = point_idx
        elif self.mode == ID_BASELINE_MODE :
            print "baseline_mode"
            hit, lm_idx = self.IsCursorOnPoint()
            if hit:
                self.SetMode( ID_BASELINE_EDIT_MODE )
                self.begin_baseline_idx = point_idx
            else:
                self.begin_baseline_idx = -1
        elif self.mode == ID_BASELINE_EDIT_MODE :
            print "baseline_edit_mode"
            hit, point_idx = self.IsCursorOnPoint()
            #print hit, point_idx, self.begin_wire_idx, self.end_wire_idx
            if not hit:
                self.end_baseline_idx = -1
                if self.is_dragging_baseline:
                    self.baseline_to_x = self.x
                    self.baseline_to_y = self.y
                else:
                    self.SetMode( ID_BASELINE_MODE )
                    self.baseline_wire_idx = -1
                    # draw dangling wire
            else:
                if self.begin_baseline_idx != point_idx:
                #to_point = self.GetParent().GetParent().point_list[lm_idx]
                #self.baseline_to_x, self.baseline_to_y = self.ImageXYtoScreenXY(to_lm[1],to_lm[2])
                    self.end_baseline_idx = point_idx
        self.img_x, self.img_y = self.ScreenXYtoImageXY( self.x, self.y )
        #print "on motion 1", time.time() - t0
        self.DrawToBuffer()
        #print "on motion 2", time.time() - t0
        
    def get_dist_criterion(self):
        dist_criterion = 5.0
        if self.zoom > 2:
            dist_criterion *= ( 1 + self.zoom ** 2  / 10 )
        return dist_criterion
      
    
    def IsCursorOnPoint(self):
        #return
        t0 = time.time()
        i = 1
        found = False
        #print "point_list", self.parent_dialog.point_list
        for p in self.parent_dialog.point_list:
            x, y = self.ImageXYtoScreenXY(p[0], p[1])
            dist = self.get_distance( x, y, self.x, self.y )
            #print i, "dist", dist
            if dist < self.get_dist_criterion():
                found = True
                #print "point", i
                break
            i += 1
        #print "iscursoronpoint", time.time() - t0
        return found, i
    
    def IsCursorOnWireframe(self):
        return
        #print "1"
        i = 1
        found = False
    
        #edge_list = self.GetParent().GetParent().edge_list
        point_list = self.point_list
        
        #print "2"
        dist_criterion = self.get_dist_criterion()
    
        found_edge = []
        #print "3", dist_criterion
        i = 1
        
        '''
        for edge in edge_list:
          #print "edge", i, edge
          #print vertex
          vfrom = int( edge[0] ) - 1
          vto = int( edge[1] ) -1 
          ( x1, y1 ) = self.ImageXYtoScreenXY( point_list[vfrom][1], point_list[vfrom][2] )
          ( x2, y2 ) = self.ImageXYtoScreenXY( point_list[vto][1], point_list[vto][2] )
          max_x = max( x1, x2 )
          min_x = min( x1, x2 )
          max_y = max( y1, y2 )
          min_y = min( y1, y2 )
          #print "5", x1, y1, x2, y2
          #print "6", self.x, self.y, max_x, min_x, max_y, min_y
          
          if ( self.x > ( max_x + dist_criterion ) ) or ( self.x < min_x - dist_criterion ) or ( self.y > max_y + dist_criterion ) or ( self.y < min_y - dist_criterion ):
            i+= 1
            continue
          #print "7"
          #print vfrom, vto, len( point_list )\
          vec = [ x2 - x1, y2 - y1 ]
          curr_pos = [ self.x - x1, self.y - y1 ]
          ab = curr_pos[0] * vec[0] + curr_pos[1] * vec[1]
          abs_b2 = vec[0] ** 2.0 + vec[1] ** 2.0
          c = [ ( ab / abs_b2 ) * vec[0], ( ab / abs_b2 ) * vec[1] ]
          dist = self.get_distance( c[0], c[1], curr_pos[0], curr_pos[1] )
          #print "projection:", c[0], c[1], "from", vec[0], vec[1]
          #print "curr", curr_pos[0], curr_pos[1]
          #print "dist:", dist, dist_criterion
          
          
          if dist < dist_criterion :
            found = True
            found_edge = edge
            break
          i+= 1
        '''
        return found, found_edge
    
    def get_distance_from_line(self, x1, y1, from_x, from_y, to_x, to_y):     
        pass
        #self.img_x = math.floor( ( self.x - self.img_left ) / self.zoom + 0.5 )
        #self.img_y = math.floor( ( self.y - self.img_top) / self.zoom + 0.5 )
        #print self.x, self.y, self.img_x, self.img_y
    def get_distance(self, x1, y1, x2, y2 ):
        x2 = float( x2 - x1 ) ** 2.0
        y2 = float( y2 - y1 ) ** 2.0
        dist = ( x2 + y2 ) ** 0.5
        return dist
      
    
    def DrawToBuffer(self):
        t0 = time.time()
        zoomed_image = self.currimg
        #print "prepare image", time.time() - t0
        
        dc = wx.BufferedDC( wx.ClientDC(self), self.buffer )
        dc.SetBackground( wx.GREY_BRUSH )
        dc.Clear()
        left = self.img_left
        top = self.img_top
        if left < 0: 
            left = 0
        if top < 0:
            top = 0
        #print "image wxh", zoomed_image.GetWidth(), zoomed_image.GetHeight()
        #print top, left
        dc.DrawBitmap( wx.BitmapFromImage( zoomed_image ), left, top )
        dc.SetPen(wx.Pen("red",1))
        #dc.SetBrush(wx.RED_BRUSH)
        dc.SetTextForeground(wx.RED)
        idxFont = wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL)    
        if self.is_calibrating:
            dc_x1, dc_y1 = self.calib_x1, self.calib_y1
            dc_x2, dc_y2 = self.calib_x2, self.calib_y2
            #print dc_x1, dc_y1, dc_x2, dc_y2
            #print self.calib_x1, self.calib_y1, self.calib_x2, self.calib_y2
            dc.SetPen(wx.Pen("red",1))
            dc.DrawCircle( dc_x1, dc_y1, 3 )
            dc.DrawCircle( dc_x2, dc_y2, 3 )
            dc.DrawLine( dc_x1, dc_y1, dc_x2, dc_y2 )
        
        if False:
            point_list = self.border_point_list
            if len( point_list ) > 0:
                dc.SetPen( wx.Pen("red",2))
                for i in range( len( point_list ) - 1 ) :
                    x1, y1 = self.ImageXYtoScreenXY(point_list[i][0], point_list[i][1])
                    x2, y2 = self.ImageXYtoScreenXY(point_list[i+1][0], point_list[i+1][1])
                    #x2, y2 = self.ImageXYtoScreenXY(pt[0], pt[1])
                    dc.DrawLine( x1, y1, x2, y2 )
                    #print "border", pt
                x1, y1 = self.ImageXYtoScreenXY(point_list[i][0], point_list[i][1])
                x2, y2 = self.ImageXYtoScreenXY(point_list[0][0], point_list[0][1])
                dc.DrawLine( x1, y1, x2, y2 )
            
        point_list = self.parent_dialog.point_list
        #print point_list
        
        dc.SetTextForeground(wx.RED)
        dc.SetPen(wx.Pen("red",1))
        
        if self.show_wireframe:
            for i in range( len( point_list ) ):
                #if vertex == self.hovering_edge:
                #  dc.SetPen( wx.Pen("red", 3 ))
                #else:
                dc.SetPen( wx.Pen("red", 1 ))
                vfrom = i
                vto = i - 1
                #print vfrom, vto, len( point_list )
                #print "draw wire"
                point_from = point_list[vfrom]
                point_to = point_list[vto]
                dc_x1, dc_y1 = self.ImageXYtoScreenXY(point_from[0], point_from[1])
                dc_x2, dc_y2 = self.ImageXYtoScreenXY(point_to[0], point_to[1])
                dc.DrawLine( dc_x1, dc_y1, dc_x2, dc_y2 )
        '''
        if self.mode == ID_WIREFRAME_EDIT_MODE and self.begin_wire_idx >= 0:
        #print self.begin_wire_idx, self.end_wire_idx
        if self.is_dragging_wire:
          from_point= self.point_list[self.begin_wire_idx-1]
          wire_from_x, wire_from_y = self.ImageXYtoScreenXY(from_lm[1],from_lm[2])
          if self.end_wire_idx >= 0:
            to_lm = self.GetParent().GetParent().point_list[self.end_wire_idx-1]
            wire_to_x, wire_to_y = self.ImageXYtoScreenXY(to_lm[1],to_lm[2])
          else:
            wire_to_x = self.x
            wire_to_y = self.y
          dc.DrawLine( wire_from_x, wire_from_y, wire_to_x, wire_to_y)
        #self.Refresh(False)
        '''
        i = 1
        #print "curr:", self.curr_point_idx
        for p in point_list:
            #print "i", i
            radius = 4
            dc.SetPen(wx.Pen("red",1))
            if self.begin_wire_idx == i or self.end_wire_idx == i or self.curr_point_idx == i:
                radius = 6
            if self.begin_baseline_idx == i or self.end_baseline_idx == i :
                #print i, self.begin_baseline_idx
                dc.SetPen(wx.Pen("blue",1))
                radius = 6
            dc_x, dc_y = self.ImageXYtoScreenXY( p[0], p[1] ) #
            #dc_x = math.floor( lm[1] * self.zoom + 0.5 ) + self.img_left
            #dc_y = math.floor( lm[2] * self.zoom + 0.5 ) + self.img_top
            dc.DrawCircle( dc_x, dc_y, int(radius) )
            #print dc_x, dc_y
            #dc.DrawPoint( dc_x, dc_y ) 
            '''
            if self.show_index:
              dc.DrawText( str( i ), dc_x + 5, dc_y - 8 )
            '''
            i += 1
        
        
        ''' draw scale bar '''
        if self.pixels_per_millimeter > 0:
            #print "draw scale bar"
            MAX_SCALEBAR_SIZE = 120
            bar_width = float( self.pixels_per_millimeter ) * self.zoom
            actual_length = 1.0
            while bar_width > MAX_SCALEBAR_SIZE:
                bar_width /= 10
                actual_length /= 10
            while bar_width < MAX_SCALEBAR_SIZE:
                if bar_width * 10 < MAX_SCALEBAR_SIZE:
                    bar_width *= 10
                    actual_length *= 10
                else:
                    if bar_width * 5 < MAX_SCALEBAR_SIZE:
                        bar_width *= 5
                        actual_length *= 5
                    elif bar_width * 2 < MAX_SCALEBAR_SIZE:
                        bar_width *= 2
                        actual_length *= 2
                    break
            bar_width = int( math.floor( bar_width + 0.5 ) )
            x = self.GetSize().width - 15 - ( bar_width + 20 )
            y = self.GetSize().height - 15 - 30
            dc.SetPen( wx.Pen('black',1))
            dc.SetTextForeground(wx.BLACK)
            dc.DrawRectangle( x, y, bar_width + 20, 30 )
            x += 10
            y += 20
            dc.DrawLine( x, y, x + bar_width, y )
            dc.DrawLine( x, y-5, x, y+5 )
            dc.DrawLine( x+bar_width, y-5, x+bar_width, y+5 )
            length_text = str( actual_length ) + " mm"
            #print length_text, len( length_text )
            dc.DrawText( length_text, x + int( math.floor( float( bar_width ) / 2.0 + 0.5 ) ) - len( length_text ) * 4, y - 15 ) 
          
    def SetWireframe(self,wireframe):
        self.wireframe = wireframe
    
    def CropImage(self, image ):
        self.crop_x1 = max( self.crop_x1, 0 )
        self.crop_x2 = min( self.crop_x2, image.GetWidth() )
        self.crop_y1 = max( self.crop_y1, 0 )
        self.crop_y2 = min( self.crop_y2, image.GetHeight() )
        rect = wx.Rect( self.crop_x1, self.crop_y1, self.crop_x2 - self.crop_x1, self.crop_y2 - self.crop_y1 )
        cropped_image = image.GetSubImage( rect )
        #print "crop:", cropped_image.GetWidth(), cropped_image.GetHeight()
        return cropped_image
    
    
    def OnPaint(self,event):
        #print "OnPaint"
        wx.BufferedPaintDC(self, self.buffer)
        #dc.DrawBitmap( wx.BitmapFromImage( self.currimg ), img_left, img_top, True )
        #dc.DrawCircle( 200,200,100)
        #dc.WriteBitmap( wx.BitmapFromImage( self.img ), 0, 0 )
      
    def OnMouseEnter(self, event):
        #wx.StockCursor(wx.CURSOR_CROSS)
        self.SetFocus()
        #def OnMouseLeave(self, event):
        #  wx.StockCursor(wx.CURSOR_ARROW)
    
    def OnWheel(self,event):
        #print "on wheel, zoom:", self.zoom
        if not self.has_image:
            return
        rotation = event.GetWheelRotation()
        #curr_scr_x, curr_scr_y = event.GetPosition()
        self.ModifyZoom( rotation )
    
    def ModifyZoom(self,rotation):
        curr_scr_x = int( self.GetSize().width / 2 )
        curr_scr_y = int( self.GetSize().height / 2 )
        
        #curr_img_x = int( math.floor( ( ( curr_scr_x - self.img_left ) / self.zoom ) + 0.5 ) )
        #curr_img_y = int( math.floor( ( ( curr_scr_y - self.img_top ) / self.zoom ) + 0.5 ) )
        
        old_zoom = self.zoom
        curr_img_x, curr_img_y = self.ScreenXYtoImageXY( curr_scr_x, curr_scr_y )
        
        ZOOM_MAX = 10
        ZOOM_MIN = 0.1
        if self.zoom < 1:
            factor = 0.5
        else:
            factor = int( self.zoom )
        self.zoom += 0.1 * factor * rotation / ( ( rotation ** 2 ) ** 0.5 ) 
        self.zoom = min( self.zoom, ZOOM_MAX )
        self.zoom = max( self.zoom, ZOOM_MIN )
        #print "zoom", self.zoom
        old_left = self.img_left 
        old_top = self.img_top
        self.img_left = int( math.floor( curr_scr_x - curr_img_x * self.zoom + 0.5 ) )  
        self.img_top = int( math.floor( curr_scr_y - curr_img_y * self.zoom + 0.5 ) )
        #print "img pos", self.img_left, self.img_top
        if not self.IsImageInside():
            self.img_left = old_left
            self.img_top = old_top
            self.zoom = old_zoom
            return
        
        self.crop_x1, self.crop_y1 = self.ScreenXYtoImageXY( 0, 0 )
        self.crop_x2, self.crop_y2 = self.ScreenXYtoImageXY( self.GetSize().width, self.GetSize().height )
        #print crop_x1, crop_y1, crop_x2, crop_y2
        self.RefreshImage()
    
    def ApplyOutline(self, img ):
        point_list = self.border_point_list
        if len( point_list ) > 0:
            for i in range( len( point_list ) - 1 ) :
                img.SetRGB( point_list[i][0], point_list[i][1], 255, 0, 0 )
        return img
    
    def RefreshImage(self):  
        image = self.origimg
        #t0 = time.time()
        with_outline = self.ApplyOutline( image )
        cropped_image = self.CropImage( with_outline )
        #print "crop", time.time() - t0
        #adjusted_image = self.AdjustBrightnessAndContrast( cropped_image )
        adjusted_image = cropped_image
        #print "b/c", time.time() - t0
        zoomed_image = self.ApplyZoom( adjusted_image )
        #print "zoom", time.time() - t0
        self.currimg = zoomed_image
        self.DrawToBuffer()
      
    def ScreenXYtoImageXY(self,x,y):
        new_x = int( math.floor( ( ( x - self.img_left ) / self.zoom ) + 0.5 ) )
        new_y = int( math.floor( ( ( y - self.img_top  ) / self.zoom ) + 0.5 ) )
        #print "screenxy", x, y, "toimagexy", new_x, new_y, "img left&top", self.img_left, self.img_top
        return new_x,new_y
    
    def ImageXYtoScreenXY(self,x,y):
        x = float(x)
        y = float(y)
        new_x = int( math.floor( ( ( x + 0.5 ) * self.zoom + self.img_left ) + 0.5 ) ) 
        new_y = int( math.floor( ( ( y + 0.5 ) * self.zoom + self.img_top  ) + 0.5 ) )
        return new_x,new_y
    
    def ApplyZoom(self, image):
        w = int( image.GetWidth() * self.zoom )
        h = int( image.GetHeight() * self.zoom )
        zoomed_image = image.Scale( w, h )
        return zoomed_image
          
    def AdjustBrightnessAndContrast( self, image ):
        #print "brightness, contrast"
        img = imagetopil( image )
        br_enhancer = ImageEnhance.Brightness( img )
        new_img = br_enhancer.enhance( self.brightness_adjustment )
        cont_enhancer = ImageEnhance.Contrast( new_img )
        new_img = cont_enhancer.enhance( self.contrast_adjustment )
        new_wximg = piltoimage( new_img )
        return new_wximg 
    
    def ApplyBrightnessAndContrast( self ):
        #print "brightness, contrast"
        img = imagetopil( self.origimg )
        br_enhancer = ImageEnhance.Brightness( img )
        new_img = br_enhancer.enhance( self.brightness_adjustment )
        cont_enhancer = ImageEnhance.Contrast( new_img )
        new_img = cont_enhancer.enhance( self.contrast_adjustment )
        new_wximg = piltoimage( new_img )
        self.ReplaceImage( new_wximg )
        return #new_wximg 

    def ReplaceImage(self, image ):
        self.image_list.append( self.origimg )
        #print image
        self.origimg = image
        self.MakeThumbnail()
        self.RefreshImage()        

    def UndoImageOperation( self ):
        if len( self.image_list ) > 0:
            self.redo_list.append( self.origimg ) 
            self.origimg = self.image_list.pop()
            #print self.origimg
            #self.ResetImage()
            self.MakeThumbnail()
            self.RefreshImage()        

    def RedoImageOperation( self ):
        #print "redo"
        if len( self.redo_list ) > 0:
            img = self.redo_list.pop()
            #print img
            self.ReplaceImage( img )

    def ApplyThreshold( self ):
        #print "brightness, contrast"
        img = imagetopil( self.origimg )
        out = img.point(lambda i: i > self.threshold and 255)        
        new_img = out.convert("P").convert("1")
        new_wximg = piltoimage( new_img )
        self.ReplaceImage( new_wximg )
        return
        #return new_wximg 
    
    def SetBrightness(self, bright ):
        if bright <= 0 :
            bright /= 100.0 * 2
        else:
            bright /= 100.0 * 2
        new_brightness = bright + 1.0
        self.brightness_adjustment = new_brightness
        print "brightness", self.brightness_adjustment
        #self.RefreshImage()

    def SetContrast(self, contrast):
        if contrast <= 0 :
            contrast /= 100.0 * 2
        else:
            contrast /= 100.0 * 2
        new_contrast = contrast + 1.0
        self.contrast_adjustment = new_contrast
        print "contrast", self.contrast_adjustment
        #self.RefreshImage()
    
    def SetThreshold(self,threshold):
        self.threshold = threshold
    
    def CopyImage(self):
        return self.origimg
    
    def PasteImage(self,image):
        self.ReplaceImage( image )#self.origimg = image
    
    def ShowWireframe(self):
        self.show_wireframe = True
        self.DrawToBuffer()
        #self.OnDraw()
    
    def HideWireframe(self):
        self.show_wireframe = False
        self.DrawToBuffer()
        #self.OnDraw()
    
    def ShowBaseline(self):
        self.show_baseline = True
        self.DrawToBuffer()
        #self.OnDraw()
    
    def HideBaseline(self):
        self.show_baseline = False
        self.DrawToBuffer()
    
    def ShowIndex(self):
        self.show_index= True
        self.DrawToBuffer()
    
    def HideIndex(self):
        self.show_index = False
        self.DrawToBuffer()
        #self.OnDraw()

    def SetKernel(self, kernel ): 
        self.kernel = kernel     
        
    def ApplyKernel( self, foreground_color ):
        image = self.origimg
        width = image.GetWidth()
        height = image.GetHeight()
        new_image = image.Copy()
        for x in range( width ):
            for y in range( height ):
                pixel_val = self.GetPixelValue( x, y )
                if pixel_val != foreground_color:
                    #print x, y, pixel_val 
                    for coord in self.kernel:
                        temp_x = min( max( x + coord[0], 0 ), width - 1 )
                        temp_y = min( max( y + coord[1], 0 ), height - 1 )
                        if self.GetPixelValue( temp_x, temp_y ) == foreground_color:
                            new_image.SetRGB( x, y, foreground_color, foreground_color, foreground_color )
                            break
        self.ReplaceImage( new_image )
                
    def ResetImage(self):
        #print "refresh_img", self.origimg
        img_w = self.origimg.GetWidth()
        img_h = self.origimg.GetHeight()
        self_w = self.GetSize().width
        self_h = self.GetSize().height
        #print img_w, img_h, self_w, self_h
        zoom = 1.0
        if img_w > self_w or img_h > self_h:
            zoom = min( float( self_w ) / float( img_w) , float( self_h ) / float( img_h ) ) 
        elif img_w < self_w and img_h < self_h:
            zoom = min( float( self_w ) / float( img_w ), float( self_h ) / float( img_h ) )
        self.zoom = zoom
        #print zoom
        self.buffer = wx.BitmapFromImage( wx.EmptyImage(self.width,self.height))
        self.has_image = True
        self.x = self.y = self.lastx = self.lasty = 0
        self.brightness_adjustment = self.contrast_adjustment = 1.0
        self.img_left = self.img_top = 0
        self.in_motion = False
        self.is_dragging_image = False
        self.crop_x1 = self.crop_y1 = 0
        self.crop_x2 = img_w
        self.crop_y2 = img_h
        self.calib_x1 = self.calib_y1 = -1
        self.calib_x2 = self.calib_y2 = -1
        #print zoom
        self.zoom = zoom
        self.RefreshImage()
        #self.DrawToBuffer()
        #self.GetParent().GetParent().ClearPointList()
        #self.Refresh(True)
    

def piltoimage(pil,alpha=True):
    """Convert PIL Image to wx.Image."""
    if alpha:
        #print "alpha 1", clock()
        image = apply( wx.EmptyImage, pil.size )
        #print "alpha 2", clock()
        image.SetData( pil.convert( "RGB").tostring() )
        #print "alpha 3", clock()
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
        #print "alpha 4", clock()
    else:
        #print "no alpha 1", clock()
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        #print "no alpha 2", clock()
        new_image = pil.convert('RGB')
        #print "no alpha 3", clock()
        data = new_image.tostring()
        #print "no alpha 4", clock()
        image.SetData(data)
        #print "no alpha 5", clock()
    #print "pil2img", image.GetWidth(), image.GetHeight()
    return image

def imagetopil(image):
    """Convert wx.Image to PIL Image."""
    #print "img2pil", image.GetWidth(), image.GetHeight()
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil
    
