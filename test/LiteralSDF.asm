TEST    START   1000
BUFFER  RESW    5
BUFFEND EQU     BUFFER+10
L1      LDA     =C'EOF'
        LDCH    =X'F1'
        STA     BUFFER
        END     TEST
