"""One source of truth for tested stock motion ports and unpublished experiments."""
import os
READY_LEVELS=(2,3,5,6,7,8)
def enabled(level):
 return os.environ.get('STOCK_TAP_MOTION','1')=='1'and(level in READY_LEVELS or(level==4 and (os.environ.get('STOCK_L4_MOTION_EXPERIMENT')=='1'or procedural_enabled(level))))

def composition_enabled(level):
 return level==5 and os.environ.get('STOCK_L5_COMPOSITION','1')=='1'

def composition_slots(level):
 return 256 if os.environ.get('STOCK_COMPACT_PALETTE')=='1' else 192

def compact_snapshot_enabled(level):
 return level==7 or procedural_enabled(level) or(composition_enabled(level)and os.environ.get('STOCK_COMPACT_PALETTE')=='1')

def procedural_enabled(level):
 return level==4 and os.environ.get('STOCK_TAP_MOTION','1')=='1'and os.environ.get('STOCK_L4_PROCEDURAL','1')=='1'
