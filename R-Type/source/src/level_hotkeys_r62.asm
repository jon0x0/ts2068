; All disk-region banks share this immutable main-loop hotkey handler.
        ORG HOT_ORIGIN
HOT_STATE EQU $FDA5
JOB_ORIG EQU $FDA7
JOB_HOLDER EQU $FDA8
JOB_CTX0 EQU $FDA9
JOB_CTX1 EQU $FDAA
JOB_CTX2 EQU $FDAB
JOB_SP EQU $FDAC
JOB_VALID EQU $FDAE
JOB_VIDEO EQU $FDAF
hotkeys:
 IF HOME_VARIANT
        LD A,1
        OUT ($F4),A
 ENDIF
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD BC,$BFFE
        IN A,(C)
        AND 2
        JR NZ,hot_l_up
        LD A,(HOT_STATE)
        CP 3
        JP Z,hot_done
        LD BC,$FEFE
        IN A,(C)
        AND 1
        JP Z,hot_preload
        LD A,(HOT_STATE)
        OR A
        JR NZ,hot_numbers
        LD A,1
        LD (HOT_STATE),A
        JR hot_numbers
hot_l_up:
        LD A,(HOT_STATE)
        CP 3
        JR NZ,hot_arm
        XOR A
        LD (HOT_STATE),A
        JR hot_done
hot_arm:
        OR A
        JR Z,hot_done
        LD A,2
        LD (HOT_STATE),A
hot_numbers:
        LD BC,$F7FE
        IN A,(C)
        CPL
        AND 31
        LD D,1
        JR Z,hot_upper
hot_bit:
        RRA
        JR C,hot_jump
        INC D
        JR hot_bit
hot_upper:
        LD B,$EF
        IN A,(C)
        CPL
        AND $1C
        JR Z,hot_done
        LD D,6
        BIT 4,A
        JR NZ,hot_jump
        INC D
        BIT 3,A
        JR NZ,hot_jump
        INC D
hot_jump:
        LD A,3
        LD (HOT_STATE),A
        LD A,D
        LD ($FD95),A
        LD A,1
        LD ($FDA3),A
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        POP HL ; discard the dispatcher return
        POP AF ; restore dispatcher's saved original AF
        ; A level change abandons this world update. Returning to $8659
        ; skips ECM/front/retained initialization and native object reset.
        POP HL ; discard the interrupted world-loop continuation
        LD HL,$8640 ; normal ECM init -> object reset -> ship setup
        PUSH HL
        LD HL,NATIVE_SELECT_START
        PUSH HL
        PUSH AF
        LD A,9
        JP $0E11
hot_done:
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        RET
hot_preload:
        LD A,3
        LD (HOT_STATE),A
        LD A,($FD4A)
        CP $FF
        JP Z,hot_done
        LD (JOB_SP),SP
        XOR A
        OUT ($FE),A ; silence the beeper and set the loading border
        LD HL,$FDC0
        LD D,3
        LD E,8
        LD BC,$FFF5
save_ay_volumes:
        LD A,E
        OUT (C),A
        INC C
        IN A,(C)
        LD (HL),A
        XOR A
        OUT (C),A ; silence this channel as soon as the request is accepted
        INC HL
        DEC C
        INC E
        DEC D
        JR NZ,save_ay_volumes
        LD A,($FD49)
        LD (JOB_ORIG),A
        LD A,($FD48)
        LD (JOB_HOLDER),A
        IN A,($FF)
        LD (JOB_VIDEO),A
 IF HOME_VARIANT
        LD A,$21
        OUT ($F4),A
        CALL LOADING_FEEDBACK
        LD A,1
        OUT ($F4),A
 ELSE
        CALL LOADING_FEEDBACK
 ENDIF
        JP preload_begin
