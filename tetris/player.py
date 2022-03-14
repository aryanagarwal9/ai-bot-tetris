from board import Direction, Rotation, Action
from random import Random
# import pygame




class Player:
    def choose_action(self, board):
        raise NotImplementedError

class AryansPlayer(Player):
    def __init__(self, seed=None):
        list_of_heights = []
        self.random = Random(seed)
        self.list_of_heights = []

    def check_height(self, sandbox):
        self.list_of_heights = [0] * sandbox.width

        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    self.list_of_heights[x] = sandbox.height - y
                    break

        return sum(self.list_of_heights)

    def max_height(self, sandbox):

        if self.list_of_heights:
            return max(self.list_of_heights)

        else:
            return 0

    def check_holes(self, sandbox):
        holes = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) not in sandbox.cells:
                    if {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}.issubset(sandbox.cells):
                        holes += 1

        return holes

    def check_blockade(self, sandbox):
        blockade = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height - 1):
                if (x, y) in sandbox.cells and (x, y + 1) not in sandbox.cells:
                    blockade += 1

        return blockade

    def check_bumps(self, sandbox):
        bumpiness = 0
        for i in range(sandbox.width - 1):
            bumpiness += abs(self.list_of_heights[i +
                             1] - self.list_of_heights[i])

        return bumpiness

    def check_lines_cleared(self, sandbox, old_score):
        new_score = sandbox.score
        bonus = new_score - old_score
        lines_cleared = 0

        if bonus < 26:
            lines_cleared = 0
        elif bonus < 101:
            lines_cleared = -5
        elif bonus < 401:
            lines_cleared = 5
        elif bonus < 801:
            lines_cleared = 8
        else:
            lines_cleared = 9

        return lines_cleared

    def check_discard(self, sandbox):
        holes = self.check_holes(sandbox)
        if holes != 0 and sandbox.discards_remaining != 0:
            return True
        else:
            return False

    def score_board(self, sandbox, board):
        # a = -0.510066
        # b = 0.760666
        # c = -0.35663
        # d = -0.184483
        a = -0.710066
        b = 0.760666
        c = -0.35663
        d = -0.184483
        e = -0.495432
        # if self.max_height(sandbox) > 20:
        #     score = a * (self.check_height(sandbox))**2 + 1 * self.check_lines_cleared(
        #         sandbox, board.score) + c * self.check_holes(sandbox) + d * self.check_bumps(sandbox)
        # else:
        score = a * (self.check_height(sandbox)) + b * self.check_lines_cleared(
            sandbox, board.score) + c * self.check_holes(sandbox) + d * self.check_bumps(sandbox) + e * self.check_blockade(sandbox)

        return score

    def move_to_target(self, board, t_rot, t_pos):
        try:
            current_position = board.falling.left
            current_rotation = 0
            moves = []
            landed = False

            while current_rotation < t_rot and not landed:
                landed = board.rotate(Rotation.Anticlockwise)
                current_rotation += 1
                moves.append(Rotation.Anticlockwise)

            while current_position > t_pos and not landed:
                landed = board.move(Direction.Left)
                moves.append(Direction.Left)
                if not landed:
                    current_position = board.falling.left

            while current_position < t_pos and not landed:
                landed = board.move(Direction.Right)
                moves.append(Direction.Right)
                if not landed:
                    current_position = board.falling.left

            # never true when block is moving to right so change that
            if current_position == t_pos and not landed:
                landed = board.move(Direction.Drop)
                moves.append(Direction.Drop)

            return moves

        except Exception:
            return

    def choose_best_move(self, board):
        self.scores = []
        best_score = -10000000
        best_moves = []
        score = 0

        for rotation1 in range(4):
            for position1 in range(10):
                sandbox = board.clone()

                moves1 = self.move_to_target(sandbox, rotation1, position1)
                score1 = self.score_board(sandbox, board)

                for rotation2 in range(4):
                    for position2 in range(10):
                        sandbox2 = sandbox.clone()
                        moves2 = self.move_to_target(
                            sandbox2, rotation2, position2)
                        score2 = self.score_board(sandbox2, sandbox)

                # self.scores.append(score)
                        if score1 + score2 > best_score:
                            moves1_copy = moves1.copy()
                            moves2_copy = moves2.copy()

                            # print(moves1.extend(moves2))
                            best_board = sandbox2
                            best_score = score1 + score2
                            moves1_copy.extend(moves2_copy)
                            best_moves = moves1_copy

        if self.check_discard(best_board):
            best_moves = [Action.Discard]

        return best_moves

    def choose_action(self, board):
        sandbox = board.clone()

        moves = self.choose_best_move(board)

        # pygame.time.delay(1000)

        return moves

class BestScore(Player):
    def __init__(self, seed=None):
        list_of_heights = []
        self.random = Random(seed)
        self.list_of_heights = []

    def check_height(self, sandbox):
        self.list_of_heights = [0] * sandbox.width

        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    self.list_of_heights[x] = sandbox.height - y
                    break

        return sum(self.list_of_heights)

    def max_height(self, sandbox):

        if self.list_of_heights:
            return max(self.list_of_heights)

        else:
            return 0

    def check_holes(self, sandbox):
        holes = 0
        list_of_heights = [0] * sandbox.width
        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    list_of_heights[x] = sandbox.height - y
                    break
        for x in range(sandbox.width):
            for y in range(sandbox.height - list_of_heights[x], sandbox.height):
                if (x, y) not in sandbox.cells:
                    holes += 1

        return holes

    def check_blockade(self, sandbox):
        blockade = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height - 1):
                if (x, y) in sandbox.cells and (x, y + 1) not in sandbox.cells:
                    blockade += 1

        return blockade

    def check_bumps(self, sandbox):
        bumpiness = 0
        for i in range(sandbox.width - 1):
            bumpiness += abs(self.list_of_heights[i +
                             1] - self.list_of_heights[i])

        return bumpiness

    def check_wells(self, sandbox):
        wells = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    break
            else:
                wells = 1

        return wells

    #improve detector
    def check_four_block(self, sandbox, board, shape):
        filled_col = 0
        if self.check_wells(sandbox) == 1:
            for x in range(sandbox.width):
                for y in range(20, sandbox.height):
                    if (x, y) not in sandbox.cells:
                        break
                else:
                    filled_col += 1
        if shape == "Shape.I" and self.check_lines_cleared(sandbox, board.score) == 2500:
            return 1
        elif filled_col == 9:
            return 1
        else:
            return 0

    def check_bottom_holes(self, sandbox):
        for x in range(sandbox.width):
            for y in range(20, sandbox.height):
                if (x, y) in sandbox.cells:
                    for i in range(y, sandbox.height):
                        if (x, y) not in sandbox.cells:
                            return True


    def rotation_range(self, board):
        if str(board.falling.shape) == "Shape.I":
            return 2
        elif str(board.falling.shape) == "Shape.O":
            return 1
        else:
            return 4

    def check_lines_cleared(self, sandbox, old_score):
        new_score = sandbox.score
        bonus = new_score - old_score
        lines_cleared = 0

        if self.check_height(sandbox) > 130:
            if bonus < 26:
                lines_cleared = 0
            elif bonus < 101:
                lines_cleared = 1
            elif bonus < 401:
                lines_cleared = 2
            elif bonus < 801:
                lines_cleared = 3
            else:
                lines_cleared = 4

        else:
            if bonus < 26:
                lines_cleared = 0
            elif bonus < 101:
                lines_cleared = -20
            elif bonus < 401:
                lines_cleared = -10
            elif bonus < 801:
                lines_cleared = -4
            else:
                lines_cleared = 2500


        return lines_cleared

    def check_discard(self, sandbox, board):
        if sandbox.falling is not None and str(sandbox.falling.shape) != "Shape.I":
            holes_new = self.check_holes(sandbox)
            holes_old = self.check_holes(board)
            holes_net = holes_new - holes_old
            if holes_net > 0 and sandbox.discards_remaining != 0:
                return True
            else:
                return False

#some error
    def check_bomb(self, sandbox):
        long_blockade = 0
        counter = 0
        if sandbox.bombs_remaining == 0:
            return False
        for x in range(sandbox.width):
            for y in range(sandbox.height - 1):
                if y < 21 and (x, y) in sandbox.cells and ({(x, y + 1), (x, y + 2), (x, y + 3)}.isdisjoint(sandbox.cells) or {(x, y + 1), (x, y + 2)}.isdisjoint(sandbox.cells)):
                    for i in range(y, -1, -1):
                        if (x, y) in sandbox.cells:
                            counter += 1
                    if counter > 0 and counter < 3:
                        return True, y

    def score_board(self, sandbox, board, shape):
        # a = -0.510066
        # b = 0.760666
        # c = -0.35663
        # d = -0.184483
        if self.check_height(sandbox) > 130:
            a = -0.710066
            b = 0.760666
            c = -0.35663
            d = -0.184483
            e = -0.495432
            score = a * (self.check_height(sandbox)) + b * self.check_lines_cleared(sandbox, board.score)+ c * self.check_holes(sandbox)+ d * self.check_bumps(sandbox) + e * self.check_blockade(sandbox)

        else:
            a = -0.760066
            b = 0.660666
            c = -1.15663
            d = -0.124483
            e = -0.695432
            f = 1.57649
            g = 1000
            score = a * (self.check_height(sandbox)) + b * self.check_lines_cleared(sandbox, board.score) + c * self.check_holes(sandbox) + d * self.check_bumps(sandbox) + e * self.check_blockade(sandbox) + f * self.check_wells(sandbox) + g * self.check_four_block(sandbox, board, shape)
            # print(f"Score: {score}, Height: {a*self.check_height(sandbox)}, Lines: {b * self.check_lines_cleared(sandbox, board.score)}, Holes: {c * self.check_holes(sandbox)}, Bumps: {d * self.check_bumps(sandbox)}, Blockade: {e*self.check_blockade(sandbox)}, Wells: {f*self.check_wells(sandbox)}")

        return score

    def move_to_target(self, board, t_rot, t_pos):
        try:
            current_position = board.falling.left
            current_rotation = 0
            moves = []
            landed = False

            while current_rotation < t_rot and not landed:
                landed = board.rotate(Rotation.Anticlockwise)
                current_rotation += 1
                moves.append(Rotation.Anticlockwise)

            while current_position > t_pos and not landed:
                landed = board.move(Direction.Left)
                moves.append(Direction.Left)
                if not landed:
                    current_position = board.falling.left

            while current_position < t_pos and not landed:
                landed = board.move(Direction.Right)
                moves.append(Direction.Right)
                if not landed:
                    current_position = board.falling.left

            # never true when block is moving to right so change that
            if current_position == t_pos and not landed:
                landed = board.move(Direction.Drop)
                moves.append(Direction.Drop)

            return moves

        except Exception:
            return

    def choose_best_move(self, board):
        best_score = -10000000
        best_moves = []
        score = 0

        for rotation1 in range(self.rotation_range(board)):
            for position1 in range(10):
                sandbox = board.clone()
                shape1 = str(sandbox.falling.shape)
                moves1 = self.move_to_target(sandbox, rotation1, position1)
                score1 = self.score_board(sandbox, board, shape1)

                for rotation2 in range(self.rotation_range(sandbox)):
                    for position2 in range(10):
                        sandbox2 = sandbox.clone()
                        shape2 = str(sandbox.falling.shape)
                        moves2 = self.move_to_target(sandbox2, rotation2, position2)
                        score2 = self.score_board(sandbox2, sandbox, shape2)

                        if score1 + score2 > best_score:
                            moves1_copy = moves1.copy()
                            moves2_copy = moves2.copy()

                            # print(moves1.extend(moves2))
                            best_board = sandbox2
                            best_score = score1 + score2
                            moves1_copy.extend(moves2_copy)
                            best_moves = moves1_copy

        if self.check_discard(best_board, board):
            best_moves = [Action.Discard]


        return best_moves

    def choose_action(self, board):
        moves = self.choose_best_move(board)
        # pygame.time.delay(1000)

        return moves



class BestScoreExperiment(Player):
    def __init__(self, seed=None):
        list_of_heights = []
        self.random = Random(seed)
        self.list_of_heights = []
        self.holes = 0

    def check_height(self, sandbox):
        self.list_of_heights = [0] * sandbox.width
        self.height = 0

        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    self.list_of_heights[x] = sandbox.height - y
                    break

        self.height = sum(self.list_of_heights)
        return self.height

    def max_height(self, sandbox):

        if self.list_of_heights:
            return max(self.list_of_heights)

        else:
            return 0

    def check_holes(self, sandbox):
        self.holes = 0
        list_of_heights = [0] * sandbox.width
        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    list_of_heights[x] = sandbox.height - y
                    break
        for x in range(sandbox.width):
            for y in range(sandbox.height - list_of_heights[x], sandbox.height):
                if (x, y) not in sandbox.cells:
                    self.holes += 1

        return self.holes

    def check_blockade(self, sandbox):
        blockade = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height - 1):
                if (x, y) in sandbox.cells and (x, y + 1) not in sandbox.cells:
                    blockade += 1

        return blockade

    def check_bumps(self, sandbox):
        bumpiness = 0
        for i in range(sandbox.width - 1):
            bumpiness += abs(self.list_of_heights[i +
                             1] - self.list_of_heights[i])

        return bumpiness

    def check_wells(self, sandbox):
        self.wells = 0
        for x in range(sandbox.width):
            for y in range(sandbox.height):
                if (x, y) in sandbox.cells:
                    break
            else:
                self.wells = 1

        return self.wells

    def check_four_block(self, sandbox, board, shape):
        filled_col = 0
        if self.wells == 1:
            for x in range(sandbox.width):
                for y in range(20, sandbox.height):
                    if (x, y) not in sandbox.cells:
                        break
                else:
                    filled_col += 1
        if shape == "Shape.I" and self.check_lines_cleared(sandbox, board.score) == 2500:
            return 1
        elif filled_col == 9:
            return 1
        else:
            return 0

    def rotation_range(self, board):
        if str(board.falling.shape) == "Shape.I":
            return 2
        elif str(board.falling.shape) == "Shape.O":
            return 1
        else:
            return 4

    def check_lines_cleared(self, sandbox, old_score):
        new_score = sandbox.score
        bonus = new_score - old_score
        lines_cleared = 0

        if self.height > 130:
            if bonus < 26:
                lines_cleared = 0
            elif bonus < 101:
                lines_cleared = 1
            elif bonus < 401:
                lines_cleared = 2
            elif bonus < 801:
                lines_cleared = 3
            else:
                lines_cleared = 4

        elif self.holes == 0:
            if bonus < 26:
                lines_cleared = 0
            elif bonus < 101:
                lines_cleared = -50
            elif bonus < 401:
                lines_cleared = -40
            elif bonus < 801:
                lines_cleared = -30
            else:
                lines_cleared = 2500
        else:
            if bonus < 26:
                lines_cleared = 0
            elif bonus < 101:
                lines_cleared = -20
            elif bonus < 401:
                lines_cleared = -10
            elif bonus < 801:
                lines_cleared = -4
            else:
                lines_cleared = 2500


        return lines_cleared

    def check_discard(self, sandbox, board):
        if sandbox.falling is not None and str(sandbox.falling.shape) != "Shape.I":
            holes_new = self.check_holes(sandbox)
            holes_old = self.check_holes(board)
            holes_net = holes_new - holes_old
            if holes_net > 0 and sandbox.discards_remaining != 0:
                return True
            else:
                return False


    def score_board(self, sandbox, board, shape):
        height = self.check_height(sandbox)
        lines_cleared = self.check_lines_cleared(sandbox, board.score)
        holes = self.check_holes(sandbox)
        bumps = self.check_bumps(sandbox)
        blockade = self.check_blockade(sandbox)
        wells = self.check_wells(sandbox)
        four_block = self.check_four_block(sandbox, board, shape)
        if height > 130:
            a = -0.710066
            b = 0.760666
            c = -0.35663
            d = -0.184483
            e = -0.495432
            score = a * height + b * lines_cleared + c * holes + d * bumps + e * blockade

        else:
            a = -0.760066
            b = 0.660666
            c = -1.15663
            d = -0.124483
            e = -0.695432
            f = 1.57649
            g = 1000
            score = a * height + b * lines_cleared + c * holes + d * bumps + e * blockade + f * wells + g * four_block
            # print(f"Score: {score}, Height: {a*self.check_height(sandbox)}, Lines: {b * self.check_lines_cleared(sandbox, board.score)}, Holes: {c * self.check_holes(sandbox)}, Bumps: {d * self.check_bumps(sandbox)}, Blockade: {e*self.check_blockade(sandbox)}, Wells: {f*self.check_wells(sandbox)}")

        return score

    def move_to_target(self, board, t_rot, t_pos):
        try:
            current_position = board.falling.left
            current_rotation = 0
            moves = []
            landed = False

            while current_rotation < t_rot and not landed:
                landed = board.rotate(Rotation.Anticlockwise)
                current_rotation += 1
                moves.append(Rotation.Anticlockwise)

            while current_position > t_pos and not landed:
                landed = board.move(Direction.Left)
                moves.append(Direction.Left)
                if not landed:
                    current_position = board.falling.left

            while current_position < t_pos and not landed:
                landed = board.move(Direction.Right)
                moves.append(Direction.Right)
                if not landed:
                    current_position = board.falling.left

            # never true when block is moving to right so change that
            if current_position == t_pos and not landed:
                landed = board.move(Direction.Drop)
                moves.append(Direction.Drop)

            return moves

        except Exception:
            return

    def choose_best_move(self, board):
        best_score = -10000000
        best_moves = []
        score = 0

        for rotation1 in range(self.rotation_range(board)):
            for position1 in range(10):
                sandbox = board.clone()
                shape1 = str(sandbox.falling.shape)
                moves1 = self.move_to_target(sandbox, rotation1, position1)
                score1 = self.score_board(sandbox, board, shape1)

                for rotation2 in range(self.rotation_range(sandbox)):
                    for position2 in range(10):
                        sandbox2 = sandbox.clone()
                        shape2 = str(sandbox.falling.shape)
                        moves2 = self.move_to_target(sandbox2, rotation2, position2)
                        score2 = self.score_board(sandbox2, sandbox, shape2)

                        if score1 + score2 > best_score:
                            moves1_copy = moves1.copy()
                            best_board = sandbox2
                            best_score = score1 + score2
                            best_moves = moves1_copy

        if self.check_discard(best_board, board):
            best_moves = [Action.Discard]


        return best_moves

    def choose_action(self, board):
        moves = self.choose_best_move(board)

        return moves


SelectedPlayer = BestScore
