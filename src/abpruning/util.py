import pisqpipe as pp
import re
from collections import Counter
import copy


class dot:
    def __init__(self, value=None, action=None, color=None):
        self.value = value  # 估计出的值
        self.action = action  # 位置


def special_pattern(board):
    """
    Find the number of special pattern exists on the board
    INPUT:
        board, color
    OUTPUT:
        counter for each special pattern
    """
    pattern_dict = {("WIN", (), ()): "11111",
                    ("F4", (0, 5), ()): "011110",
                    ("B4", (0), (5)): "011112",
                    ("B4", (5), (0)): "211110",
                    ("B4", (0), ()): "01111$",
                    ("B4", (4), ()): "^11110",
                    ("B4", (0, 2, 6), ()): "0101110",
                    ("B4", (0, 3, 6), ()): "0110110",
                    ("B4", (0, 4, 6), ()): "0111010",
                    ("F3", (0, 4), ()): "01110",
                    ("F3", (0, 2, 5), ()): "010110",
                    ("F3", (0, 3, 5), ()): "011010",
                    ("B3", (0, 1), (5)): "001112",
                    ("B3", (0, 1), ()): "00111$",
                    ("B3", (4, 5), (0)): "211100",
                    ("B3", (4, 5), ()): "^11100",
                    ("B3", (0, 2), (5)): "010112",
                    ("B3", (0, 2), ()): "01011$",
                    ("B3", (3, 5), (0)): "211010",
                    ("B3", (3, 5), ()): "^110101",
                    ("B3", (0, 3), (5)): "011012",
                    ("B3", (0, 3), ()): "01101$",
                    ("B3", (2, 5), (0)): "210110",
                    ("B3", (2, 5), ()): "^10110",
                    ("B3", (1, 2), ()): "10011",
                    ("B3", (2, 3), ()): "11001",
                    ("B3", (1, 3), ()): "10101",
                    ("B3", (1, 5), (0, 6)): "2011102",
                    ("B3", (1, 5), (0)): "201110$",
                    ("B3", (1, 5), (6)): "^011102",
                    ("F2", (0, 3, 4), ()): "01100",
                    ("F2", (0, 1, 4), ()): "00110",
                    ("F2", (0, 2, 4), ()): "01010",
                    ("F2", (0, 2, 3, 5), ()): "010010",
                    ("B2", (0, 1, 2), (5)): "000112",
                    ("B2", (0, 1, 2), ()): "00011$",
                    ("B2", (3, 4, 5), (0)): "211000",
                    ("B2", (3, 4, 5), ()): "^11000",
                    ("B2", (0, 1, 3), (5)): "001012",
                    ("B2", (0, 1, 3), ()): "00101$",
                    ("B2", (2, 4, 5), (0)): "210100",
                    ("B2", (2, 4, 5), ()): "^10100",
                    ("B2", (0, 2, 3), (5)): "010012",
                    ("B2", (0, 2, 3), ()): "01001$",
                    ("B2", (2, 3, 5), (0)): "210010",
                    ("B2", (2, 3, 5), ()): "^10010",
                    ("B2", (1, 2, 3), ()): "10001",
                    ("B2", (1, 3, 5), (0, 6)): "2010102",
                    ("B2", (1, 3, 5), (0)): "201010$",
                    ("B2", (1, 3, 5), (6)): "^010102",
                    ("B2", (1, 4, 5), (0, 6)): "2011002",
                    ("B2", (1, 4, 5), (0)): "201100$",
                    ("B2", (1, 4, 5), (6)): "^011002",
                    ("B2", (1, 2, 5), (0, 6)): "2001102",
                    ("B2", (1, 2, 5), (0)): "200110$",
                    ("B2", (1, 2, 5), (6)): "^001102",
                    }

    height, width = pp.height, pp.width
    pattern_counter = Counter()

    for idx, row in enumerate(board):
        work_str = "".join(map(str, row))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], work_str))

    for idx in range(width):
        col = [b[idx] for b in board]
        work_str = "".join(map(str, col))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], work_str))

    for dist in range(-width + 1, height):
        row, col = (0, -dist) if dist < 0 else (dist, 0)
        diag = [board[i][j] for i in range(row, height) for j in range(col, width) if i - j == dist]
        work_str = "".join(map(str, diag))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], work_str))

    for dist in range(0, width + height - 1):
        row, col = (dist, 0) if dist < height else (height - 1, dist - height + 1)
        diag = [board[i][j] for i in range(row, -1, -1) for j in range(col, width) if i + j == dist]
        work_str = "".join(map(str, diag))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], work_str))

    return pattern_counter


def scoring(board):
    """
    scoring the situation on the board
    Input:
        board
    Output:
        the score for current condition
    """
    score_map = {"WIN": 200000,
                 "F4": 10000,
                 "B4": 1000,
                 "F3": 200,
                 "B3": 50,
                 "F2": 5,
                 "B2": 3
                 }
    score = 0
    pattern1 = special_pattern(board)
    boardcopy = [[board[x][y] for y in range(pp.width)] for x in range(pp.height)]
    for i in range(pp.height):
        for j in range(pp.width):
            boardcopy[i][j] = (3 - boardcopy[i][j]) % 3
    pattern2 = special_pattern(boardcopy)

    if pattern1['WIN'] != 0:
        return float("+inf")
    for pattern, num in pattern1.items():
        score = score + score_map[pattern] * num

    if pattern2['WIN'] != 0:
        return float("-inf")
    for pattern, num in pattern2.items():
        if pattern in ['F4', 'B4', 'F3']:
            score = score - 10 * score_map[pattern] * num
        else:
            score = score - score_map[pattern] * num
    return score


def evaluation(board):
    """
    Evaluate the potential actions nearby
    INPUT:
        Board
    OUTPUT:
        list of actions with descending order w.r.t score
    """
    expand_num = 6
    height, width = pp.height, pp.width
    action_set = set()
    for i in range(height):
        if sum(board[i]) != 0:
            for j in range(width):
                if board[i][j] != 0:
                    for x in range(max(0, i - 2), min(width, i + 3)):
                        for y in range(max(0, j - 2), min(height, j + 3)):
                            if board[x][y] == 0:
                                action_set.add((x, y))
    dot_list = []
    for action in action_set:
        board[action[0]][action[1]] = 1
        new_dot = dot(scoring(board), action)
        board[action[0]][action[1]] = 0
        dot_list.append(new_dot)
    dot_list.sort(key=lambda d: d.value, reverse=True)
    if len(dot_list) < expand_num:
        return dot_list
    else:
        return dot_list[0:expand_num]
