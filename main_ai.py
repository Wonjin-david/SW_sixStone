import numpy as np
import pygame
import sys
import math

BROWN = (95, 69, 19)
DARKGREY = (70, 70, 70)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
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


def piece_drop(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, row, col):
    return board[row][col] == 0


def next_open_row(board, col):
    for row in range(no_of_rows):
        if board[row][col] == 0:
            return row


def print_board(board):
    print(np.flip(board, 0))


# connect 6 완성되었을 때
def winner_move(board, piece):
    """checks if the game is won for the player this board belongs to"""
    for slot in ind_list:
        a = np.where(board == 1, 0, board)
        a = np.where(board == 2, 1, a)
        b = np.where(board == 2, 0, board)
        check = sum(a[slot])
        if check >= C6:
            return True
        check = sum(b[slot])
        if check >= C6:
            return True
    return False


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


# def is_terminal_node(board):
#     return winner_move(board, PLAYER_PIECE) or winner_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

#---------------------------------------------------------------------------------------------------------------------------------------------------

def minimax(board, depth, alpha, beta, maximizingPlayer):
    # valid_locations = get_valid_locations(board) # get_valid_locations의 return값은 가능한 착수 가능한 좌표 리스트 [(0,0) ... (3,4), (4,4), (5,4) ...]
    # is_terminal = is_terminal_node(board)
    # if is_terminal:
    #     return (None, None, 100000000000000)
        # if winner_move(board, AI_PIECE):
        #     return (None, None, 100000000000000)
        # elif winner_move(board, PLAYER_PIECE):
        #     return (None, None, -10000000000000)
        # else:  # Game is over, no more valid moves
        #     return (None, None, 0)

    board_ai = np.where(board == 1, 0, board)
    board_ai = np.where(board == 2, 1, board_ai)
    board_player = np.where(board == 2, 0, board)

    # for i in range(30):
        # board_ai = np.where(board == 1, 0, board)
        # board_ai = np.where(board == 2, 1, board_ai)
        # board_player = np.where(board == 2, 0, board)

        # if i % 2 == 0:
    bestmoves, scores = find_best_mvs(board_ai, board_player)
    move = bestmoves[0]
        #     board_ai[move[0][0], move[0][1]] = 1
        #     board_ai[move[1][0], move[1][1]] = 1
        # else:
        #     bestmoves, scores = find_best_mvs(board_player, board_ai)
        #     move = bestmoves[0]
        #     board_player[move[0][0], move[0][1]] = 1
        #     board_player[move[1][0], move[1][1]] = 1

    return move, scores[0]

def find_best_mvs(ai, player):
    """finds best local moves"""
    moves = []
    best1 = apriori_1(ai, player)
    for i in range(10): #eval_pri -> 우리가 설정하는 값
        best2 = apriori_2(ai, player, best1[i])
        for j in range(10):
            moves.append((best1[i], best2[j]))
    bestmoves, scores = aposteriori(ai, player, moves)
    return bestmoves, scores

def apriori_1(ai, player):
    """evaluate board before making 1st move"""
    B_M, B_O = count_mat(ai, player, 4)
    ai_pri_1 = np.array([2, 6, 0, 1000]).reshape(4,1,1)
    player_pri_1 = np.array([1, 4, 10, 100]).reshape(4,1,1)
    B_eval = sum(B_M*ai_pri_1 + B_O*player_pri_1)
    bestmoves = top_n_indexes(B_eval, 10)
    return bestmoves

def apriori_2(ai, player, move1):
    """evaluate board before making 2nd move"""
    board_ai_virt = np.zeros((no_of_rows, no_of_columns)) + ai
    board_ai_virt[move1] = 1
    B_M, B_O = count_mat(board_ai_virt, player, 5)
    ai_pri_2 = np.array([2, 1, 6, 0, 1000]).reshape(5,1,1)
    player_pri_2 = np.array([1, 4, 6, 100, 100]).reshape(5,1,1)
    B_eval = sum(B_M*ai_pri_2 + B_O*player_pri_2)
    bestmoves = top_n_indexes(B_eval, 10)
    return bestmoves

def count_mat(ai, player, n_max):
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
    B_M = only_free(B_M, ai, player)
    B_O = only_free(B_O, ai, player)
    return B_M, B_O

def count_num(ai, player):
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

def only_free(B, ai, player):
    """gets rid of occupied spaces"""
    # multiply with free spaces
    board_free = np.remainder(ai + player + np.ones((no_of_rows, no_of_columns)), 2)
    B *= board_free
    return B

def aposteriori(ai, player, moves):
    """evaluate board after making two moves"""
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
        B_M, B_O = count_num(board_ai_virt, player)
        score = sum(B_M*ai_pos-B_O*player_pos)
        checklist.append(checkmove)
        scores.append(-score)
    if len(checklist) > 0:
            moves = checklist
            moves = [x for y, x in sorted(zip(scores,checklist))]
            scores = sorted(scores)
            del moves[1:]
            del scores[1:]
    return moves, scores


def top_n_indexes(array, n):
    """function gets indices in form of tuples of n largest entries of array"""
    inds = np.argpartition(array, array.size-n, axis=None)[-n:]
    width = array.shape[1]
    return [divmod(i, width) for i in inds]

#---------------------------------------------------------------------------------------------------------------------------------------------------

# def get_valid_locations(board):
#     valid_locations = []
#     for c in range(no_of_columns):
#         for r in range(no_of_rows):
#             if is_valid_location(board, r, c):
#                 valid_locations.append((r,c))
#     return valid_locations

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
                pygame.draw.circle(game_screen, RED, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(game_screen, YELLOW, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# def recent_drop():


###-----------------------------------------------------------------------------

# 게임판 2차원 배열
board = board_create()


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
main_screen = pygame.display.set_mode((500,200))
pygame.display.set_caption('CONNECT 6 :: MAIN')
button_rect = pygame.Rect(200, 100, 100, 50)
show_main_screen = True
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 마우스 왼쪽 버튼을 클릭했을 때
                if button_rect.collidepoint(event.pos):  # 버튼이 클릭되었을 때, 초기 화면을 숨기고 새로운 창을 열어 게임 진행
                    print("Here")
                    show_main_screen = False
                    pygame.quit()
        if show_main_screen:
            main_screen.fill((255, 255, 255))  # 흰색으로 화면 채우기
            pygame.draw.rect(main_screen, (0, 0, 255), button_rect)  # 파란색 버튼 그리기
            pygame.display.flip()
        else:
            pygame.init()
            SQUARESIZE = 50
            width = no_of_columns * SQUARESIZE
            height = no_of_rows * SQUARESIZE
            size = (width, height)
            RADIUS = int(SQUARESIZE / 2 - 5)
            game_screen = pygame.display.set_mode(size)
            pygame.display.set_caption('CONNECT 6 :: GAME')
            background_color = BROWN
            game_screen.fill(BROWN)
            draw_board(board)
            pygame.display.update()


            # 게임 진행
            game_over = False
            player_count = 0
            turn = 0
            while not game_over:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()

                    pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        if turn % 2 == 1:
                            print("Player")
                            posx = event.pos[0]
                            posy = event.pos[1]
                            col = int(math.floor(posx / SQUARESIZE))
                            row = int(math.floor(posy / SQUARESIZE))

                            if is_valid_location(board, row, col):
                                piece_drop(board, row, col, PLAYER_PIECE)
                                player_count += 1

                                if winner_move(board, PLAYER_PIECE):
                                    label = myfont.render("Player wins!!", 1, RED)
                                    game_screen.blit(label, (40, 10))
                                    game_over = True

                                if player_count == 2:
                                    player_count = 0
                                    turn += 1

                                draw_board(board)


                if turn % 2 == 0 and not game_over:
                    print("AI")
                    if turn == 0:
                        piece_drop(board, 9, 9, AI_PIECE)
                    else:
                        pos, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
                        pos1 = pos[0]
                        pos2 = pos[1]

                        piece_drop(board, pos1[0], pos1[1], AI_PIECE)
                        piece_drop(board, pos2[0], pos2[1], AI_PIECE)

                        if winner_move(board, AI_PIECE):
                            label = myfont.render("AI wins!!", 1, YELLOW)
                            game_screen.blit(label, (40, 10))
                            game_over = True

                    draw_board(board)

                    turn += 1

                if game_over:
                    pygame.time.wait(3000)
