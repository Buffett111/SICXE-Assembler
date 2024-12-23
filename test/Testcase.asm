MAIN    START   1000
        EXTDEF  LENGTH, BUFFER
        .Not recommanded,but we support blank after,
        EXTREF  DATA
        LDA     =C'EOF'
        STA     BUFFER
        LDA     BUFFER+10
        BASE    LENGTH
        LDCH    =X'F1'
        USE     BLOCK1
FIRST   STL     RETADR
        LDB     #LENGTH
        BASE    LENGTH
        USE     BLOCK2
SECOND  +LDA     DATA
        STA     BUFFER
        USE     BLOCK1
RETADR  RESW    1
LENGTH  WORD    30
BUFFER  RESB    10

WRREC	CSECT
        EXTREF	BUFFER,LENGTH
        EXTDEF DATA
        CLEAR	X
        +LDT	LENGTH
WLOOP	TD	=X'05'
        JEQ	WLOOP
        +LDCH	BUFFER,X
        WD	=X'05'
        TIXR	T
        JLT	WLOOP
DATA    WORD 20
        RSUB
        END	FIRST