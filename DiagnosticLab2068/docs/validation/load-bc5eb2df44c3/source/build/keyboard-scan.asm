 ld bc,$fefe
 in a,(c)
 ld e,a
 ld hl,$5b00
 bit 0,e
 jr nz,key_up_0
 ld (hl),1
 ld a,$60
 jr key_color_0
key_up_0:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_0
 ld a,$68
key_color_0:
 ld hl,$59c0
 ld b,3
 ld iy,key_painted_0_0
 jp keyboard_paint
key_painted_0_0:
 ld a,c
 ld hl,$59dd
 ld b,3
 ld iy,key_painted_0_1
 jp keyboard_paint
key_painted_0_1:
 ld hl,$5b01
 bit 1,e
 jr nz,key_up_1
 ld (hl),1
 ld a,$60
 jr key_color_1
key_up_1:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_1
 ld a,$68
key_color_1:
 ld hl,$59c3
 ld b,2
 ld iy,key_painted_1_0
 jp keyboard_paint
key_painted_1_0:
 ld hl,$5b02
 bit 2,e
 jr nz,key_up_2
 ld (hl),1
 ld a,$60
 jr key_color_2
key_up_2:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_2
 ld a,$68
key_color_2:
 ld hl,$59c6
 ld b,2
 ld iy,key_painted_2_0
 jp keyboard_paint
key_painted_2_0:
 ld hl,$5b03
 bit 3,e
 jr nz,key_up_3
 ld (hl),1
 ld a,$60
 jr key_color_3
key_up_3:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_3
 ld a,$68
key_color_3:
 ld hl,$59c9
 ld b,2
 ld iy,key_painted_3_0
 jp keyboard_paint
key_painted_3_0:
 ld hl,$5b04
 bit 4,e
 jr nz,key_up_4
 ld (hl),1
 ld a,$60
 jr key_color_4
key_up_4:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_4
 ld a,$68
key_color_4:
 ld hl,$59cc
 ld b,2
 ld iy,key_painted_4_0
 jp keyboard_paint
key_painted_4_0:
 ld bc,$fdfe
 in a,(c)
 ld e,a
 ld hl,$5b05
 bit 0,e
 jr nz,key_up_5
 ld (hl),1
 ld a,$60
 jr key_color_5
key_up_5:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_5
 ld a,$68
key_color_5:
 ld hl,$5962
 ld b,2
 ld iy,key_painted_5_0
 jp keyboard_paint
key_painted_5_0:
 ld hl,$5b06
 bit 1,e
 jr nz,key_up_6
 ld (hl),1
 ld a,$60
 jr key_color_6
key_up_6:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_6
 ld a,$68
key_color_6:
 ld hl,$5965
 ld b,2
 ld iy,key_painted_6_0
 jp keyboard_paint
key_painted_6_0:
 ld hl,$5b07
 bit 2,e
 jr nz,key_up_7
 ld (hl),1
 ld a,$60
 jr key_color_7
key_up_7:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_7
 ld a,$68
key_color_7:
 ld hl,$5968
 ld b,2
 ld iy,key_painted_7_0
 jp keyboard_paint
key_painted_7_0:
 ld hl,$5b08
 bit 3,e
 jr nz,key_up_8
 ld (hl),1
 ld a,$60
 jr key_color_8
key_up_8:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_8
 ld a,$68
key_color_8:
 ld hl,$596b
 ld b,2
 ld iy,key_painted_8_0
 jp keyboard_paint
key_painted_8_0:
 ld hl,$5b09
 bit 4,e
 jr nz,key_up_9
 ld (hl),1
 ld a,$60
 jr key_color_9
key_up_9:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_9
 ld a,$68
key_color_9:
 ld hl,$596e
 ld b,2
 ld iy,key_painted_9_0
 jp keyboard_paint
key_painted_9_0:
 ld bc,$fbfe
 in a,(c)
 ld e,a
 ld hl,$5b0a
 bit 0,e
 jr nz,key_up_10
 ld (hl),1
 ld a,$60
 jr key_color_10
key_up_10:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_10
 ld a,$68
key_color_10:
 ld hl,$5901
 ld b,2
 ld iy,key_painted_10_0
 jp keyboard_paint
key_painted_10_0:
 ld hl,$5b0b
 bit 1,e
 jr nz,key_up_11
 ld (hl),1
 ld a,$60
 jr key_color_11
key_up_11:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_11
 ld a,$68
key_color_11:
 ld hl,$5904
 ld b,2
 ld iy,key_painted_11_0
 jp keyboard_paint
key_painted_11_0:
 ld hl,$5b0c
 bit 2,e
 jr nz,key_up_12
 ld (hl),1
 ld a,$60
 jr key_color_12
key_up_12:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_12
 ld a,$68
key_color_12:
 ld hl,$5907
 ld b,2
 ld iy,key_painted_12_0
 jp keyboard_paint
key_painted_12_0:
 ld hl,$5b0d
 bit 3,e
 jr nz,key_up_13
 ld (hl),1
 ld a,$60
 jr key_color_13
key_up_13:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_13
 ld a,$68
key_color_13:
 ld hl,$590a
 ld b,2
 ld iy,key_painted_13_0
 jp keyboard_paint
key_painted_13_0:
 ld hl,$5b0e
 bit 4,e
 jr nz,key_up_14
 ld (hl),1
 ld a,$60
 jr key_color_14
key_up_14:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_14
 ld a,$68
key_color_14:
 ld hl,$590d
 ld b,2
 ld iy,key_painted_14_0
 jp keyboard_paint
key_painted_14_0:
 ld bc,$f7fe
 in a,(c)
 ld e,a
 ld hl,$5b0f
 bit 0,e
 jr nz,key_up_15
 ld (hl),1
 ld a,$60
 jr key_color_15
key_up_15:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_15
 ld a,$68
key_color_15:
 ld hl,$58a0
 ld b,2
 ld iy,key_painted_15_0
 jp keyboard_paint
key_painted_15_0:
 ld hl,$5b10
 bit 1,e
 jr nz,key_up_16
 ld (hl),1
 ld a,$60
 jr key_color_16
key_up_16:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_16
 ld a,$68
key_color_16:
 ld hl,$58a3
 ld b,2
 ld iy,key_painted_16_0
 jp keyboard_paint
key_painted_16_0:
 ld hl,$5b11
 bit 2,e
 jr nz,key_up_17
 ld (hl),1
 ld a,$60
 jr key_color_17
key_up_17:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_17
 ld a,$68
key_color_17:
 ld hl,$58a6
 ld b,2
 ld iy,key_painted_17_0
 jp keyboard_paint
key_painted_17_0:
 ld hl,$5b12
 bit 3,e
 jr nz,key_up_18
 ld (hl),1
 ld a,$60
 jr key_color_18
key_up_18:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_18
 ld a,$68
key_color_18:
 ld hl,$58a9
 ld b,2
 ld iy,key_painted_18_0
 jp keyboard_paint
key_painted_18_0:
 ld hl,$5b13
 bit 4,e
 jr nz,key_up_19
 ld (hl),1
 ld a,$60
 jr key_color_19
key_up_19:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_19
 ld a,$68
key_color_19:
 ld hl,$58ac
 ld b,2
 ld iy,key_painted_19_0
 jp keyboard_paint
key_painted_19_0:
 ld bc,$effe
 in a,(c)
 ld e,a
 ld hl,$5b14
 bit 0,e
 jr nz,key_up_20
 ld (hl),1
 ld a,$60
 jr key_color_20
key_up_20:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_20
 ld a,$68
key_color_20:
 ld hl,$58bb
 ld b,2
 ld iy,key_painted_20_0
 jp keyboard_paint
key_painted_20_0:
 ld hl,$5b15
 bit 1,e
 jr nz,key_up_21
 ld (hl),1
 ld a,$60
 jr key_color_21
key_up_21:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_21
 ld a,$68
key_color_21:
 ld hl,$58b8
 ld b,2
 ld iy,key_painted_21_0
 jp keyboard_paint
key_painted_21_0:
 ld hl,$5b16
 bit 2,e
 jr nz,key_up_22
 ld (hl),1
 ld a,$60
 jr key_color_22
key_up_22:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_22
 ld a,$68
key_color_22:
 ld hl,$58b5
 ld b,2
 ld iy,key_painted_22_0
 jp keyboard_paint
key_painted_22_0:
 ld hl,$5b17
 bit 3,e
 jr nz,key_up_23
 ld (hl),1
 ld a,$60
 jr key_color_23
key_up_23:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_23
 ld a,$68
key_color_23:
 ld hl,$58b2
 ld b,2
 ld iy,key_painted_23_0
 jp keyboard_paint
key_painted_23_0:
 ld hl,$5b18
 bit 4,e
 jr nz,key_up_24
 ld (hl),1
 ld a,$60
 jr key_color_24
key_up_24:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_24
 ld a,$68
key_color_24:
 ld hl,$58af
 ld b,2
 ld iy,key_painted_24_0
 jp keyboard_paint
key_painted_24_0:
 ld bc,$dffe
 in a,(c)
 ld e,a
 ld hl,$5b19
 bit 0,e
 jr nz,key_up_25
 ld (hl),1
 ld a,$60
 jr key_color_25
key_up_25:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_25
 ld a,$68
key_color_25:
 ld hl,$591c
 ld b,2
 ld iy,key_painted_25_0
 jp keyboard_paint
key_painted_25_0:
 ld hl,$5b1a
 bit 1,e
 jr nz,key_up_26
 ld (hl),1
 ld a,$60
 jr key_color_26
key_up_26:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_26
 ld a,$68
key_color_26:
 ld hl,$5919
 ld b,2
 ld iy,key_painted_26_0
 jp keyboard_paint
key_painted_26_0:
 ld hl,$5b1b
 bit 2,e
 jr nz,key_up_27
 ld (hl),1
 ld a,$60
 jr key_color_27
key_up_27:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_27
 ld a,$68
key_color_27:
 ld hl,$5916
 ld b,2
 ld iy,key_painted_27_0
 jp keyboard_paint
key_painted_27_0:
 ld hl,$5b1c
 bit 3,e
 jr nz,key_up_28
 ld (hl),1
 ld a,$60
 jr key_color_28
key_up_28:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_28
 ld a,$68
key_color_28:
 ld hl,$5913
 ld b,2
 ld iy,key_painted_28_0
 jp keyboard_paint
key_painted_28_0:
 ld hl,$5b1d
 bit 4,e
 jr nz,key_up_29
 ld (hl),1
 ld a,$60
 jr key_color_29
key_up_29:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_29
 ld a,$68
key_color_29:
 ld hl,$5910
 ld b,2
 ld iy,key_painted_29_0
 jp keyboard_paint
key_painted_29_0:
 ld bc,$bffe
 in a,(c)
 ld e,a
 ld hl,$5b1e
 bit 0,e
 jr nz,key_up_30
 ld (hl),1
 ld a,$60
 jr key_color_30
key_up_30:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_30
 ld a,$68
key_color_30:
 ld hl,$597d
 ld b,3
 ld iy,key_painted_30_0
 jp keyboard_paint
key_painted_30_0:
 ld hl,$5b1f
 bit 1,e
 jr nz,key_up_31
 ld (hl),1
 ld a,$60
 jr key_color_31
key_up_31:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_31
 ld a,$68
key_color_31:
 ld hl,$597a
 ld b,2
 ld iy,key_painted_31_0
 jp keyboard_paint
key_painted_31_0:
 ld hl,$5b20
 bit 2,e
 jr nz,key_up_32
 ld (hl),1
 ld a,$60
 jr key_color_32
key_up_32:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_32
 ld a,$68
key_color_32:
 ld hl,$5977
 ld b,2
 ld iy,key_painted_32_0
 jp keyboard_paint
key_painted_32_0:
 ld hl,$5b21
 bit 3,e
 jr nz,key_up_33
 ld (hl),1
 ld a,$60
 jr key_color_33
key_up_33:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_33
 ld a,$68
key_color_33:
 ld hl,$5974
 ld b,2
 ld iy,key_painted_33_0
 jp keyboard_paint
key_painted_33_0:
 ld hl,$5b22
 bit 4,e
 jr nz,key_up_34
 ld (hl),1
 ld a,$60
 jr key_color_34
key_up_34:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_34
 ld a,$68
key_color_34:
 ld hl,$5971
 ld b,2
 ld iy,key_painted_34_0
 jp keyboard_paint
key_painted_34_0:
 ld bc,$7ffe
 in a,(c)
 ld e,a
 ld hl,$5b23
 bit 0,e
 jr nz,key_up_35
 ld (hl),1
 ld a,$60
 jr key_color_35
key_up_35:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_35
 ld a,$68
key_color_35:
 ld hl,$5a27
 ld b,18
 ld iy,key_painted_35_0
 jp keyboard_paint
key_painted_35_0:
 ld hl,$5b24
 bit 1,e
 jr nz,key_up_36
 ld (hl),1
 ld a,$60
 jr key_color_36
key_up_36:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_36
 ld a,$68
key_color_36:
 ld hl,$59d8
 ld b,3
 ld iy,key_painted_36_0
 jp keyboard_paint
key_painted_36_0:
 ld hl,$5b25
 bit 2,e
 jr nz,key_up_37
 ld (hl),1
 ld a,$60
 jr key_color_37
key_up_37:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_37
 ld a,$68
key_color_37:
 ld hl,$59d5
 ld b,2
 ld iy,key_painted_37_0
 jp keyboard_paint
key_painted_37_0:
 ld hl,$5b26
 bit 3,e
 jr nz,key_up_38
 ld (hl),1
 ld a,$60
 jr key_color_38
key_up_38:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_38
 ld a,$68
key_color_38:
 ld hl,$59d2
 ld b,2
 ld iy,key_painted_38_0
 jp keyboard_paint
key_painted_38_0:
 ld hl,$5b27
 bit 4,e
 jr nz,key_up_39
 ld (hl),1
 ld a,$60
 jr key_color_39
key_up_39:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_39
 ld a,$68
key_color_39:
 ld hl,$59cf
 ld b,2
 ld iy,key_painted_39_0
 jp keyboard_paint
key_painted_39_0:
 ld bc,$fefe
 in a,(c)
 bit 0,a
 jr nz,break_up
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jr nz,break_up
 ld hl,$5b28
 ld (hl),1
 ld a,$60
 jr break_color
break_up:
 ld hl,$5b28
 bit 0,(hl)
 ld a,$78
 jr z,break_color
 ld a,$68
break_color:
 ld hl,$59db
 ld b,2
 ld iy,keyboard_break_done
 jp keyboard_paint
keyboard_break_done:
