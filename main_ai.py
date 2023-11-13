import numpy as np
import pygame
import sys
import math
import tkinter as tk # 표준 GUI 라이브러리

BROWN = (204, 153, 51)
DARKGREY = (70, 70, 70)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 51, 204)
BLUE = (0, 50, 255)
RED=(255,0,0)
YELLOW = (255, 255, 0)

no_of_rows = 19
no_of_columns = 19

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4
C6 = 6


def board_create():
    board = np.zeros((no_of_rows, no_of_columns))
    return board

def yellow_board_create():
    yellow_board = np.zeros((no_of_rows, no_of_columns))
    return yellow_board

def piece_drop(board, row, col, piece):
    board[row][col] = piece

def recent_piece_drop(yellow_board, row, col, piece):
    yellow_board[row][col] = piece


def is_valid_location(board, row, col):
    return board[row][col] == 0



def print_board(board):
    print(np.flip(board, 0))


# connect 6 완성되었을 때
def winner_check(board, piece):
    """승자 체크"""
    for slot in ind_list:
        a = np.where(board == 1, 0, board)
        a = np.where(board == 2, 1, a)
        a = np.where(board == 3, 0, a)
        b = np.where(board == 2, 0, board)
        b = np.where(board == 3, 0, b)
        check = sum(a[slot])
        if check >= C6:
            return True
        check = sum(b[slot])
        if check >= C6:
            return True
    return False

def minimax(board, depth):

    board_ai = np.where(board == 1, 0, board)
    board_ai = np.where(board == 2, 1, board_ai)
    board_player = np.where(board == 2, 0, board)

    move = []
    score = []
    for k in range(6):
        board_ai = np.where(board == 1, 0, board)
        board_ai = np.where(board == 2, 1, board_ai)
        board_player = np.where(board == 2, 0, board)
        for i in range(depth):
            if i % 2 == 0:

                bestmoves, scores = check_best_moves(board_ai, board_player)
                moves = [x for y, x in sorted(zip(scores, bestmoves), reverse=True)]
                s = [y for y, x in sorted(zip(scores, bestmoves), reverse=True)]
                if i == 0:
                    move.append(bestmoves[k])
                piece_drop(board_ai, moves[0][0][0], moves[0][0][1], 1)
                piece_drop(board_ai, moves[0][1][0], moves[0][1][1], 1)
            else:
                #  min
                bestmoves, scores = check_best_moves(board_player, board_ai)
                moves = [x for y, x in sorted(zip(scores, bestmoves), reverse=True)]
                s = [y for y, x in sorted(zip(scores, bestmoves), reverse=True)]
                piece_drop(board_player, moves[0][0][0], moves[0][0][1], 1)
                piece_drop(board_player, moves[0][1][0], moves[0][1][1], 1)
        score.append(s[0])

    maxValue = max(score)
    for k in range (6):
        if score[k] == maxValue:
            return move[k]

def check_best_moves(ai, player):
    """최적화된 이동 체크"""
    moves = []
    best1 = stone_1(ai, player)
    for i in range(10): #eval_pri -> 우리가 설정하는 값
        best2 = stone_2(ai, player, best1[i])
        for j in range(10):
            moves.append((best1[i], best2[j]))
    bestmoves, scores = aposteriori(ai, player, moves)
    return bestmoves, scores

def stone_1(ai, player):
    """착수할 첫번째 돌의 위치 계산"""
    B_M, B_O = ai_calculate(ai, player, 4)
    ai_pri_1 = np.array([2, 6, 0, 1000]).reshape(4,1,1)
    player_pri_1 = np.array([1, 4, 10, 100]).reshape(4,1,1)
    B_eval = sum(B_M*ai_pri_1 + B_O*player_pri_1)
    bestmoves = check_top_n(B_eval, 10)
    return bestmoves

def stone_2(ai, player, move1):
    """착수할 두번째 돌의 위치 계산"""
    board_ai_virt = np.zeros((no_of_rows, no_of_columns)) + ai
    board_ai_virt[move1] = 1
    B_M, B_O = ai_calculate(board_ai_virt, player, 5)
    ai_pri_2 = np.array([2, 1, 6, 0, 1000]).reshape(5,1,1)
    player_pri_2 = np.array([1, 4, 6, 100, 100]).reshape(5,1,1)
    B_eval = sum(B_M*ai_pri_2 + B_O*player_pri_2)
    bestmoves = check_top_n(B_eval, 10)
    return bestmoves

def ai_calculate(ai, player, n_max):
    """evaluate board by checking the number of stones adjacent to each
    point of the board. outpiut are 5 matrices"""
    B_M = np.zeros((n_max, no_of_rows, no_of_columns))
    B_O = np.zeros((n_max, no_of_rows, no_of_columns))
    for list in ind_list_collect:
        B_M_loop = np.zeros((n_max, no_of_rows, no_of_columns))
        B_O_loop = np.zeros((n_max, no_of_rows, no_of_columns))
        for slot in list:
            check_me = min(int(sum(ai[slot])), n_max) # 그러면 n_max가 4일 때 check_me는 0, 1, 2, 3, 4 중 하나
            check_op = min(int(sum(player[slot])), n_max)
            if check_me>=1 and check_op==0:
                B_M_loop[check_me-1,:,:][slot] = 1
            elif check_op>=1 and check_me==0:
                B_O_loop[check_op-1,:,:][slot] = 1 #B_O_loop[check_op-1,:,:][slot]
        B_M += B_M_loop
        B_O += B_O_loop
    B_M = stone_free(B_M, ai, player)
    B_O = stone_free(B_O, ai, player)
    return B_M, B_O

def ai_evaluate(ai, player):
    """evaluate board by counting total number of slots with numbers up to
    n_max. output are n_max numbers"""
    B_M = np.zeros((6))
    B_O = np.zeros((6))
    for list in ind_list_collect:
        for slot in list:
            check_me = int(sum(ai[slot]))
            check_op = int(sum(player[slot]))
            if check_me>=1 and check_me<=6 and check_op==0:
                B_M[check_me-1] += 1
            elif check_op>=1 and check_op<=6 and check_me==0:
                B_O[check_op-1] += 1
    return B_M, B_O

def stone_free(B, ai, player):
    # 빈 판에 현재 놓여져 있는 돌 착수
    board_free = np.remainder(ai + player + np.ones((no_of_rows, no_of_columns)), 2)
    B *= board_free
    return B

def aposteriori(ai, player, moves):
    """두 돌 착수 후에 보드 계산"""
    # only unique moves
    ii = 0
    while ii<len(moves):
        moves[ii] = (moves[ii][1],moves[ii][0])
        moves = list(set(moves))
        ii += 1
    # evaluate moves
    checklist = []
    scores = []
    ai_pos = [0, 3/4, 8/5, 13/3, 12/2, 10000]
    player_pos = [1/5, 1, 12/4, 1000, 1000, 1000]
    for checkmove in moves:
        board_ai_virt = np.zeros((no_of_rows, no_of_columns)) + ai
        board_ai_virt[checkmove[0]] = 1
        board_ai_virt[checkmove[1]] = 1
        B_M, B_O = ai_evaluate(board_ai_virt, player)
        score = sum(B_M*ai_pos-B_O*player_pos)
        checklist.append(checkmove)
        scores.append(-score)
    if len(checklist) > 0:
            moves = checklist
            moves = [x for y, x in sorted(zip(scores,checklist))]
            scores = sorted(scores)
    return moves, scores


def check_top_n(array, n):
    inds = np.argpartition(array, array.size-n, axis=None)[-n:]
    width = array.shape[1]
    return [divmod(i, width) for i in inds]

def draw_board(board):
    for c in range(no_of_columns):
        for r in range(no_of_rows):
            pygame.draw.line(game_screen, BLACK, (int((c+0.5)*SQUARESIZE), r*SQUARESIZE), (int((c+0.5)*SQUARESIZE), (r+1)*SQUARESIZE) ,1)
            pygame.draw.line(game_screen, BLACK, (c*SQUARESIZE, int((r+0.5)*SQUARESIZE)), ((c+1)*SQUARESIZE, int((r+0.5)*SQUARESIZE)) ,1)
            if c in [3,9, 15 ]:
                if r in [3,9,15]:
                    pygame.draw.circle(game_screen, BLACK, (int((c+0.5)*SQUARESIZE), int((r+0.5)*SQUARESIZE)), int(SQUARESIZE/(5)))
    for c in range(no_of_columns):
        for r in range(no_of_rows):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(game_screen, PINK, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS) # Player

            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(game_screen, BLUE, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS) # AI

            elif board[r][c] == 3 :
                pygame.draw.circle(game_screen, RED, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS) # 장애물

    print("turn: ", turn)
    pygame.display.update()

# 최근에 놓은 AI 돌 표시
def draw_recent(yellow_board, who):

    for c in range(no_of_columns):
        # print()
        for r in range(no_of_rows):
            # print(yellow_board[c][r], end=' ')
            if yellow_board[r][c] == 2:
                pygame.draw.circle(game_screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), SQUARESIZE/5) # 현재 돌 표시

    pygame.display.update()

###-----------------------------------------------------------------------------

# 게임판 2차원 배열
board = board_create()

# 최근 돌 표시를 위한 배열
yellow_board = yellow_board_create()

# 이길 수 있는 경우의 수 List
ind_list_diag1 = []  # list of diagonal slots (first)
ind_list_diag2 = []  # list of diagonal slots (second)
ind_list_hor = []    # list of horizontal slots
ind_list_ver = []    # list of vertical slots
ind_list = []        # list of all slot
ind_list_collect = []

indices_row, indices_col= np.indices((no_of_rows, no_of_columns))
for ii in range(no_of_rows):
    for jj in range(no_of_columns - C6 + 1):
        a = jj
        b = jj + C6
        #horizontals
        rows=indices_row[ii,a:b]
        cols=indices_col[ii,a:b]
        ind_list.append((rows,cols))
        ind_list_hor.append((rows,cols))
        #verticals
        rows=indices_row[a:b,ii]
        cols=indices_col[a:b,ii]
        ind_list.append((rows,cols))
        ind_list_ver.append((rows,cols))
#diagonals
for ii in range(-(no_of_rows-C6),no_of_columns-C6+1):
    for jj in range(len(indices_row.diagonal(ii))-C6+1):
        a = jj
        b = jj + C6
        rows=indices_row.diagonal(ii)[a:b]
        cols=indices_col.diagonal(ii)[a:b]
        ind_list.append((rows,cols))
        ind_list_diag1.append((rows,cols))
        rows=indices_row[::-1,:].diagonal(ii)[a:b]
        cols=indices_col[::-1,:].diagonal(ii)[a:b]
        ind_list.append((rows,cols))
        ind_list_diag2.append((rows,cols))

ind_list_collect = [ind_list_hor, ind_list_ver, ind_list_diag1, ind_list_diag2]


# 메뉴창과 바둑창 설정
pygame.init()
main_screen = pygame.display.set_mode((500,400))
pygame.display.set_caption('CONNECT 6 :: MAIN')
myfont = pygame.font.Font(None, 20)
myfont2 = pygame.font.Font(None, 30)
p1_text = myfont.render("AI First", True, BLACK) #pygame.font.Font(None, 36)
p2_text = myfont.render("Human First", True, BLACK)
obstacle = myfont.render("Number of obstacles", True, BLACK)
ob0_text = myfont.render("0", True, BLACK)
ob1_text = myfont.render("1", True, BLACK)
ob2_text = myfont.render("2", True, BLACK)
ob3_text = myfont.render("3", True, BLACK)
ob4_text = myfont.render("4", True, BLACK)
start_text = myfont2.render("start", True, BLACK)

start_button = pygame.Rect(200, 300, 100, 50)
player1_button = (200,50)
player2_button = (300,50)
ob0_button = (300, 130)
ob1_button = (300, 160)
ob2_button = (300, 190)
ob3_button = (300, 220)
ob4_button = (300, 250)
button_radius = 20
selected_button = AI
selected_ob = 0
show_main_screen = True
turn = 0
ob_cnt=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 마우스 왼쪽 버튼을 클릭했을 때
                if start_button.collidepoint(event.pos):  # 버튼이 클릭되었을 때, 초기 화면을 숨기고 새로운 창을 열어 게임 진행
                    show_main_screen = False
                    pygame.quit()
                d1 = pygame.math.Vector2(event.pos[0] - player1_button[0], event.pos[1] - player1_button[1]).length()
                d2 = pygame.math.Vector2(event.pos[0] - player2_button[0], event.pos[1] - player2_button[1]).length()


                if d1 <= button_radius:
                    selected_button = PLAYER
                elif d2 <= button_radius:
                    selected_button = AI
                ob0 = pygame.math.Vector2(event.pos[0] - ob0_button[0], event.pos[1] - ob0_button[1]).length()
                ob1 = pygame.math.Vector2(event.pos[0] - ob1_button[0], event.pos[1] - ob1_button[1]).length()
                ob2 = pygame.math.Vector2(event.pos[0] - ob2_button[0], event.pos[1] - ob2_button[1]).length()
                ob3 = pygame.math.Vector2(event.pos[0] - ob3_button[0], event.pos[1] - ob3_button[1]).length()
                ob4 = pygame.math.Vector2(event.pos[0] - ob4_button[0], event.pos[1] - ob4_button[1]).length()
                if ob0 <= button_radius/2:
                    selected_ob = 0
                elif ob1 <= button_radius/2:
                    selected_ob = 1
                elif ob2 <= button_radius/2:
                    selected_ob = 2
                elif ob3 <= button_radius/2:
                    selected_ob = 3
                elif ob4 <= button_radius/2:
                    selected_ob = 4
        if show_main_screen:
            main_screen.fill(WHITE)  # 흰색으로 화면 채우기
            main_screen.blit(p1_text, (170, 75))
            main_screen.blit(p2_text, (270, 75))
            main_screen.blit(obstacle, (100, 125))
            main_screen.blit(ob0_text, (270, 125))
            main_screen.blit(ob1_text, (270, 155))
            main_screen.blit(ob2_text, (270, 185))
            main_screen.blit(ob3_text, (270, 215))
            main_screen.blit(ob4_text, (270, 245))
            main_screen.blit(start_text, (230, 360))


            pygame.draw.rect(main_screen, RED, start_button)  # 시작 버튼 그리기
            pygame.draw.circle(main_screen, BLACK, player1_button, button_radius, 2)
            pygame.draw.circle(main_screen, BLACK, player2_button, button_radius, 2)
            pygame.draw.circle(main_screen, BLACK, ob0_button, button_radius/2, 2)
            pygame.draw.circle(main_screen, BLACK, ob1_button, button_radius/2, 2)
            pygame.draw.circle(main_screen, BLACK, ob2_button, button_radius/2, 2)
            pygame.draw.circle(main_screen, BLACK, ob3_button, button_radius/2, 2)
            pygame.draw.circle(main_screen, BLACK, ob4_button, button_radius/2, 2)

            if selected_button == AI:
                pygame.draw.circle(main_screen, PINK, player2_button, button_radius-2)
                turn = -1
            elif selected_button == PLAYER:
                pygame.draw.circle(main_screen, PINK, player1_button, button_radius-2)
                turn =-2
            if selected_ob == 0:
                pygame.draw.circle(main_screen, RED, ob0_button, button_radius/2-2)
            elif selected_ob == 1:
                pygame.draw.circle(main_screen, RED, ob1_button, button_radius/2-2)
            elif selected_ob == 2:
                pygame.draw.circle(main_screen, RED, ob2_button, button_radius/2-2)
            elif selected_ob == 3:
                pygame.draw.circle(main_screen, RED, ob3_button, button_radius/2-2)
            elif selected_ob == 4:
                pygame.draw.circle(main_screen, RED, ob4_button, button_radius/2-2)
            pygame.display.flip()
        else:
            pygame.init()
            SQUARESIZE = 50
            width = no_of_columns * SQUARESIZE
            height = no_of_rows * SQUARESIZE
            size = (width, height)
            RADIUS = int(SQUARESIZE / 2 - 5)
            myfont = pygame.font.SysFont("monospace", 75)
            game_screen = pygame.display.set_mode(size)
            game_screen.fill(BROWN)
            pygame.display.set_caption('CONNECT 6 :: GAME')
            game_screen.fill(BROWN)
            draw_board(board)
            pygame.display.update()


            game_over = False
            player_count = 0

            while not game_over:
                if ob_cnt>=selected_ob :
                    break

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        sys.exit()

                    pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        obx=event.pos[0]
                        oby=event.pos[1]
                        col = int(math.floor(obx / SQUARESIZE))
                        row = int(math.floor(oby / SQUARESIZE))

                        if is_valid_location(board, row, col):
                            piece_drop(board, row, col, 3)
                            draw_board(board)
                            ob_cnt+=1

            while not game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()

                    pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        if turn % 2 == 1:
                            posx = event.pos[0]
                            posy = event.pos[1]
                            col = int(math.floor(posx / SQUARESIZE))
                            row = int(math.floor(posy / SQUARESIZE))

                            if is_valid_location(board, row, col):
                                piece_drop(board, row, col, PLAYER_PIECE)
                                px = row
                                py = col
                                player_count += 1

                                if winner_check(board, PLAYER_PIECE):
                                    label = myfont.render("Player wins!!", 1, PINK)
                                    game_screen.blit(label, (40, 10))
                                    game_over = True

                                if player_count == 2:
                                    player_count = 0
                                    turn += 1

                            else:
                                if (px,py) == (row,col):
                                    piece_drop(board, row, col, 0)
                                    player_count -= 1
                                    game_screen.fill(BROWN)

                            draw_board(board)
                            draw_recent(yellow_board, PLAYER_PIECE)


                if turn == -1 and not game_over:
                            piece_drop(board, 9, 9, PLAYER_PIECE)
                            turn = 0
                            draw_board(board)
                            draw_recent(yellow_board, PLAYER_PIECE)
                            break

                if turn % 2 == 0 and not game_over:
                    px = -1
                    py = -1
                    if turn == -2:
                        piece_drop(board, 9, 9, AI_PIECE)
                        turn =1
                        break
                    else:
                        pos = minimax(board, 4)
                        pos1 = pos[0]
                        pos2 = pos[1]

                        piece_drop(board, pos1[0], pos1[1], AI_PIECE)
                        piece_drop(board, pos2[0], pos2[1], AI_PIECE)
                        recent_piece_drop(yellow_board, pos1[0], pos1[1], AI_PIECE)
                        recent_piece_drop(yellow_board, pos2[0], pos2[1], AI_PIECE)

                        if winner_check(board, AI_PIECE):
                            label = myfont.render("AI wins!!", 1, BLUE)
                            game_screen.blit(label, (40, 10))
                            game_over = True

                    draw_board(board)
                    draw_recent(yellow_board, AI_PIECE)
                    yellow_board = yellow_board_create()

                    turn += 1

            if game_over:
                pygame.time.wait(3000)
                pygame.quit()
                pygame.init()
                main_screen = pygame.display.set_mode((500,400))
                pygame.display.set_caption('CONNECT 6 :: MAIN')
                start_button = pygame.Rect(200, 280, 100, 50)
                player1_button = (200,50)
                player2_button = (300,50)
                button_radius = 20
                selected_button = AI
                show_main_screen = True
                ob_cnt=0
                board = board_create()