import numpy as np


class Puzzle:
    puzzleMatrix = np.full((5, 5), -1)
    answerMatrix = np.full((5, 5), -1)
    acrossQuestions = [dict() for x in range(5)]
    downQuestions = [dict() for x in range(5)]
    date = False

    def __init__(self, arr, across_questions, down_questions, date, answers):
        self.date = date
        self.char_count = 0
        for i in range(25):
            self.puzzleMatrix[int(i / 5)][int(i % 5)] = 32 if bool(arr[i]) else 36
            if bool(arr[i]):
                self.char_count += 1

        for i in range(5):
            j = 0
            while self.puzzleMatrix[i][j] == 36:
                j += 1
            across_questions[i]['place'] = i*5 + j, i
        temp_place = sorted(across_questions, key=lambda d: d['place'][0], reverse=False)

        self.acrossQuestions = sorted(across_questions, key=lambda d: d['display_index'], reverse=False)
        for i in range(5):
            self.acrossQuestions[i]['index'] = temp_place[i]['place'][1]
        self.acrossQuestions = sorted(self.acrossQuestions, key=lambda d: d['index'], reverse=False)

        for j in range(5):
            i = 0
            while self.puzzleMatrix[i][j] == 36:
                i += 1
            down_questions[j]['place'] = i*5 + j, j
        temp_place = sorted(down_questions, key=lambda d: d['place'][0], reverse=False)
        self.downQuestions = sorted(down_questions, key=lambda d: d['display_index'], reverse=False)
        for i in range(5):
            self.downQuestions[i]['index'] = temp_place[i]['place'][1]
        self.downQuestions = sorted(self.downQuestions, key=lambda d: d['index'], reverse=False)

        self.answerMatrix = answers

    def get_coordinates(self, is_across, i):
        result = []
        for j in range(5):
            if is_across:
                if self.puzzleMatrix[i][j] == 32:
                    result.append((i, j))
            else:
                if self.puzzleMatrix[j][i] == 32:
                    result.append((j, i))
        return result

    def get_across_char_count(self, i):
        result = 0
        for j in range(5):
            if self.puzzleMatrix[i][j] == 32:
                result += 1
        return result

    def get_down_char_count(self, j):
        result = 0
        for i in range(5):
            if self.puzzleMatrix[i][j] == 32:
                result += 1
        return result

    def save(self, filename):
        file = open(filename, "w")

        temp_str = ""
        for i in range(5):
            for j in range(5):
                temp_str += str(self.puzzleMatrix[i][j]) + " "
            temp_str += "\n"
        file.write(str(temp_str))

        temp_str = ""
        for i in range(5):
            temp_str += str(self.acrossQuestions[i]['index']) + " "
            temp_str += str(self.acrossQuestions[i]['display_index']) + " "
            temp_str += self.acrossQuestions[i]['clue'] + " "
            temp_str += "\n"
        file.write(temp_str)

        temp_str = ""
        for i in range(5):
            temp_str += str(self.downQuestions[i]['index']) + " "
            temp_str += str(self.downQuestions[i]['display_index']) + " "
            temp_str += self.downQuestions[i]['clue'] + " "
            temp_str += "\n"
        file.write(temp_str)

        file.write(self.date+"\n")

        temp_str = ""
        for i in range(5):
            for j in range(5):
                temp_str += str(self.answerMatrix[i][j]) + " "
            temp_str += "\n"
        file.write(str(temp_str))

        file.close()

    def print(self):
        print("Across:\n")
        for i in range(5):
            print('{0}. {1}\n'.format(self.acrossQuestions[i]['display_index'], self.acrossQuestions[i]['clue']))

        print("\nDown:\n")
        for i in range(5):
            print('{0}. {1}\n'.format(self.downQuestions[i]['display_index'], self.downQuestions[i]['clue']))

        print("\nLayout:\n")

        temp_str = ""
        for i in range(5):
            temp_str += "|"
            for j in range(5):
                temp_str += chr(self.puzzleMatrix[i][j]) + "|"
            temp_str += "\n"
        print(temp_str)
