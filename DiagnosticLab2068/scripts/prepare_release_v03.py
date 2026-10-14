"""Refresh public release wording without changing firmware or old snapshots."""
from pathlib import Path
from release_info import VERSION, RELEASE_DATE_DISPLAY
root=Path(__file__).resolve().parents[1]
p=root/'README.md'
s=p.read_text(encoding='utf-8').replace('Release v0.2 | October 12, 2026',f'Release {VERSION} | {RELEASE_DATE_DISPLAY}')
s=s.replace('TS2068DiagnosticLab-v0.2.zip',f'TS2068DiagnosticLab-{VERSION}.zip').replace('TS2068DiagnosticLab-v0.2-HOME-ROM.zip',f'TS2068DiagnosticLab-{VERSION}-HOME-ROM.zip')
p.write_text(s,encoding='utf-8')
p=root/'scripts/build_manual.py';s=p.read_text(encoding='utf-8').replace('v0.2',VERSION).replace('October 12, 2026',RELEASE_DATE_DISPLAY)
for old,new in [('despite37','despite 37'),('over5F00','over 5F00'),('near5ED0','near 5ED0'),('MainL','Main L'),('option3','option 3'),('option4','option 4'),('option6','option 6'),('option7','option 7'),('names60Hz','names 60 Hz'),('in6 seconds','in 6 seconds'),('checked00','checked 00'),('logic+5V','logic +5 V'),('compensated10x','compensated 10x'),('section2.1.2','section 2.1.2'),('specifies4.75-5.25V','specifies 4.75-5.25 V'),('above4.75V','above 4.75 V'),('the6-second','the 6-second'),('Compare20MHz','Compare 20 MHz')]:
    s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
p=root/'scripts/prepare_github_publication.py';s=p.read_text(encoding='utf-8').replace('v0.2',VERSION).replace('October 12, 2026',RELEASE_DATE_DISPLAY)
s=s.replace("anchor='| AI skill |'", "text='\\n'.join(line for line in text.split('\\n') if not line.startswith('| TS2068 Diagnostic Lab |'))\nanchor='| AI skill |'") if "if not line.startswith('| TS2068 Diagnostic Lab |')" not in s else s
s=s.replace('anchor="    \'Development tools\': [\\n"', 'text="\\n".join(line for line in text.split("\\n") if "(\'TS2068 Diagnostic Lab\'," not in line)\nanchor="    \'Development tools\': [\\n"') if 'if "(\'TS2068 Diagnostic Lab\'," not in line' not in s else s
# Preserve referenced evidence hashes rather than relabelling old checkpoints.
s=s.replace("for name in ['diagnostic-v02.dck'", "for folder_name in ['load-'+json.loads((ROOT/'build/manifest-v02.json').read_text())['dck_sha256'][:12]]:\n    shutil.copytree(ROOT/'docs/validation'/folder_name,DEST/'docs/validation'/folder_name,dirs_exist_ok=True)\nfor name in ['diagnostic-v02.dck'",1) if 'for folder_name in' not in s else s
p.write_text(s,encoding='utf-8')
(root/'docs/RELEASE_POST.txt').write_text(f'''TS2068 Diagnostic Lab cartridge {VERSION} - {RELEASE_DATE_DISPLAY}

This release adds configurable mixed-load and quiet/busy power-cycle tests:
RAM/March, normal/ECM/hires video, 60 Hz IRQ, banking, stronger AY/envelope/beeper
activity and stack-data comparisons. Main L/P selects combined loads; choose
N one batch or C continuous, then S. Genuine IM1/IM2 returns use separate R
confirmation and fresh prerequisites. The running screen explains the6-second
notice. Soak notices remain readable for6 seconds.

Transient read/POP reports now retain the original observed byte, with checked
D0-D7 and multi-bit masks in all RAM regions. The motivating Sinistar D1-loss
incident is a supplied report, not a physically reproduced result.

The updated PDF/offline manual and POWER_LOAD_TROUBLESHOOTING.md explain why
load transitions matter, how to inspect the5 V rail with an oscilloscope and
how to separate supply hypotheses from RAM/refresh/timing faults.

Images and checksums are emulator validated. Physical supply/current/thermal
validation remains pending. HOME U16 retains reduced coverage without L.
Internal diagnostic-v02 filenames are retained for build/tool compatibility;
the public release archives and manifests identify {VERSION}.
''',encoding='utf-8')
