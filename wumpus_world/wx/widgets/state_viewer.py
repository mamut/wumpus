import math

import wx

import garlicsim_wx


class StateViewer(wx.Panel, garlicsim_wx.widgets.WorkspaceWidget):

    def __init__(self, frame):
        wx.Panel.__init__(self, frame, style=wx.SUNKEN_BORDER)
        garlicsim_wx.widgets.WorkspaceWidget.__init__(self, frame)

        self.state = None

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
        red_brush = wx.Brush(wx.NamedColor('Red'))
        white_brush = wx.Brush(wx.NamedColor('White'))

        black_pen = wx.Pen(wx.NamedColor('Black'), width=1.5)
        red_pen = wx.Pen(wx.NamedColor('Red'), width=3.0)

        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(background_brush)
        dc.Clear()

        if self.state is None:
            return

        gc = wx.GraphicsContext.Create(dc)
        assert isinstance(gc, wx.GraphicsContext)
        client_width, client_height = self.GetClientSize()
        board_size = self.state.board_size

        def print_board_tile(pos, board_tile):
            xi, yi = pos
            x = xi * 50
            y = (board_size - 1 - yi) * 50

            def print_wumpus():
                gc.SetPen(red_pen)
                gc.SetBrush(red_brush)
                gc.DrawRectangle(x + 15, y + 15, 20, 20)

            def print_pit():
                gc.SetPen(black_pen)
                gc.SetBrush(pit_brush)
                gc.DrawEllipse(x + 5, y + 5, 40, 40)

            def print_player(direction):

                def print_dir():
                    rotation = {
                            'up': 0,
                            'right': math.pi / 2,
                            'down': math.pi,
                            'left': 3 * math.pi / 2
                        }[direction]
                    gc.PushState()
                    gc.Translate(x + 25, y + 25)
                    gc.Rotate(rotation)
                    gc.Translate(0, -10)
                    gc.Rotate(math.pi / 4)
                    dir_side = 20 / math.sqrt(2)
                    gc.DrawRectangle(-dir_side / 2, -dir_side / 2,
                            dir_side, dir_side)
                    gc.PopState()

                gc.SetPen(black_pen)
                gc.SetBrush(white_brush)
                print_dir()
                if self.state.gold_grabbed:
                    gc.SetBrush(gold_brush)
                else:
                    gc.SetBrush(white_brush)
                gc.DrawRectangle(x + 15, y + 15, 20, 20)

            gc.SetPen(black_pen)
            if pos == (0, 0):
                gc.SetBrush(start_brush)
            elif board_tile.gold and not self.state.gold_grabbed:
                gc.SetBrush(gold_brush)
            else:
                gc.SetBrush(background_brush)
            gc.DrawRectangle(x, y, 50, 50)

            if board_tile.pit:
                print_pit()

            if board_tile.wumpus and not self.state.wumpus_dead:
                print_wumpus()

            if self.state.player_pos == pos:
                print_player(self.state.player_dir)

        for pos, board_tile in self.state.board.iteritems():
            print_board_tile(pos, board_tile)

        def print_points():
            dc.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.DrawLabel(str(self.state.points),
                    wx.Rect(0, (client_height - 40), client_width, 40),
                    wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        print_points()

    def on_size(self, event):
        self.Refresh()

