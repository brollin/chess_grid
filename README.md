# Chess Grid

## Overview
Chess Grid is an interactive voice-command chess tool intended to be used with the
[Talon Voice framework](https://talonvoice.com/).

Chess Grid allows you to use voice commands to move pieces on any chess board, such as this one from Lichess:
![normal board](images/board_normal.png)

By saying the command `chess grid`, the chess board will be automatically detected and a grid will be overlaid on top of it:
![board with grid](images/board_grid.png)

Never fear! You can then hide the grid with the command `chess hide`.

You can move a piece with a command such as

`mark each four fine five`

to move the pawn from E4 to F5.
Check out the talon files to see the other commands that are available.

## Future work
- Allow showing only the labels
- Allow manually positioning the grid
- Implement piece detection, perhaps like [this](https://github.com/IlicStefan/ChessDiagramRecognition/)
- Possible piece detection data set [here](https://www.kaggle.com/anshulmehtakaggl/chess-pieces-detection-images-dataset)
- Using piece detection, implement more natural move commands like `knight each four`
