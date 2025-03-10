// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// configuration
    @8192  // = 32 columns (à 16 pixels) * 256 rows
    D=A
    @segments
    M=D

(LOOP)
    @color
    M=0  // default to white

    @KBD
    D=M
    @NOT_PRESSED
    D;JEQ

    // key pressed
    @color
    M=-1  // change to black

(NOT_PRESSED)
    @SCREEN
    D=A
    @address
    M=D
    @segment
    M=0

    // change color of screen
(NEXT_SEGMENT)
    @color
    D=M 
    @address
    A=M
    M=D
    @address
    M=M+1  // next address
    @segment
    M=M+1  // next segment
    D=M
    @segments
    D=M-D
    @NEXT_SEGMENT
    D;JGT  // continue with next segment

    // all segments processed -> starting over
    @LOOP
    0;JMP
