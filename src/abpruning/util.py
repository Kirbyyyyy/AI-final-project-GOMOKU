import pisqpipe as pp
import re
def special_pattern(board, color):


def evaluation(board):
    """
    evaluate the situation on the board
    Input:
        board
    Output:
        the score for current condition
    """
    score_map = {"WIN": 100000,
                 "F4" : 50000,
                 "B4" : 400,
                 "F3" : 400,
                 "B3" : 20,
                 "F2" : 20,
                 "B2" : 1,
                 "F1" : 1
                 }
    score = 0

    for pattern, num in special_pattern(board, 1).items():
        score += score_map[pattern] * num
    for pattern, num in special_pattern(board, 2).items():
        if pattern in ['F4', 'WIN']:
            score = score - 10 * score_map[pattern] * num
        else:
            score = score - score_map[pattern] * num

    return score