; Native nonblocking arcade-derived AY effects; selected65 death envelope/noise.
 IFDEF ROM_ONLY
RUNTIME_MAP EQU 3
 ELSE
RUNTIME_MAP EQU 9
 ENDIF
PENDING EQU $FBC0
ACTIVE EQU $FBC1
DELAY EQU $FBC2
NOISE EQU $FBC3
BANK EQU $FBC4
POINTER EQU $FBC5
PHASE EQU $FBC7
INITIALIZED EQU $FBC9
        ORG $F87C
        JP sound_queue
sound_queue:
        PUSH AF
        LD A,H
        CP 22
        JR C,queue_valid
        AND 15
queue_valid:
        LD (PENDING),A
        POP AF
        RET
; Called with DI by the native IRQ. No joystick R14/R15 access.
ay_write:
        PUSH BC
        LD BC,$FFF5
        OUT (C),A
        LD BC,$FFF6
        LD A,E
        OUT (C),A
        POP BC
        RET
        ASSERT $ <= $F8E8
        INCLUDE "src/compiled_sprite_key.inc"
        DS $F8E8-$,$FF
        RET ; obsolete beeper channel callbacks
music_gateway:
        LD A,RUNTIME_MAP|$10
        OUT ($F4),A
        CALL $9C00
        LD A,RUNTIME_MAP
        OUT ($F4),A
        JP ay_tick
        DS $F8F8-$,$FF
        RET
        DS $F908-$,$FF
        RET
        DS $F922-$,$FF
        RET
        DS $F930-$,$FF
ay_irq:
        IN A,($F4) ; HSR is R/W, Timex technical manual2.1.13
        PUSH AF
        LD A,(INITIALIZED)
        AND A
        JR NZ,ay_scheduled
        INC A
        LD (INITIALIZED),A
        XOR A
        LD ($FD93),A
        LD ($FD94),A
        LD E,0
        LD A,8
        CALL ay_write
        LD A,9
        CALL ay_write
        LD A,10
        CALL ay_write
ay_scheduled:
        LD HL,(PHASE)
        LD DE,1834
        ADD HL,DE
        LD DE,2205
        AND A
        SBC HL,DE
        JR NC,ay_tick_due
        ADD HL,DE
        LD (PHASE),HL
        JP ay_irq_done
ay_tick_due:
        LD (PHASE),HL
        CALL music_gateway
ay_irq_done:
        POP AF
        OUT ($F4),A
        LD HL,$7A8A ; displaced native BE2D; caller then increments frame timer
        RET
ay_tick:
        LD A,(PENDING)
        OR A
        JR Z,ay_continue
        LD B,A
        XOR A
        LD (PENDING),A
        LD A,(ACTIVE)
        CP B
        JR Z,ay_continue
        CP 11
        JR Z,ay_continue
        LD A,B
        LD (ACTIVE),A
        LD C,A
        LD B,0
        LD H,B
        LD L,C
        ADD HL,HL
        ADD HL,BC
        LD BC,$0480
        ADD HL,BC
        LD A,(HL)
        LD (BANK),A
        INC HL
        LD E,(HL)
        INC HL
        LD D,(HL)
        LD (POINTER),DE
        XOR A
        LD (DELAY),A
        LD A,$B8
        LD (NOISE),A
ay_continue:
        LD A,(ACTIVE)
        OR A
        RET Z
        LD A,(DELAY)
        OR A
        JR Z,ay_read_frame
        DEC A
        LD (DELAY),A
        RET
ay_read_frame:
        LD A,(BANK)
        OR RUNTIME_MAP
        OUT ($F4),A
        LD HL,(POINTER)
        LD A,(HL)
        INC HL
        OR A
        JR Z,ay_stop
        DEC A
        LD (DELAY),A
        LD B,(HL)
        INC HL
        LD C,0
ay_frame_register:
        SRL B
        JR NC,ay_frame_skip
        LD E,(HL)
        INC HL
        LD A,C
        CP 2
        JR C,ay_frame_write
        CP 5
        JR C,ay_base_register
        CP 7
        LD A,9
        JR Z,ay_frame_write
        LD A,C
        SUB 3
        JR ay_frame_write
ay_base_register:
        ADD A,4
        CP 7
        JR NZ,ay_frame_write
        LD A,E
        LD (NOISE),A
        LD A,7
ay_frame_write:
        CALL ay_write
ay_frame_skip:
        INC C
        LD A,C
        CP 8
        JR NZ,ay_frame_register
        CALL $0BC0 ; death-only envelope trailer; preserves shape on skipped ticks
        LD (POINTER),HL
        JR ay_restore_map
ay_stop:
        LD A,(ACTIVE)
        CP 11
        JR NZ,ay_stop_a
        LD E,0
        LD A,9
        CALL ay_write
ay_stop_a:
        XOR A
        LD (ACTIVE),A
        LD E,A
        LD A,8
        CALL ay_write
        LD E,$B8
        LD A,7
        CALL ay_write
ay_restore_map:
        LD A,RUNTIME_MAP
        OUT ($F4),A
        RET
        INCLUDE "src/background_rows.inc"
        INCLUDE "src/compiled_sprite_runtime.inc"
        ASSERT $ <= $FBC0
        DS $FBC0-$,$FF
        DS 10,0
        ASSERT $ < $FC0B

        IFDEF TITLE_DELTA
        INCLUDE "src/title_delta_cell.inc"
        ELSE
        INCLUDE "src/title_reveal.inc"
        ENDIF
        INCLUDE "src/irq_banking.inc"
