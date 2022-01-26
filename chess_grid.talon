# find a chessboard in the active window and overlay the grid. no piece detection, so only the
# manual move command will work
chess grid:
    user.chess_grid_activate()

# find a chessboard in the active window. assume pieces are in their normal starting positions,
# and save them for future use in detecting later positions. append the word black or white to
# set the starting orientation.
# "chess reference white"
# "chess reference black"
chess reference [<user.text>]:
    user.chess_reference(user.text or "")
