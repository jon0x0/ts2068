# Public release console font

Source: https://github.com/dhepper/font8x8/blob/master/font8x8_basic.h

Daniel Hepper's basic Latin font is explicitly dedicated to the public domain
in its source header, with attribution to Marcel Sondaar and IBM VGA fonts.
The header is retained unchanged. tools/public_font.py selects characters 32–127
and reverses row bit order for the TS2068 bitmap console. Public downloads use
this font rather than bytes extracted from a HOME ROM.
