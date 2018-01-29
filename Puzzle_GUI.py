import os
import threading

import wx

from PuzzleParser import fetch_data, load_puzzle

WINDOW_SIZE_X = 960
WINDOW_SIZE_Y = 540
LABEL_W = WINDOW_SIZE_X / 4
LABEL_H = WINDOW_SIZE_Y / 15
TILE_WH = (WINDOW_SIZE_X - 2 * LABEL_W) / 5
BUTTON_W = TILE_WH * 5 / 4
BUTTON_H = WINDOW_SIZE_Y - 5 * TILE_WH

DARK_PURPLE = (40, 30, 40, 255)
HL_PURPLE = (100, 90, 100, 255)
SEMIHL_PURPLE = (180, 170, 180, 255)
LIGHT_PURPLE = (210, 200, 210, 255)


class MenuPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent,
                          pos=(0, 0), size=(WINDOW_SIZE_X, WINDOW_SIZE_Y))

        self.panel = PuzzlePanel(parent)
        self.panel.Hide()

        self.menu_button_daily = wx.Button(self, wx.ID_ANY, "Daily",
                                           pos=(WINDOW_SIZE_X / 2 - BUTTON_W / 2, WINDOW_SIZE_Y / 4 - BUTTON_H / 2),
                                           size=(BUTTON_W, BUTTON_H))
        self.menu_button_daily.SetForegroundColour(DARK_PURPLE)

        self.menu_button_load = wx.Button(self, wx.ID_ANY, "Load",
                                          pos=(WINDOW_SIZE_X / 2 - BUTTON_W / 2, WINDOW_SIZE_Y / 2 - BUTTON_H / 2),
                                          size=(BUTTON_W, BUTTON_H))

        # Connect Events
        self.menu_button_daily.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "daily"))
        self.menu_button_load.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "load"))

    def button_events(self, event, puzzle_name=""):
        try:
            self.menu_button_daily.Disable()
            self.menu_button_load.Disable()
            if puzzle_name == "daily":
                p = fetch_data("https://www.nytimes.com/crosswords/game/mini")

            elif puzzle_name == "load":
                with wx.FileDialog(self, "Open MINI file", wildcard="*.mini",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                    fileDialog.SetDirectory("mini")
                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return  # the user changed their mind

                    filename = fileDialog.GetPath()
                    try:
                        p = load_puzzle(filename)
                    except IOError:
                        dlg = wx.MessageDialog(self, "Cannot open file", wx.OK | wx.ICON_WARNING)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return
            else:
                return

            self.Hide()
            self.panel.Show()
            self.panel.insert_puzzle(p)
        finally:
            self.menu_button_daily.Enable()
            self.menu_button_load.Enable()


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
def pass_empty(puzzle_matrix, isacross, x, y, i):
    while True:
        if isacross:
            y += i
            if not 0 <= y < 5:
                x = (x + i) % 5
                y = y % 5
        else:
            x += i
            if not 0 <= x < 5:
                x = x % 5
                y = (y + i) % 5
        if puzzle_matrix[x][y] != 36:
            return x, y


class PuzzlePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent,
                          pos=(0, 0), size=(WINDOW_SIZE_X, WINDOW_SIZE_Y))
        self.hl_i = 0
        self.hl_j = 0
        self.hl_across = True
        self.clue_index_list = []
        self.puzzle = None
        self.curr_feas_index = -1
        self.feasible_answers = []
        self.answers = AnswerFrame(self)
        self.answers.Hide()

        self.CLUE_TITLE = wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.TILE_FONT = wx.Font(int(TILE_WH / 2), wx.MODERN, wx.NORMAL, wx.BOLD)

        # Across Clues
        size = (LABEL_W, LABEL_H)
        self.across_clue_title = wx.StaticText(self, -1, label="Across", pos=(LABEL_W / 4, LABEL_H), size=size)
        self.across_clue_title.SetFont(self.CLUE_TITLE)
        self.across_clue_list = []
        for i in range(5):
            self.across_clue_list.append(
                wx.StaticText(self, -1, pos=(LABEL_W / 4, (i + 2) * LABEL_H), size=size))

        # Down Clues
        size = (LABEL_W, LABEL_H)
        self.down_clue_title = wx.StaticText(self, -1, label="Down", pos=(LABEL_W / 4, 8 * LABEL_H), size=size)
        self.down_clue_title.SetFont(self.CLUE_TITLE)
        self.down_clue_list = []
        for i in range(5):
            self.down_clue_list.append(
                wx.StaticText(self, -1, pos=(LABEL_W / 4, (i + 9) * LABEL_H), size=size))

        # Buttons
        size = (BUTTON_W, BUTTON_H)
        self.daily_button = wx.Button(self, -1, label="Daily", pos=(LABEL_W + BUTTON_W, 0), size=size)
        self.daily_button.SetForegroundColour(DARK_PURPLE)
        self.daily_button.SetBackgroundColour(LIGHT_PURPLE)

        self.save_button = wx.Button(self, -1, label="Save", pos=(LABEL_W + 2 * BUTTON_W, 0), size=size)
        self.save_button.SetForegroundColour(DARK_PURPLE)
        self.save_button.SetBackgroundColour(LIGHT_PURPLE)

        self.load_button = wx.Button(self, -1, label="Load", pos=(LABEL_W + 3 * BUTTON_W, 0), size=size)
        self.load_button.SetForegroundColour(DARK_PURPLE)
        self.load_button.SetBackgroundColour(LIGHT_PURPLE)

        self.solve_button = wx.Button(self, -1, label="Solve", pos=(LABEL_W + 4 * BUTTON_W, 0), size=size)
        self.solve_button.SetForegroundColour(DARK_PURPLE)
        self.solve_button.SetBackgroundColour(LIGHT_PURPLE)

        self.show_answers_button = wx.Button(self, -1, label="Show Answers", pos=(LABEL_W + 5 * BUTTON_W, 0), size=size)
        self.show_answers_button.SetForegroundColour(DARK_PURPLE)
        self.show_answers_button.SetBackgroundColour(LIGHT_PURPLE)

        self.prev_button = wx.Button(self, -1, label="Prev", pos=(LABEL_W + 5 * BUTTON_W, BUTTON_H), size=size)
        self.prev_button.SetForegroundColour(DARK_PURPLE)
        self.prev_button.SetBackgroundColour(LIGHT_PURPLE)
        self.next_button = wx.Button(self, -1, label="Next", pos=(LABEL_W + 5 * BUTTON_W, 2 * BUTTON_H), size=size)
        self.next_button.SetForegroundColour(DARK_PURPLE)
        self.next_button.SetBackgroundColour(LIGHT_PURPLE)

        # Puzzle Tiles
        self.tile_list = []
        for i in range(5):
            for j in range(5):
                posx = LABEL_W + BUTTON_W + j * TILE_WH
                posy = BUTTON_H + i * TILE_WH
                sizex = TILE_WH
                sizey = TILE_WH
                a = wx.StaticText(self, -1, label="", pos=(posx, posy), size=(sizex, sizey))
                a.SetBackgroundColour(DARK_PURPLE)
                a.Disable()
                self.tile_list.append(
                    wx.StaticText(self, -1, pos=(posx + 1, posy + 1),
                                  size=(sizex - 2, sizey - 2), style=wx.ALIGN_CENTRE))

        self.tile_index_list = []
        for i in range(10):
            self.tile_index_list.append(wx.StaticText(self, -1, pos=(0, 0), size=(0, 0)))

        # Label Presses
        for i in range(5):
            self.across_clue_list[i].Bind(wx.EVT_LEFT_DOWN, lambda event, x=i: self.highlight_puzzle(event, True, x, 0))
        for i in range(5):
            self.down_clue_list[i].Bind(wx.EVT_LEFT_DOWN, lambda event, y=i: self.highlight_puzzle(event, False, 0, y))
        for i in range(25):
            self.tile_list[i].Bind(wx.EVT_LEFT_DOWN,
                                   lambda event, x=i / 5, y=i % 5: self.highlight_puzzle(event, True, x, y, True))

        # Connect Events
        parent.Bind(wx.EVT_KEY_DOWN, lambda event: self.key_pressed(event))
        self.daily_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "daily"))
        self.save_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "save"))
        self.load_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "load"))
        self.solve_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "solve"))
        self.show_answers_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "show"))
        self.prev_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "prev"))
        self.next_button.Bind(wx.EVT_BUTTON, lambda event: self.button_events(event, "next"))

    def onClose(self, event):
        self.answers.Close()
        self.Close()

    def solve_puzzle(self):
        down_hints = [None for x in range(5)]
        across_hints = [None for x in range(5)]
        for j in range(5):
            temp_str = ""
            i = 0
            while self.puzzle.puzzleMatrix[i][j] == 36:
                i += 1
            while i < 5 and self.tile_list[i * 5 + j].GetLabel() != chr(36) \
                    and self.tile_list[i * 5 + j].GetLabel() != chr(32):
                temp_str += self.tile_list[i * 5 + j].GetLabel()
                i += 1
            if self.puzzle.get_down_char_count(j) == len(temp_str):
                down_hints[j] = {temp_str: 1}

            temp_str = ""
            i = 0
            while self.puzzle.puzzleMatrix[j][i] == 36:
                i += 1
            while i < 5 and self.tile_list[j * 5 + i].GetLabel() != chr(36) \
                    and self.tile_list[j * 5 + i].GetLabel() != chr(32):
                temp_str += self.tile_list[j * 5 + i].GetLabel()
                i += 1
            if self.puzzle.get_across_char_count(j) == len(temp_str):
                across_hints[j] = {temp_str: 1}

        from Evaluator import Evaluator
        e = Evaluator(self.puzzle)

        e.search(across_hints, down_hints)

        result = e.try_freq()

        self.curr_feas_index = 0
        self.feasible_answers = e.feasible_matrices

        print("Complete" if result else "Incomplete", len(self.feasible_answers), "solutions")

        for a in e.feasible_matrices:
            print("-", a)

        if 0 < len(self.feasible_answers):
            for i in range(5):
                for j in range(5):
                    self.tile_list[5 * i + j].SetLabel(self.feasible_answers[0][i][j])

        self.Update()

    def key_pressed(self, event):
        keycode = event.GetKeyCode()

        index = int(self.hl_i * 5 + self.hl_j)
        temp = 0, 0

        if event.GetKeyCode() == wx.WXK_BACK or event.GetKeyCode() == wx.WXK_DELETE:
            self.tile_list[index].SetLabel(" ")
            temp = pass_empty(self.puzzle.puzzleMatrix, self.hl_across, self.hl_i, self.hl_j, -1)

        elif 65 <= keycode <= 90:
            self.tile_list[index].SetLabel(chr(keycode))
            temp = pass_empty(self.puzzle.puzzleMatrix, self.hl_across, self.hl_i, self.hl_j, 1)

        elif keycode == wx.WXK_UP:
            temp = pass_empty(self.puzzle.puzzleMatrix, False, self.hl_i, self.hl_j, -1)
        elif keycode == wx.WXK_DOWN:
            temp = pass_empty(self.puzzle.puzzleMatrix, False, self.hl_i, self.hl_j, 1)
        elif keycode == wx.WXK_LEFT:
            temp = pass_empty(self.puzzle.puzzleMatrix, True, self.hl_i, self.hl_j, -1)
        elif keycode == wx.WXK_RIGHT:
            temp = pass_empty(self.puzzle.puzzleMatrix, True, self.hl_i, self.hl_j, 1)

        self.highlight_puzzle(event, self.hl_across, int(temp[0]), int(temp[1]), False)

    def button_events(self, event, puzzle_name=""):
        self.SetFocus()
        self.daily_button.Disable()
        self.save_button.Disable()
        self.load_button.Disable()
        self.solve_button.Disable()
        self.show_answers_button.Disable()
        self.prev_button.Disable()
        self.next_button.Disable()
        try:
            if puzzle_name == "daily":
                t = threading.Thread(target=self.insert_puzzle,
                                     args=(fetch_data("https://www.nytimes.com/crosswords/game/mini"),))
                t.start()
                t.join()

            elif puzzle_name == "save":
                filename = "mini/" + self.puzzle.date + ".mini"
                if os.path.exists(filename) and os.path.isfile(filename):
                    dlg = wx.MessageDialog(self, "Save already exists", caption=wx.MessageBoxCaptionStr,
                                           style=wx.OK | wx.CENTRE)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    self.puzzle.save(filename)
                    dlg = wx.MessageDialog(self, "Puzzle saved", caption=wx.MessageBoxCaptionStr,
                                           style=wx.OK | wx.CENTRE)
                    dlg.ShowModal()
                    dlg.Destroy()

            elif puzzle_name == "load":
                with wx.FileDialog(self, "Open MINI file", wildcard="*.mini",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                    fileDialog.SetDirectory("mini")
                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return  # the user changed their mind

                    filename = fileDialog.GetPath()
                    try:
                        self.insert_puzzle(load_puzzle(filename))
                    except IOError:
                        dlg = wx.MessageDialog(self, "Cannot open file", wx.OK | wx.ICON_WARNING)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif puzzle_name == "solve":

                import timeit
                start_time = timeit.default_timer()

                self.solve_puzzle()

                import Configs
                if Configs.get_setting('TRY', 'try_solve_time') == '1':
                    time = timeit.default_timer() - start_time
                    import BasicLogger
                    BasicLogger.log(time)
                    print(time)
                self.curr_feas_index = 0

            elif puzzle_name == "show":
                self.answers.show_new_matrix(self.puzzle.answerMatrix)
                self.answers.Show()
                self.SetFocus()

            elif puzzle_name == "prev":
                if 0 < len(self.feasible_answers):
                    self.curr_feas_index = (self.curr_feas_index - 1) % len(self.feasible_answers)
                    if self.curr_feas_index < len(self.feasible_answers):
                        for i in range(5):
                            for j in range(5):
                                a = self.feasible_answers[self.curr_feas_index][i][j]
                                self.tile_list[5 * i + j].SetLabel(a)

            elif puzzle_name == "next":
                if 0 < len(self.feasible_answers):
                    self.curr_feas_index = (self.curr_feas_index + 1) % len(self.feasible_answers)
                    if self.curr_feas_index < len(self.feasible_answers):
                        for i in range(5):
                            for j in range(5):
                                a = self.feasible_answers[self.curr_feas_index][i][j]
                                self.tile_list[5 * i + j].SetLabel(a)
            else:
                return

            self.Layout()
        finally:
            self.daily_button.Enable()
            self.save_button.Enable()
            self.load_button.Enable()
            self.solve_button.Enable()
            self.show_answers_button.Enable()
            self.prev_button.Enable()
            self.next_button.Enable()

    def highlight_puzzle(self, event, is_across, x, y, switch=False):
        x = int(x)
        y = int(y)

        if switch and x == self.hl_i and y == self.hl_j:
            is_across = not self.hl_across

        # Remove Old Highlights
        for i in range(5):
            temp_old = (self.hl_i, i) if self.hl_across else (i, self.hl_j)
            if self.puzzle.puzzleMatrix[temp_old[0]][temp_old[1]] != 36:
                self.tile_list[temp_old[0] * 5 + temp_old[1]].SetBackgroundColour(LIGHT_PURPLE)

        # Add New Highlights
        for i in range(5):
            temp_new = (x, i) if is_across else (i, y)
            color = HL_PURPLE if (y == i if is_across else x == i) else SEMIHL_PURPLE
            if self.puzzle.puzzleMatrix[temp_new] != 36:
                self.tile_list[temp_new[0] * 5 + temp_new[1]].SetBackgroundColour(color)

        for btn in self.tile_list:
            btn.Refresh()

        for btn in self.tile_index_list:
            btn.Refresh()

        self.hl_i = x
        self.hl_j = y
        self.hl_across = is_across

        self.Layout()

    def insert_puzzle(self, puzzle):
        self.puzzle = puzzle

        for i in range(5):
            for j in range(5):
                self.tile_list[5 * i + j].SetBackgroundColour(
                    DARK_PURPLE if puzzle.puzzleMatrix[i][j] == 36 else LIGHT_PURPLE)
                self.tile_list[5 * i + j].SetLabel(
                    " " if puzzle.puzzleMatrix[i][j] == 36
                    else chr(puzzle.puzzleMatrix[i][j]))
                self.tile_list[5 * i + j].SetFont(self.TILE_FONT)

        for i in range(5):
            self.across_clue_list[i].SetLabel(str(puzzle.acrossQuestions[i]['display_index'])
                                              + ". " + puzzle.acrossQuestions[i]['clue'])
            for j in range(5):
                if puzzle.puzzleMatrix[i][j] != 36:
                    self.clue_index_list.append((i, j))
                    pos = (self.tile_list[i * 5 + j].GetPosition())
                    self.tile_index_list[j] = wx.StaticText(self, -1,
                                                            label=str(self.puzzle.acrossQuestions[i]['display_index']),
                                                            pos=(pos[0] + 2, pos[1] + 2),
                                                            size=(TILE_WH / 5, TILE_WH / 5))
                    self.tile_index_list[j].SetBackgroundColour(self.tile_list[i * 5 + j].GetBackgroundColour())
                    break

        for i in range(5):
            self.down_clue_list[i].SetLabel(str(puzzle.downQuestions[i]['display_index'])
                                            + ". " + puzzle.downQuestions[i]['clue'])
            for j in range(5):
                if puzzle.puzzleMatrix[j][i] != 36:
                    self.clue_index_list.append((j, i))
                    pos = (self.tile_list[j * 5 + i].GetPosition())
                    self.tile_index_list[j + 5] = wx.StaticText(self, -1,
                                                                label=str(
                                                                    self.puzzle.downQuestions[i]['display_index']),
                                                                pos=(pos[0] + 2, pos[1] + 2),
                                                                size=(TILE_WH / 5, TILE_WH / 5))
                    self.tile_index_list[j + 5].SetBackgroundColour(
                        self.tile_list[j * 5 + i].GetBackgroundColour())
                    break

        while self.puzzle.puzzleMatrix[self.hl_i][self.hl_j] == 36:
            self.hl_j += 1
            if 4 < self.hl_j:
                self.hl_i = int((self.hl_i + 1) % 5)
                self.hl_j = int(self.hl_j % 5)
        self.highlight_puzzle(None, self.hl_across, self.hl_i, self.hl_j)

        self.curr_feas_index = -1
        self.feasible_answers = []
        self.answers = AnswerFrame(self)
        self.answers.Hide()
        self.Show()
        self.Layout()


class AnswerFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Answers",
                          pos=(100 + WINDOW_SIZE_X, 100), size=(TILE_WH * 5, TILE_WH * 5 + 40))
        self.parent = parent
        pan = wx.Panel(self)

        TILE_FONT = wx.Font(int(TILE_WH / 2), wx.MODERN, wx.NORMAL, wx.BOLD)
        self.answer_tiles = []
        for i in range(5):
            for j in range(5):
                posx = j * TILE_WH
                posy = i * TILE_WH
                sizex = TILE_WH
                sizey = TILE_WH
                a = wx.StaticText(pan, -1, label="", pos=(posx, posy), size=(sizex, sizey))
                a.SetBackgroundColour(DARK_PURPLE)
                a.Disable()
                st = wx.StaticText(pan, -1, pos=(posx + 1, posy + 1),
                                   size=(sizex - 2, sizey - 2), style=wx.ALIGN_CENTRE)
                st.SetFont(TILE_FONT)
                self.answer_tiles.append(st)

    def show_new_matrix(self, matrix):
        for i in range(5):
            for j in range(5):
                self.answer_tiles[5 * i + j].SetLabel(chr(matrix[i][j]))


class App(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="New York's Best Puzzle Solver",
                          pos=(100, 100), size=(WINDOW_SIZE_X, WINDOW_SIZE_Y + 40))

        self.panel = MenuPanel(self)


app = wx.App()
frame = App()
frame.Show()
app.MainLoop()
