tag: user.chess_grid_activated
-
^manual <user.any_alphanumeric_key>+$:
    user.chess_grid_click_square(any_alphanumeric_key_list)

^mark <user.any_alphanumeric_key>+$:
    user.chess_grid_move(any_alphanumeric_key_list, "white")

^black <user.any_alphanumeric_key>+$:
    user.chess_grid_move(any_alphanumeric_key_list, "black")

chess flip:
    user.chess_grid_flip_board("")

chess white:
    user.chess_grid_flip_board("white")

chess black:
    user.chess_grid_flip_board("black")

chess text:
    user.chess_grid_toggle_text()

chess show:
    user.chess_grid_show()

chess hide:
    user.chess_grid_hide()

chess detect:
    user.chess_detect()

chess [grid] off:
    user.chess_grid_close()
