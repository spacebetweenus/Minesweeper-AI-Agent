# Minesweeper-AI-Agent

Implementing a Minesweeper AI Agent, which is able to play and solve the Minesweeper game.

Language used: Python




Three different difficulty: 
-- Beginner:  8 row x 8 column with 10 mines
-- Intermediate: 16x16 with 40 mines
-- Expert: 16x30 with 99 mines

File "Problems" provides 100*Intermediate worlds/environments for testing

To generate more worlds,issue the command: 

python3 WorldGenerator.py [numFiles] [filename] [rowDimension] [colDimension] [numMines]

In which, 
numFiles - The number of files to generate
filename - The base name of the file
rowDimension - The number of rows
colDimension - The number of columns
numMines - The number of mines

NOTES:
(1) The minimum number of rows is 4.
(2) The minimum number of columns is 4.
(3) The minimum number of mines is 1. 
(4) The number of mines must also be less than or equal to (rowDimension)*(colDimension) - 9
