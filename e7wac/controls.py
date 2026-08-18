import msvcrt

_is_paused = False
_stop_requested = False

def check_controls():
    global _is_paused, _stop_requested
    while msvcrt.kbhit():
        char = msvcrt.getch()
        if char.lower() == b'p':
            _is_paused = not _is_paused
            if _is_paused:
                print("\n" + "="*60 + "\nSCAN PAUSED\n" + "="*60)
                print("Press P to resume\nPress Ctrl+C to stop and save\n" + "="*60)
            else:
                print("\n" + "="*60 + "\nSCAN RESUMED\n" + "="*60)
                
def is_paused():
    return _is_paused
