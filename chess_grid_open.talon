tag: user.chess_grid_activated
-
# make a move manually by clicking squares
# "manual each two each four" to move whatever piece is on e2 to e4
# "manual fine four" to click the square f4
^manual <user.any_alphanumeric_key>+$:
    user.chess_grid_click_square(any_alphanumeric_key_list)

# make a move using standard algebraic notation (SAN)
# "white each four" makes the move e4 as white
# "black near bat drum seven" makes the move Nbd7 as black
^white <user.any_alphanumeric_key>+$:
    user.chess_grid_move(any_alphanumeric_key_list, "white")
^black <user.any_alphanumeric_key>+$:
    user.chess_grid_move(any_alphanumeric_key_list, "black")

# flip the board's orientation from black to white or vice versa
chess flip:
    user.chess_grid_flip_board("")

# orient the board as white
chess white:
    user.chess_grid_flip_board("white")

# orient the board as black
chess black:
    user.chess_grid_flip_board("black")

# toggle the coordinate text on and off
chess text:
    user.chess_grid_toggle_text()

# show the chess grid overlay
chess show:
    user.chess_grid_show()

# hide the chess grid overlay
chess hide:
    user.chess_grid_hide()

# detect the state of the board using a prior reference, display in log
chess detect:
    user.chess_detect()

chess [grid] off:
    user.chess_grid_close()
