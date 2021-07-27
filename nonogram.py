

def merge_results(res_1, res_2):
    """
    Merges the possible results. This is necessary as the type of results
    changes, sometimes a string, sometimes a list and sometimes none.
    :param res_1:
    :param res_2:
    :return:
    """
    merged_list = []
    if res_1:
        if type(res_1[0]) == list:
            for lst_1 in res_1:
                merged_list.append(lst_1)
        else:
            merged_list.append(res_1)
    if res_2:
        if type(res_2[0]) == list:
            for lst_2 in res_2:
                merged_list.append(lst_2)
        else:
            merged_list.append(res_2)
    return merged_list


def get_constrains_from_row(row):
    contrains = []
    len_counter = 0
    for val in row:
        if val == 1:
            len_counter += 1
        if val == 0 or val == -1:
            if len_counter:
                contrains.append(len_counter)
                len_counter = 0
    if len_counter:  # add the last one who doesn't have a 0 following
        contrains.append(len_counter)
    return contrains


def get_possible_constrains_from_row(row):
    constrains = []
    len_counter = 0
    for val in row:
        if val == 1 or val == -1:
            len_counter += 1
        if val == 0:
            if len_counter:
                constrains.append(len_counter)
                len_counter = 0
    if len_counter:  # add the last one who doesn't have a 0 following
        constrains.append(len_counter)
    return constrains


def check_if_row_can_meet_constrains(row, wanted_constrains,
                                     current_constrains):
    num_of_zero = row.count(0)
    if len(row) - num_of_zero < sum(wanted_constrains):  # too many zeros
        return False
    if len(current_constrains) > 0 and len(wanted_constrains) > 0:  # a row
        # with at list one block
        if max(current_constrains) > max(wanted_constrains):  # the max block
            # is bigger then the wanted max block
            return False
        elif sum(current_constrains) > sum(wanted_constrains):  # the number of
            # black cells in the row is bigger the the wanted black cells
            # number
            return False

        possible_constrains = get_possible_constrains_from_row(row)  # get the
        # length of the possible block using -1 cells
        if max(possible_constrains) < max(wanted_constrains):  # if the
            # length of the max block using the -1 cells isn't big enough,
            # it not going to
            # be able to meet the constrains
            return False
    else:  # it's maybe possible to meet constrains
        return True
    return True


def check_if_row_meets_constrains(row, wanted_constrains):
    current_constrains = get_constrains_from_row(row)
    if wanted_constrains == current_constrains:  # perfect!
        return 1
    elif -1 not in row:  # complete but wrong row
        return -1

    # check if the un completed row can meet the constrains in the future
    elif check_if_row_can_meet_constrains(row, wanted_constrains,
                                          current_constrains):
        return 0
    else:
        return -1


def fix_get_row_variations(row, blocks):
    res = get_row_variations(row, blocks)
    if res:
        if type(res[0]) == int:
            return [res]
        else:
            return res
    else:
        return []


def get_row_variations(row, blocks):
    """
    :param row: a given row from the board
    :param blocks: the constrains on the row
    :return: list of all the possible rows answering those constrains
    if the row it self it the only option - return the row itself
    """
    # stopping condition
    indicate = check_if_row_meets_constrains(row, blocks)
    if indicate == 1:
        return [[r if r != -1 else 0 for r in row]]

    if indicate == -1:
        return []
    # step
    ind = row.index(-1)
    row_copy_1 = [r for r in row]
    row_copy_1[ind] = 0
    add_0 = get_row_variations(row_copy_1, blocks)
    row_copy_2 = [r for r in row]
    row_copy_2[ind] = 1
    add_1 = get_row_variations(row_copy_2, blocks)

    return merge_results(add_0, add_1)


def get_intersection_row(rows):
    """
    :param rows: number of rows from the output of the get_row_variations
    function
    the purpose of the function is to find if the values of each index
    in the rows is mutual or different
    :return: - a row that represent the decision for each index: if all said 1-
     then 1, if all said 0- then 0, if some said 0 and some said 1- then -1.
    """
    if len(rows) == 0:
        return []
    n_row = len(rows)
    n_col = len(rows[0])
    final_row = []
    for j in range(n_col):
        col = []
        for i in range(n_row):
            col.append(rows[i][j])
        if len(set(col)) == 1:
            final_row.append(col[0])
        else:
            final_row.append((-1))
    return final_row


def transpose_board(board):
    board_as_columns = []
    for i in range(len(board[0])):
        column_i = []
        for j in range(len(board)):
            column_i.append(board[j][i])
        board_as_columns.append(column_i)  # changed the board to
        # list of columns
    # In order not to have to replace the transpose board we
    # had to change the original board like this
    for i in range(len(board)):
        board.pop(0)
    for i in range(len(board_as_columns)):
        board.append(board_as_columns[i])


def conclude_from_constraints(board, constraints):
    """
    :param board: the nonogram board
    :param constraints: the constrains on the board
    :return: the board with all the values that can be filled without
    gussing, only certain decisions
    """
    # turn board into an object
    # start by looking at all rows and columns that will lead us to the next
    # moves by adding rows/columns to look at in cases something has changed
    # in  those rows/columns
    if len(board) == 0:
        return
    check_after_update_idxs = [(0, row) for row in range(len(board))] + \
                              [(1, col) for col in range(len(board[0]))]

    while len(check_after_update_idxs):  # while there are still rows/columns
        # to check
        row_or_col, idx = check_after_update_idxs[0]
        if row_or_col == 0:  # row
            row_var = get_row_variations(board[idx], constraints[0][idx])
            if not row_var:  # no variartion, stop looking and move to the
                # next move
                check_after_update_idxs.pop(0)
                continue
            inter_row = get_intersection_row(row_var)
            if board[idx] != inter_row:  # only if the X/_ are new
                # information we will update the row, and check the columns
                # infected by this update
                for inter_i, val in enumerate(inter_row):
                    if val != -1 and board[idx][inter_i] == -1:
                        check_after_update_idxs.append((1, inter_i))
                board[idx] = inter_row

        if row_or_col == 1:  # column
            transpose_board(board)  # turn rows to columns
            row_var = get_row_variations(board[idx], constraints[1][idx])
            if not row_var:  # no variartion, stop looking and move to the
                # next move
                transpose_board(board)
                check_after_update_idxs.pop(0)
                continue
            inter_row = get_intersection_row(row_var)
            if board[idx] != inter_row:  # only if the X/_ are new
                # information we will update the column, and check the rows
                # infected by this update
                for inter_i, val in enumerate(inter_row):
                    if val != -1 and board[idx][inter_i] == -1:
                        check_after_update_idxs.append((0, inter_i))
                board[idx] = inter_row
            transpose_board(board)  # turn back columns to rows
        check_after_update_idxs.pop(0)
        check_after_update_idxs = list(set(check_after_update_idxs))


def solve_easy_nonogram(constraints):
    """
    :param constraints: the constrains on the board
    build a initial board using the dimensions of the constrains of the row
    and the columns
    iteratively we will "get_row_variations" then "get_intersection_row" and
    "conclude_from_constrains"
    agian and again until we can't fill no more cells or we finished
    :return: the final board
    """
    if len(constraints) == 0 or len(constraints[0]) == 0 or len(constraints[1]) \
            == 0:
        if len(constraints) == 0:
            return []
        return [[[] for i in range(len(constraints[0]))], [[] for j in range(
            len(constraints[1]))]]
    board = [[-1 for i in range(len(constraints[1]))] for j in range(len(
        constraints[0]))]
    conclude_from_constraints(board, constraints)
    return board


if __name__ == "__main__":
    pass
