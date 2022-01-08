tag: user.chess_grid_showing
-
^mark <user.any_alphanumeric_key>+$:
    user.chess_grid_click_square(any_alphanumeric_key_list)

chess flip:
    user.chess_grid_flip_board()

chess text:
    user.chess_grid_toggle_text()

chess show:
    user.chess_grid_show()

chess hide:
    user.chess_grid_hide()

chess [grid] off:
    user.chess_grid_close()
