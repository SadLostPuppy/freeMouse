import ctypes
from ctypes import wintypes

# Define user32 and kernel32
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Key event constants
vk_lalt = 0xA4  # Virtual key code for Left Alt


def release_cursor():
    """
    Explicitly release the cursor by calling ClipCursor with None.
    """
    user32.ClipCursor(None)


def remove_all_focus():
    print("Lost focus: Alt key pressed")
    """
    Remove focus from all windows, ensuring no window is focused.
    """
    user32.SetFocus(None)
    # print("Alt key pressed: All window focus removed.")


def set_hook():
    """
    Set a low-level keyboard hook to detect when Left Alt is held down.
    """
    wh_mouse_ll = 14
    hc_action = 0

    # Define the hook procedure pointer
    def low_level_mouse_proc(n_code, w_param, l_param):
        # If the mouse event is being processed
        if n_code == hc_action and l_param is not None:
            # Check if Left Alt is being held down
            if user32.GetAsyncKeyState(vk_lalt) & 0x8000:
                # If Left Alt is held down, release the cursor lock and remove all focus
                release_cursor()
                remove_all_focus()

        # Call the next hook in the chain
        return ctypes.windll.user32.CallNextHookEx(hook_id, n_code, w_param, ctypes.cast(l_param, ctypes.c_void_p))

    # Define the hook procedure pointer
    cmp_func = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    pointer = cmp_func(low_level_mouse_proc)

    # Set the hook globally (module_handle = 0)
    hook_id = user32.SetWindowsHookExW(wh_mouse_ll, pointer, 0, 0)
    if not hook_id:
        error_code = kernel32.GetLastError()
        raise ctypes.WinError(error_code)

    # Keep the hook running
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
        # Log which window received focus after Alt key press
        focused_window = user32.GetForegroundWindow()
        window_text = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(focused_window, window_text, 512)
        print(f"Restored focus in: {window_text.value}")


if __name__ == "__main__":
    try:
        set_hook()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
