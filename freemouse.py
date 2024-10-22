import ctypes
from ctypes import wintypes

hook_id = None


def remove_clip_cursor():
    """
    This function releases the mouse cursor if it is confined.
    """
    ctypes.windll.user32.ClipCursor(None)


def set_hook():
    """
    Set a low-level mouse hook to detect when applications try to confine the cursor.
    """
    global hook_id
    wh_mouse_ll = 14
    hc_action = 0

    # Define the hook procedure pointer
    def low_level_mouse_proc(n_code, w_param, l_param):
        # If the mouse event is being processed
        if n_code == hc_action:
            # Remove any cursor clipping
            remove_clip_cursor()
        # Call the next hook in the chain
        return ctypes.windll.user32.CallNextHookEx(hook_id, n_code, w_param, ctypes.cast(l_param, ctypes.c_void_p))

    # Define the hook procedure pointer
    cmp_func = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    pointer = cmp_func(low_level_mouse_proc)

    # Set the hook globally (module_handle = 0)
    user32 = ctypes.windll.user32
    hook_id = user32.SetWindowsHookExW(wh_mouse_ll, pointer, 0, 0)
    if not hook_id:
        error_code = ctypes.get_last_error()
        print(f"Failed to set hook. Error code: {error_code}")
        raise ctypes.WinError(error_code)
    else:
        print(f"Hook set successfully with hook ID: {hook_id}")

    # Keep the hook running
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


if __name__ == "__main__":
    try:
        set_hook()
    except KeyboardInterrupt:
        print("\nExiting...")
        if hook_id:
            try:
                ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
            except Exception as e:
                print(f"Error unhooking: {e}")
    except Exception as e:
        print(f"Error: {e}")
