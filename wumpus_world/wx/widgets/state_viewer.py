import wx

import garlicsim_wx


class StateViewer(wx.Panel, garlicsim_wx.widgets.WorkspaceWidget):

    def __init__(self, frame):
        wx.Panel.__init__(self, frame, style=wx.SUNKEN_BORDER)
        garlicsim_wx.widgets.WorkspaceWidget.__init__(self, frame)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM) # Solves Windows flicker

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.gui_project.active_node_changed_emitter.add_output(
            lambda: self.set_state(self.gui_project.get_active_state())
        )

    def set_state(self, state):
        self.state = state
        self.Refresh()

    def on_paint(self, event):
        event.Skip()
        background_brush = wx.Brush(self.GetBackgroundColour())
        start_brush = wx.Brush(wx.NamedColor('Green'))
        gold_brush = wx.Brush(wx.NamedColor('Gold'))
        pit_brush = wx.Brush(wx.NamedColor('Black'))

        black_pen = wx.Pen(wx.NamedColor('Black'), width=1.5)
        wumpus_pen = wx.Pen(wx.NamedColor('Red'), width=3.0)

        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(background_brush)
        dc.Clear()

        if self.state is None:
            return

        gc = wx.GraphicsContext.Create(dc)
        assert isinstance(gc, wx.GraphicsContext)
        client_width, client_height = self.GetClientSize()

        def print_board_tile(pos, board_tile):
            xi, yi = pos
            x = xi * 50
            y = yi * 50

            if board_tile.wumpus:
                gc.SetPen(wumpus_pen)
            else:
                gc.SetPen(black_pen)

            if pos == (0, 0):
                gc.SetBrush(start_brush)
            elif board_tile.gold:
                gc.SetBrush(gold_brush)
            else:
                gc.SetBrush(background_brush)
            gc.DrawRectangle(x, y, 50, 50)

            if board_tile.pit:
                gc.SetBrush(pit_brush)
                gc.DrawEllipse(x + 5, y + 5, 40, 40)

        for pos, board_tile in self.state.board.iteritems():
            print_board_tile(pos, board_tile)

    def on_size(self, event):
        self.Refresh()

