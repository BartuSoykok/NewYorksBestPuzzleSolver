import re
import threading
import BasicLogger
import numpy as np
import Configs
from Searcher import Search


def get_pattern(c, matrix):
    pattern = r'\b'
    for i in c:
        if ord(matrix[i[0]][i[1]]) == 32 or ord(matrix[i[0]][i[1]]) == 36:
            pattern += r'[a-zA-Z]'
        else:
            pattern += matrix[i[0]][i[1]]
    pattern += r'\b'

    return pattern


def compare_matrix(size, a, b):
    for i in range(size):
        for j in range(size):
            if a[i][j] != b[i][j]:
                return False
    return True


class Evaluator:
    across_freq = [dict() for x in range(5)]
    down_freq = [dict() for x in range(5)]

    feasible_matrices = []
    max_sum = 0
    answer_limit = 2

    def __init__(self, puzzle):
        self.puzzle = puzzle

        self.matrix = np.array([['$', '$', '$', '$', '$'],
                                ['$', '$', '$', '$', '$'],
                                ['$', '$', '$', '$', '$'],
                                ['$', '$', '$', '$', '$'],
                                ['$', '$', '$', '$', '$']])
        for i in range(5):
            for j in range(5):
                self.matrix[i][j] = chr(self.puzzle.puzzleMatrix[i][j])

    def search(self, across_hints=[None for x in range(5)], down_hints=[None for x in range(5)]):
        print(across_hints, "\n---", down_hints)
        for i in range(5):
            if across_hints[i] is not None:
                self.across_freq[i] = across_hints[i]
            if len(self.across_freq[i]) == 1:
                c_arr = self.puzzle.get_coordinates(True, i)

                for freq in self.across_freq[i]:
                    # Put word to row
                    for char_index in range(len(freq)):
                        if self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                            self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq[char_index]
                    break

            if down_hints[i] is not None:
                self.down_freq[i] = down_hints[i]
            if len(self.down_freq[i]) == 1:
                c_arr = self.puzzle.get_coordinates(False, i)

                for freq in self.down_freq[i]:
                    # Put word to row
                    for char_index in range(len(freq)):
                        if self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                            self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq[char_index]
                    break

        threads = []
        for m in range(5):
            if Configs.get_setting('METHOD', 'internet') == '1' and across_hints[m] is None:
                t = threading.Thread(target=self.basic_search_thread, args=(True, m,))
                t.start()
                threads.append(t)
            elif Configs.get_setting('METHOD', 'hint') == '1':
                self.across_freq[m] = across_hints[m]
        for m in range(5):
            if Configs.get_setting('METHOD', 'internet') == '1' and down_hints[m] is None:
                t = threading.Thread(target=self.basic_search_thread, args=(False, m,))
                t.start()
                threads.append(t)
            elif Configs.get_setting('METHOD', 'hint') == '1':
                self.down_freq[m] = down_hints[m]
        for t in threads:
            t.join()

        #################
        # SORT
        for i in range(5):
            temp_freq = dict()
            from collections import OrderedDict
            for key_i, value_i in OrderedDict(
                    sorted(self.across_freq[i].items(), key=lambda t: t[1], reverse=True)).items():
                temp_freq[key_i] = value_i
            self.across_freq[i] = temp_freq

            temp_freq = dict()
            from collections import OrderedDict
            for key_i, value_i in OrderedDict(
                    sorted(self.down_freq[i].items(), key=lambda t: t[1], reverse=True)).items():
                temp_freq[key_i] = value_i
            self.down_freq[i] = temp_freq

        if Configs.get_setting('DEBUG', 'print_freq') == '1':
            BasicLogger.log("Threads finished")
            print("Threads finished")

    def try_freq(self):

        for i in range(5):
            if len(self.across_freq[i]) == 1:
                c_arr = self.puzzle.get_coordinates(True, i)

                for freq in self.across_freq[i]:
                    # Put word to row
                    for char_index in range(len(freq)):
                        if self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                            self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq[char_index]
                    break

            if len(self.down_freq[i]) == 1:
                c_arr = self.puzzle.get_coordinates(False, i)

                for freq in self.down_freq[i]:
                    # Put word to row
                    for char_index in range(len(freq)):
                        if self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                            self.matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq[char_index]
                    break

        temp_sum = 0
        for x in range(5):
            for y in range(5):
                if ord(self.matrix[x][y]) != 32 and ord(self.matrix[x][y]) != 36:
                    temp_sum += 1

        for i in range(5):
            if '_' in self.puzzle.acrossQuestions[i]['clue']:
                return self.try_across(self.matrix, i)
            if '_' in self.puzzle.acrossQuestions[i]['clue']:
                return self.try_down(self.matrix, i)
        return self.try_across(self.matrix, 0)

    def try_across(self, matrix, i):
        c_arr = self.puzzle.get_coordinates(True, i)

        # Create pattern
        temp_str = r'\b'
        for c in c_arr:
            if ord(matrix[c[0]][c[1]]) == 32 or ord(matrix[c[0]][c[1]]) == 36:
                temp_str += r'[a-zA-Z]'
            else:
                temp_str += "[" + matrix[c[0]][c[1]] + "]"
        temp_str += r'\b'
        pattern = re.compile(temp_str)

        # Try all words eventually
        for freq_array in self.across_freq[i]:

            if pattern.match(freq_array):  # Check pattern
                if Configs.get_setting('TRY', 'try_show_words') == '1':
                    BasicLogger.log(str(i) + " across: freq_array " + freq_array)
                    print(str(i) + " across: freq_array " + freq_array)

                # Put word to row
                for char_index in range(len(freq_array)):
                    if matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                        matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq_array[char_index]

                temp_sum = 0
                for x in range(5):
                    for y in range(5):
                        if ord(matrix[x][y]) != 32 and ord(matrix[x][y]) != 36:
                            temp_sum += 1

                if self.max_sum < temp_sum:
                    self.max_sum = temp_sum
                    self.feasible_matrices = []

                if self.max_sum == temp_sum:
                    ck = True
                    for a in self.feasible_matrices:
                        if compare_matrix(5, a, matrix):
                            ck = False
                            break
                    if ck:
                        self.feasible_matrices.append(matrix)
                        if Configs.get_setting('TRY', 'try_show_feasible_matrix') == '1':
                            BasicLogger.log(str(i) + " across feasible " + str(temp_sum) + ":\n" + str(matrix))
                            print(i, "across feasible", temp_sum, ":\n", matrix)

                if temp_sum == self.puzzle.char_count:
                    if self.answer_limit < len(self.feasible_matrices):
                        return True

                if Configs.get_setting('TRY', 'try_show_matrices') == '1':
                    BasicLogger.log(str(i) + " across matrix:\n" + str(matrix))
                    print(i, "across matrix:\n", matrix)

                # Continue recursively
                sorted_c_arr = []
                for c in c_arr:
                    index = 0
                    for j in range(len(sorted_c_arr)):
                        if '_' in self.puzzle.downQuestions[c[1]]['clue']:
                            index = j
                            break
                    sorted_c_arr.insert(index, c)

                check = True
                for j in sorted_c_arr:

                    for k in range(5):
                        if ord(matrix[k][j[1]]) == 32:
                            check = False

                            if self.try_down(matrix.copy(), j[1]):
                                return True
                            elif self.try_across(matrix.copy(), k):
                                return True
                if check:
                    if self.answer_limit < len(self.feasible_matrices):
                        return True
        return False

    def try_down(self, matrix, j):

        c_arr = self.puzzle.get_coordinates(False, j)

        # Create pattern
        temp_str = r'\b'
        for c in c_arr:
            if ord(matrix[c[0]][j]) == 32 or ord(matrix[c[0]][j]) == 36:
                temp_str += r'[a-zA-Z]'
            else:
                temp_str += "[" + matrix[c[0]][c[1]] + "]"
        temp_str += r'\b'
        pattern = re.compile(temp_str)

        # Try all words eventually
        for freq_array in self.down_freq[j]:

            if pattern.match(freq_array):  # Check pattern

                if Configs.get_setting('TRY', 'try_show_words') == '1':
                    BasicLogger.log(str(j) + " down: freq_array " + freq_array)
                    print(j, "down: freq_array", freq_array)

                # Put word to col
                for char_index in range(len(freq_array)):
                    if matrix[c_arr[char_index][0]][c_arr[char_index][1]] != '$':
                        matrix[c_arr[char_index][0]][c_arr[char_index][1]] = freq_array[char_index]

                temp_sum = 0
                for x in range(5):
                    for y in range(5):
                        if ord(matrix[x][y]) != 32 and ord(matrix[x][y]) != 36:
                            temp_sum += 1

                if self.max_sum < temp_sum:
                    self.max_sum = temp_sum
                    self.feasible_matrices = []

                if self.max_sum == temp_sum:
                    ck = True
                    for a in self.feasible_matrices:
                        if compare_matrix(5, a, matrix):
                            ck = False
                            break
                    if ck:
                        self.feasible_matrices.append(matrix)
                        if Configs.get_setting('TRY', 'try_show_feasible_matrix') == '1':
                            BasicLogger.log(str(j) + " down feasible " + str(temp_sum) + ":\n" + str(matrix))
                            print(j, "down feasible", temp_sum, ":\n", matrix)

                if temp_sum == self.puzzle.char_count:
                    if self.answer_limit < len(self.feasible_matrices):
                        return True

                if Configs.get_setting('TRY', 'try_show_matrices') == '1':
                    BasicLogger.log(str(j) + " down: matrix\n" + str(matrix))
                    print(j, "down: matrix\n", matrix)

                # Continue recursively
                sorted_c_arr = []
                index = 0
                for c in c_arr:
                    j = 0
                    for j in range(len(sorted_c_arr)):
                        if '_' in self.puzzle.acrossQuestions[c[0]]['clue']:
                            index = j
                            break

                    sorted_c_arr.insert(index, c)

                check = True
                for i in sorted_c_arr:

                    for k in range(5):
                        if ord(matrix[i[0]][k]) == 32:
                            check = False

                            if self.try_across(matrix.copy(), i[0]):
                                return True
                            elif self.try_down(matrix.copy(), k):
                                return True
                if check:
                    if self.answer_limit < len(self.feasible_matrices):
                        return True
        return False

    def basic_search_thread(self, is_across, index):

        if Configs.get_setting('DEBUG', 'print_freq') == '1':
            BasicLogger.log("Thread started " + str(is_across) + " " + str(index))
            print("Thread started", is_across, index)

        if is_across:
            clue_text = self.puzzle.acrossQuestions[index]["clue"].strip()
        else:
            clue_text = self.puzzle.downQuestions[index]["clue"].strip()

        if '_' in clue_text:
            space_index = clue_text.index('_')

            clue_text = re.sub('"', '', clue_text)
            clue_text = re.sub('_', '', clue_text)
            temp = re.sub('\(.*?\)', '', clue_text)
            # clue_text = re.sub(r'\W+', ' ', clue_text)

            c_arr = self.puzzle.get_coordinates(is_across, index)
            pattern = r''
            for c in c_arr:
                if self.matrix[c[0]][c[1]] == chr(32) \
                        or self.matrix[c[0]][c[1]] == chr(36):
                    pattern += r'[a-zA-Z]'
                else:
                    pattern += "[" + self.matrix[c[0]][c[1]] + "]"

            header = temp[:space_index].strip()
            if 0 < len(header):
                header = header + " "
            footer = temp[space_index:].strip()
            if 0 < len(footer):
                footer = " " + footer

            pattern = r'\b' + header + "(" + pattern + ")" + footer + r'\b'
        else:
            c_arr = self.puzzle.get_coordinates(is_across, index)
            pattern = r'\b('
            for c in c_arr:
                if self.matrix[c[0]][c[1]] == chr(32) \
                        or self.matrix[c[0]][c[1]] == chr(36):
                    pattern += r'[a-zA-Z]'
                else:
                    pattern += "[" + self.matrix[c[0]][c[1]] + "]"
            pattern += r')[\.]?\b'
            # pattern = r'\b('
            # for i in range(char_count):
            #     pattern += r'[a-zA-Z]'
            # pattern += r')\b'
        s = Search(clue_text, pattern=pattern)

        for urls in s.googleSearch():
            try:
                s.searchPage(urls)
            except Exception as ssl:
                print(ssl)

        from collections import OrderedDict
        count = 1
        sumfreq = 0
        for key in s.word_freq:
            if 1 < s.word_freq[key]:
                count += 1
                sumfreq += s.word_freq[key]
        avg = sumfreq / count
        if is_across:
            # Sort
            for key_i, value_i in OrderedDict(
                    sorted(s.word_freq.items(), key=lambda t: t[1], reverse=True)).items():
                if 1 < value_i and avg <= value_i:
                    self.across_freq[index][key_i] = value_i
            # self.across_freq[index].update(temp_freq)
        else:
            # Sort
            for key_i, value_i in OrderedDict(
                    sorted(s.word_freq.items(), key=lambda t: t[1], reverse=True)).items():
                if 1 < value_i and avg <= value_i:
                    self.down_freq[index][key_i] = value_i
            # self.down_freq[index].update(temp_freq)

        if Configs.get_setting('DEBUG', 'print_freq') == '1':
            if is_across:
                temp_str = str(avg) + "across " + str(self.puzzle.acrossQuestions[index]['index']) + "result: \n" + str(
                    self.across_freq[index])
            else:
                temp_str = str(avg) + "down " + str(self.puzzle.downQuestions[index]['index']) + "result: \n" + str(
                    self.down_freq[index])

            BasicLogger.log(str(temp_str))
            print(str(temp_str))
