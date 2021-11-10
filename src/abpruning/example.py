import random
from pisqpipe import DEBUG_EVAL, DEBUG
from util import *

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
begin = 1

def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")

def brain_restart():
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

def Isterminate(board):#判断场上是否胜负已分
	height, width = pp.height, pp.width
	for row in board:
		work_str = "".join(map(str, row))
		if "11111" in work_str:
			return True

	for idx in range(width):
		col = [b[idx] for b in board]
		work_str = "".join(map(str, col))
		if "11111" in work_str:
			return True

	for dist in range(-width + 1, height):
		row, col = (0, -dist) if dist < 0 else (dist, 0)
		diag = [board[i][j] for i in range(row, height) for j in range(col, width) if i - j == dist]
		work_str = "".join(map(str, diag))
		if "11111" in work_str:
			return True

	for dist in range(0, width + height - 1):
		row, col = (dist, 0) if dist < height else (height - 1, dist - height + 1)
		diag = [board[i][j] for i in range(row, -1, -1) for j in range(col, width) if i + j == dist]
		work_str = "".join(map(str, diag))
		if "11111" in work_str:
			return True

	return False

def abpSearch(board,alpha,beta,depth,maxdep):
	action = [-1,-1]
	if depth%2 == maxdep%2:##max节点，我方行动
		# if Isterminate(board):
		# 	return float("+inf"), [-1, -1]
		dotspace = evaluation(board)
		if depth == 0:
			return dotspace[0].value, dotspace[0].action
		if dotspace[0].value == float("+inf"):
			return dotspace[0].value, dotspace[0].action
		for i in range(len(dotspace)):#对每个子空间落子
			x = dotspace[i].action[0]
			y = dotspace[i].action[1]
			board[x][y] = 1
			move_v, move_action = abpSearch(board,alpha,beta,depth-1,maxdep)
			board[x][y] = 0
			if move_v > alpha:
				action = [x, y]
				alpha = move_v
			if alpha >= beta:
				return alpha, action
		return alpha, action
	else: #min节点,敌方行动
		boardcopy = [[board[x][y] for y in range(pp.width)] for x in range(pp.height)]
		for x in range(pp.width):#翻转棋盘，黑白子对换，才能用evaluation函数找白方较优势的落子点
			for y in range(pp.height):
				boardcopy[x][y] = (3 - boardcopy[x][y]) % 3
		# if Isterminate(board):
		# 	return float("-inf"), [-1, -1]
		dotspace = evaluation(boardcopy)
		if depth == 0:
			return -dotspace[0].value, dotspace[0].action
		if dotspace[0].value == float("+inf"):
			return -dotspace[0].value, dotspace[0].action
		for i in range(len(dotspace)):#对每个子空间落子
			x = dotspace[i].action[0]
			y = dotspace[i].action[1]
			board[x][y] = 2
			move_v, move_action = abpSearch(board,alpha,beta,depth-1,maxdep)
			board[x][y] = 0
			if move_v < beta:
				action = [x, y]
				beta = move_v
			if alpha >= beta:
				return beta, action
		return beta, action


def brain_turn():
	if pp.terminateAI:
		return
	i = 0
	global begin
	if begin == 1:
		for k in range(pp.width):
			for j in range(pp.height):
				if not isFree(k,j):
					begin = 0
					break
			if begin == 0:
				break

	while True:
		if begin == 1:#此时场上没有棋子，下天元
			x = pp.width//2
			y = pp.height//2
			begin = 0
		else:
			max_depth = 1
			getboard = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
			_, move = abpSearch(getboard,float("-Inf"),float("Inf"),max_depth,max_depth)
			flag = 0
			if move == [-1, -1]:
				for i in range(pp.height):
					for j in range(pp.width):
						if board[i][j] == 0:
							x = i
							y = j
							flag = 1
							break
					if flag == 1:
						break
			else:
				x = move[0]
				y = move[1]
		i += 1
		if pp.terminateAI:
			return
		if isFree(x,y):
			break
	if i > 1:
		pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
	pp.do_mymove(x, y)

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################

# define a file for logging ...
# DEBUG_LOGFILE = "D:/John Yao/University/Homework/term5/人工智能/projects/final_project/src/abpruning/pbrain-abpruning.log"
# ...and clear it initially
# with open(DEBUG_LOGFILE,"w") as f:
# 	pass

# define a function for writing messages to the file
# def logDebug(msg):
# 	with open(DEBUG_LOGFILE,"a") as f:
# 		f.write(msg+"\n")
# 		f.flush()

# define a function to get exception traceback
# def logTraceBack():
# 	import traceback
# 	with open(DEBUG_LOGFILE,"a") as f:
# 		traceback.print_exc(file=f)
# 		f.flush()
# 	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
# def brain_turn():
# 	logDebug("some message 1")
# 	try:
# 		logDebug("some message 2")
# 		1. / 0. # some code raising an exception
# 		logDebug("some message 3") # not logged, as it is after error
# 	except:
# 		logTraceBack()

######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()
