assembly_cache_call:
 di
 ld c,a
 ld a,($78df)
 ld iyl,a
 ld a,$18
 out ($f4),a
 jp assembly_cache_source
assembly_cache_return:
 ld sp,($5bd5)
 ld a,($5bda)
 out ($f4),a
 ei
 ret
