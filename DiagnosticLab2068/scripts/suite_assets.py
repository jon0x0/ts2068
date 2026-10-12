"""Immutable UI and PackBits asset generation for the ROM suite."""
from pathlib import Path
import re
from generate_design_assets import offset

def pack(data):
    out=bytearray();i=0
    while i<len(data):
        n=1
        while i+n<len(data) and data[i+n]==data[i] and n<128:n+=1
        if n>=3:out.extend([128+n-1,data[i]]);i+=n
        else:
            start=i;i+=n
            while i<len(data) and i-start<128:
                n=1
                while i+n<len(data) and data[i+n]==data[i] and n<3:n+=1
                if n>=3:break
                i+=min(n,128-(i-start))
            out.append(i-start-1);out.extend(data[start:i])
    check=bytearray();i=0
    while i<len(out):
        a=out[i];i+=1;n=(a&127)+1
        if a&128:check.extend([out[i]]*n);i+=1
        else:check.extend(out[i:i+n]);i+=n
    assert check==data
    return bytes(out)

def pages(font):
    def display_text(value):
        # Font already contains ASCII32-127, including lowercase. Keep physical
        # keys, hardware identifiers and author spelling; sentence-case prose.
        keep={'TS2068','Z80','CPU','SCLD','RAM','ROM','ROM0','HOME','EXROM',
              'CRC32','AY','HSR','IRQ','IX','IY','EAR','U6','U7','U12','U13',
              'U16','U17','U18','U20','R0','R13','FF','AA','PASS','CAPS','ENTER'}
        def segment(part):
            first=True
            def word(match):
                nonlocal first
                text=match[0]
                result=text if len(text)==1 or text in keep or not text.isupper() else text.lower()
                if first: result=result[:1].upper()+result[1:]
                first=False
                return result
            return re.sub(r'[A-Za-z][A-Za-z0-9]*',word,part)
        return '/'.join(segment(p) for p in value.split('/'))
    def page(title,lines,footer='M  MENU',status='ROM CONTROL / HOME DISPLAY',bottom='MENU: M / TEST: ANY KEY'):
        pix=bytearray(6144);attrs=bytearray([0x47]*768)
        def text(row,col,value,attr=0x47):
            value=display_text(value)
            assert col+len(value)<=32,(row,col,value)
            for x,ch in enumerate(value,col):
                for y in range(8):pix[offset(x,row*8+y)]=font[(ord(ch)-32)*8+y]
                attrs[row*32+x]=attr
        attrs[:96]=bytes([0x4d])*96
        text(0,1,'TS2068 / DIAGNOSTIC LAB',0x4d);text(2,1,title,0x4f);text(4,1,status,0x45)
        for row,value in lines:
            text(row,1,value,0x47)
            if value[:1].isdigit():attrs[row*32+1:row*32+3]=bytes([0x46])*2
        attrs[22*32:]=bytes([0x4d])*64
        text(22,1,footer,0x4f);text(23,1,bottom,0x4d)
        for x in range(32):pix[offset(x,31)]=255
        return bytes(pix+attrs)
    out={
    'fullinfo':page('Full test / coverage',[(6,'Automatic: all 48K RAM'),(7,'Patterns/March/address/random'),(8,'Retention + 100 bank cycles'),(9,'AY R0-R13 masked readback'),(11,'You judge: beeper + AY sounds'),(12,'Six video cards + every key'),(14,'Matched is not a whole-PC PASS'),(15,'~4 min to keys / ~8 min total'),(16,'Not run: ROM CRC / IRQ'),(17,'Optional CPU / overnight / ext'),(19,'1  Start the full sequence'),(20,'M  Return without running')],footer='1 START / M MENU',bottom='DIGITAL + OBSERVED RESULTS'),
    'fullsummary':page('Full sequence / completed',[(6,'Automatic comparisons matched:'),(7,'48K RAM / 100 bank cycles / AY'),(9,'Still needs your judgement:'),(10,'Beeper / AY sound / all keys'),(11,'Colors / BRIGHT / FLASH / modes'),(13,'Outputs are not read back'),(14,'Unseen/unpressed is not passed'),(16,'Not run: ROM CRC / IRQ'),(17,'Optional CPU / overnight / ext'),(19,'Repeat single tests to inspect'),(20,'Reset/startup CPU is separate')],status='DIGITAL MATCH / REVIEW OUTPUTS',footer='ANY NEW KEY RETURNS TO MENU',bottom='NO AUTOMATIC WHOLE-MACHINE PASS'),
    'cpuinfo':page('Z80 / HOW TO COUNT THE BEEPS',[(5,'Two groups of counting beeps:'),(6,'8 beeps / pause / stage count'),(7,'Example: 8 then 3 = shifts'),(9,'Once = starting that stage'),(10,'Repeats = comparison failed'),(12,'1 Registers / 2 Arithmetic'),(13,'3 Shifts / 4 Alternate regs'),(14,'5 IX/IY / 6 Address checks'),(16,'Address fault: 9 then 1-16'),(17,'1=A0, 2=A1 ... 16=A15'),(19,'Success shows PASS'),(20,'Silence/stall is inconclusive')],status='CPU RUN ~80 SEC / BEEP GUIDE',footer='NEW KEY EXITS REPEATED CODES',bottom='EACH COUNTING BEEP ~0.6 SEC'),
    'startupquick':page('POWER-ON / QUICK RAM CHECK',[(6,'00 / FF CHECK / ALL 48K'),(8,'HOLD R=RAM / F=FULL AT POWER'),(10,'Release keys; new key stops'),(12,'Screen RAM is being tested'),(14,'BLUE patterns / CYAN bits'),(15,'YELLOW March / MAGENTA addr'),(16,'GREEN random / RED retention'),(18,'BOOT CPU / 55-AA ADDRESS PAIRS'),(20,'Errors use chip text + pulses')],footer='QUICK CHECK IS LIMITED'),
    'startupfull':page('POWER-ON / EXTENDED TESTS',[(6,'R  COMPLETE RAM ~1.5 MIN'),(8,'F  FULL ~4 MIN TO KEYS'),(10,'Release held key; new key stops'),(12,'Screen RAM is being tested'),(14,'BLUE patterns / CYAN bits'),(15,'YELLOW March / MAGENTA addr'),(16,'GREEN random / RED retention'),(18,'Selected test is highlighted'),(20,'~8 min with keyboard timeout')],footer='RAM / BANK / AUDIO / VIDEO'),
    'menu':page('READY / SELECT A TEST',[(6,'1  FULL DIGITAL + GUIDED TEST'),(7,'2  RAM / RANDOM / RETENTION'),(8,'3  VIDEO / COLORS / MODES'),(9,'4  KEYBOARD / LIVE MATRIX'),(10,'5  BEEPER / AY SOUND'),(11,'6  BANK SWITCH STRESS'),(12,'7  OVERNIGHT RAM SOAK'),(13,'8  OPTIONAL ROM CHECKSUMS'),(14,'9  CPU / SCLD OPTIONAL TESTS'),(16,'0  HELP / CREDITS'),(17,'J  JOYSTICKS / EAR INPUTS'),(18,'STARTUP CHECK IS LIMITED'),(20,'RAM: QUICK START / FULL IN MENU')],footer='PRESS A NUMBER TO OPEN'),
    'rammenu':page('RAM / SELECT COVERAGE',[(6,'1  COMPLETE ~84 SEC'),(8,'2  PATTERNS / BITS ~41 SEC'),(10,'3  MARCH C- ~8 SEC'),(12,'4  ADDRESS DATA ~8 SEC'),(14,'5  SEEDED RANDOM ~3 SEC'),(16,'6  WRITE/HOLD/READ ~24 SEC'),(18,'Can identify failing RAM chips'),(19,'Any new key stops the sweep')]),
    'videomenu':page('VIDEO / SELECT A PATTERN',[(6,'1  COLOR BARS / BRIGHT'),(8,'2  NORMAL / FLASH / BIT LANES'),(10,'3  SECOND DISPLAY FILE'),(12,'4  EXTENDED COLOR / DITHER'),(14,'5  512 PIXEL CALIBRATION'),(16,'6  128 ATTRIBUTE MIXES'),(19,'Visual tests need observation'),(20,'128 mixes are not 128 colors')]),
    'soundmenu':page('AUDIO / LISTEN AND COMPARE',[(7,'1  BEEPER / THREE TONES'),(10,'2  AY REGISTERS + A/B/C'),(14,'Register reads test data only'),(16,'Sound requires your judgement'),(19,'All exits silence the AY')]),
    'rommenu':page('ROM / OPTIONAL EXPOSED TEST',[(6,'H  HOME U16 / 16K CRC32'),(8,'E  EXROM U20 / 8K CRC32'),(11,'Stock HOME:  BF44EC3F'),(12,'Stock EXROM: AE16233A'),(15,'Nonstandard is not proof bad'),(17,'HOME runs from high ROM'),(18,'EXROM runs a checked gateway'),(20,'Opcode faults can stop these')]),
    'irqmenu':page('CPU / SCLD / OPTIONAL TESTS',[(6,'I  IRQ INHIBIT + ARRIVAL'),(8,'U  CPU / ADDRESS ALIAS TEST'),(11,'CPU progress: 8, pause, stage'),(12,'Repeating code means failure'),(14,'Example: 8 then 3 = shifts'),(16,'U opens the beep-code guide'),(18,'Success shows PASS'),(20,'No sound/stall is inconclusive')]),
    'soak':page('OVERNIGHT / REPEATED RAM',[(7,'Every pass covers all 48K'),(9,'Patterns / March / random'),(11,'Address data / retention'),(12,'~1.5 min per pass'),(13,'Repeats until stopped'),(14,'PASS COUNT:'),(17,'First mismatch stops the soak'),(19,'Border color identifies phase'),(20,'Press any key to stop')]),
    'soakstop':page('RAM SOAK / STOPPED',[(7,'No failures during the test'),(10,'Completed passes (hex):'),(14,'Count:'),(19,'Covered comparisons only'),(20,'Press a new key for the menu')],status='STOPPED / NO FAILURES'),
    'bank':page('BANKING / TORTURE LOOP',[(7,'HSR bits 1-7 / combinations'),(9,'HOME write isolation checks'),(11,'ROM0 stays resident'),(14,'PASS COUNT:'),(17,'Any new key stops; faults latch'),(19,'Cannot recover lost ROM fetch')]),
    'rampass':page('ALL 6 RAM CHIPS PASS',[(6,'All 48K comparisons matched'),(8,'U6 U7 U12 U13 U17 U18'),(10,'All tested patterns completed'),(12,'Faults: chip text + sound code'),(14,'Wiring can mimic a failed chip'),(16,'No long-term fault guarantee'),(20,'Press any key for the menu')],status='RESULT / COMPLETE RAM'),
    'pass':page('SELECTED CHECKS PASS',[(8,'Selected comparisons matched'),(12,'Covers this test on this run'),(16,'Press any key for the menu')],status='RESULT / TEST COMPLETE'),
    'fail':page('MISMATCH / SUSPECT PATH',[(7,'A digital comparison failed'),(10,'Capture this result and code'),(14,'DETAIL:'),(15,'ADDRESS:'),(17,'REGISTER/PHASE:'),(18,'Shared bus / decode possible'),(20,'Any key returns to the menu')],status='RESULT / MISMATCH'),
    'romresult':page('ROM / MEASURED CRC32',[(7,'CRC32:'),(10,'STOCK:'),(14,'Match compares the full image'),(17,'Different can mean modified'),(19,'Any key returns to the menu')],status='RESULT / IDENTITY'),
    'beeper':page('BEEPER / LOW MID HIGH',[(8,'Listen for three tones'),(9,'About 15 seconds total'),(11,'LOW red / MID magenta'),(12,'HIGH green'),(15,'Silence cannot be read back'),(18,'Any new key stops; returns')]),
    'aylisten':page('AY / LISTEN AND COMPARE',[(5,'R0-R13 READBACK MATCHED'),(6,'A: LOW   MID     HIGH    TOP'),(8,'B: LOW   MID     HIGH    TOP'),(10,'C: LOW   MID     HIGH    TOP'),(12,'VOLUME: LOW     MID     MAX'),(14,'NOISE:  LOW     MID     HIGH'),(15,'ENVELOPE SHAPES'),(16,'DOWN    UP      TRI     SAW'),(18,'CHORD           SILENCE'),(20,'ACTIVE STEP IS YELLOW'),(21,'........................')],footer='ANY NEW KEY STOPS AND MUTES',status='ABOUT 22 SECONDS / 24 STEPS'),
    'help':page('HELP / SOURCES',[(6,'Passive boot needs HOME ROM'),(8,'Reports: sync / 2 / chip / bit'),(9,'Chips: U6 U7 U12 U13 U17 U18'),(10,'Bits: 1-4; 5 means multiple'),(11,'3 CART 4 BANK 5 AY 6 CODE 7 IRQ'),(12,'Timex manual + schematic'),(13,'Carl Miles / ZX diagnostics'),(14,'128 Colors: Mark Miller'),(15,'TSRun: Josef Jelinek'),(16,'Fuse / SjASMPlus contributors'),(18,'P  EAR / JOYSTICK INPUTS'),(20,'C  FAULT CODES / EXAMPLES')]),
    'soundguide':page('FAULT CODES / TRAINING',[(5,'RAM: long sync / 2 / chip / bit'),(6,'Chips: U6 U7 U12 U13 U17 U18'),(7,'Bit: 1-4; 5 means multiple'),(9,'1  RAM: SYNC / 2 / 6 / 2'),(10,'   U18 PATH / D5 EXAMPLE'),(12,'2  BANK: 4 PULSES'),(13,'3  CPU: 8 / 3 (SHIFT STAGE)'),(15,'3 CART 4 BANK 5 AY 6 CODE 7 IRQ'),(17,'8 + STAGE CPU / 9 + BIT ADDRESS'),(19,'Examples are not failures'),(20,'Listen, then choose or return')],footer='1-3 LISTEN / M RETURNS TO HELP'),
    'inputs':page('INPUTS / EAR + JOYSTICKS',[(7,'EAR HIGH/LOW:'),(10,'JOY 1 RAW:'),(12,'JOY 2 RAW:'),(16,'Input levels / user observation'),(18,'No tape decoding or loopback'),(20,'Any key returns to the menu')]),
    }
    # Two spatial direction pads; all five signals are highlighted independently.
    joy_lines=[(6,'Port 1          Port 2'),(7,'RAW:            RAW:')]
    for cy,placements in [(8,[(5,'^ Up  ')]),(11,[(1,'< Left'),(9,'Right>')]),(14,[(5,'v Down')]),(17,[(5,' FIRE ')])]:
        cells=[' ']*32
        for cx,label in placements:
            for player in (0,16): cells[cx+player:cx+player+len(label)]=label
        joy_lines.append((cy,''.join(cells)[1:].rstrip()))
    joy_lines.extend([(19,'Green now / cyan tested'),(20,'EAR raw:'),(21,'White unseen / all combinations')])
    out['inputs']=page('JOYSTICKS / LIVE INPUTS',joy_lines,status='MOVE / FIRE BOTH JOYSTICKS',footer='PRESS ANY KEY TO RETURN',bottom='RAW FF = NO CONTACTS ACTIVE')
    out['keyboard']=page('KEYBOARD / PHYSICAL LAYOUT',[(19,'Green held / cyan released'),(20,'Art: Josef Jelinek / TSRun'),(21,'Both CAPS share one contact')],footer='HOLD CAPS+SPACE OR ENTER+SPACE',status='PRESS KEYS / TIMEOUT ~4 MIN',bottom='WHITE UNSEEN / HOLD EXIT CHORD')
    pix=bytearray(out['keyboard'][:6144]);attrs=bytearray(out['keyboard'][6144:]);coords={}
    from keyboard_art import draw_keyboard
    coords=draw_keyboard(pix,attrs,font)
    out['keyboard']=bytes(pix+attrs)
    return out,coords







