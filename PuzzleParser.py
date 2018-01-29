import numpy
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from Puzzle import Puzzle


def fetch_data(target_page):
    #driver = webdriver.PhantomJS("phantomjs.exe")
    driver = webdriver.Chrome("chromedriver.exe")

    driver.get(target_page)

    # Fetching data from clues

    # Date
    date = driver.find_element_by_xpath\
            ('/html/body/div[1]/div/div[1]/div[3]/div/main/div[2]/header/div/div/div/div[1]').text

    # Across clues
    across_clue_list = driver.find_element_by_xpath \
        ('//*[@id="root"]/div/div/div[3]/div/main/div[2]/div/article/section[2]/div[1]/ol').text.rsplit("\n")

    acc_dict_array = [dict() for i in range(5)]
    for i in range(5):
        acc_dict_array[i] = {'index': i, 'clue': across_clue_list[2 * i + 1],
                             'display_index': across_clue_list[2 * i]}

    # Down clues
    down_clue_list = driver.find_element_by_xpath \
        ('//*[@id="root"]/div/div/div[3]/div/main/div[2]/div/article/section[2]/div[2]/ol').text.rsplit("\n")

    down_dict_array = [dict() for i in range(5)]
    for i in range(5):
        down_dict_array[i] = {'index': i, 'clue': down_clue_list[2 * i + 1], 'display_index': down_clue_list[2 * i]}

    # Fetching data from puzzle
    soup = BeautifulSoup(requests.get(target_page).text)
    layout = numpy.zeros(25)
    i = 0
    for rect in soup.find_all("rect"):
        if i < 25:
            layout[i] = bool(rect['fill'].lower() != "black")
        i += 1

    # Getting the solutions

    # Click to ready button
    ready_button = driver.find_element_by_xpath(
        '//*[@id="root"]/div/div/div[3]/div/main/div[2]/div/div[2]/div[2]/article/div[2]/button/div')
    driver.execute_script("arguments[0].scrollIntoView();", ready_button)
    ready_button.click()

    # Find the reveal button and click
    reveal_button = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[3]/div/main/div[2]/div/div/ul/div[1]/li[2]/button')
    driver.execute_script("arguments[0].scrollIntoView();", reveal_button)
    reveal_button.click()

    # Click to solve puzzle button
    solve_puzzle_button = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[3]/div/main/div[2]/div/div/ul/div[1]/li[2]/ul/li[3]/a')
    driver.execute_script("arguments[0].scrollIntoView();", solve_puzzle_button)
    solve_puzzle_button.click()

    # Confirm button
    confirm_button = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[2]/article/div[2]/button[2]')
    driver.execute_script("arguments[0].scrollIntoView();", confirm_button)
    confirm_button.click()

    # Exit button
    exit_button = driver.find_element_by_xpath('/ html / body / div[1] / div / div[2] / div[2] / div / a')
    driver.execute_script("arguments[0].scrollIntoView();", exit_button)
    exit_button.click()
    time.sleep(5)

    # # Fetching data from puzzle
    answers = []
    for item in driver.find_elements_by_xpath(
            "//*[name()='svg']//*[name()='g' and @data-group='cells']//*[name()='g']//*[name()='text' and @text-anchor='middle']"):
        answers.append(item.text)

    answer_matrix = numpy.full((5, 5), -1)
    j = 0
    for i in range(25):
        if bool(layout[i]):
            answer_matrix[int(i / 5)][int(i % 5)] = ord(answers[j])
            j += 1
        else:
            answer_matrix[int(i / 5)][int(i % 5)] = 36 # $ sign signals black block

    driver.close()
    return Puzzle(layout, acc_dict_array, down_dict_array, date, answer_matrix)


def load_puzzle(filename):
    with open(filename, "rb") as fp:
        layout = numpy.zeros(25)
        acc_dict_array = [dict() for i in range(5)]
        down_dict_array = [dict() for i in range(5)]
        answer_matrix = numpy.full((5, 5), -1)

        i = 0
        for line in fp:
            temp_str = line.decode()
            if i < 5:  # line [0, 5)
                temp_list = temp_str.strip('\r\n').split(' ', 4)
                layout[i * 5] = int(temp_list[0]) != 36
                layout[i * 5 + 1] = int(temp_list[1]) != 36
                layout[i * 5 + 2] = int(temp_list[2]) != 36
                layout[i * 5 + 3] = int(temp_list[3]) != 36
                layout[i * 5 + 4] = int(temp_list[4]) != 36

            # b'{:d} {:d} {:D} \r\n'
            elif i < 10:  # line [5, 10)
                temp_list = temp_str.strip('\r\n').split(' ', 2)
                acc_dict_array[i-5] = {'index': int(temp_list[0]), 'display_index': int(temp_list[1]), 'clue': temp_list[2]}

            # b'{:d} {:d} {:D} \r\n'
            elif i < 15:  # line [10, 15)
                temp_list = temp_str.strip('\r\n').split(' ', 2)
                down_dict_array[i-15] = {'index': int(temp_list[0]), 'display_index': int(temp_list[1]), 'clue': temp_list[2]}
            elif i < 16:  # line [15, 16)
                date = temp_str.strip("\n")
            elif i < 21:  # line [16, 21)
                temp_list = temp_str.strip('\r\n').split(' ', 4)
                answer_matrix[(i-16)][0] = int(temp_list[0])
                answer_matrix[(i-16)][1] = int(temp_list[1])
                answer_matrix[(i-16)][2] = int(temp_list[2])
                answer_matrix[(i-16)][3] = int(temp_list[3])
                answer_matrix[(i-16)][4] = int(temp_list[4])
            i += 1

        return Puzzle(layout, acc_dict_array, down_dict_array, date, answer_matrix)
