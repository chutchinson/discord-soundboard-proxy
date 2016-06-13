"""
Global key binding hooks for the win32 platform.
"""

import ctypes
import ctypes.wintypes
import collections
import atexit

__author__ = 'Chris Hutchinson'
__version__ = '0.0.1'

byref = ctypes.byref
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

_hooks = []
_hook_delegate = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
_hook_modifiers = []
_hook_key_map = {
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4a,
    'k': 0x4b, 'l': 0x4c, 'm': 0x4d, 'n': 0x4e, 'o': 0x4f, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5a,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12,
    'esc': 0x18, 'pgup': 0x21, 'pgdn': 0x22, 'end': 0x23, 'home': 0x24,
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'n0': 0x60, 'n1': 0x61, 'n2': 0x63, 'n3': 0x64, 'n5': 0x65, 'n6': 0x66, 'n7': 0x67, 'n8': 0x68, 'n9': 0x69,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78,
    'f10': 0x79, 'f11': 0x80, 'f12': 0x81
}

# win32 constants

WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104


# wraps KBDLLHOOKSTRUCT
# see https://msdn.microsoft.com/en-us/library/ms644967.aspx

class NativeKeyboardEvent(ctypes.Structure):
    _fields_ = (
        ('vkcode', ctypes.wintypes.DWORD),
        ('scancode', ctypes.wintypes.DWORD),
        ('flags', ctypes.wintypes.DWORD),
        ('extra', ctypes.wintypes.PULONG)
    )


def _hook_modifier(event, key):

    modifier = None

    # pool all of the key modifiers into a subset
    # to make detection easier; not ideal
    # but satisfies laziness

    if key == 0xa0 or key == 0xa1 or key == 0x10:
        modifier = 0x10
    elif key == 0xa2 or key == 0xa3 or key == 0x11:
        modifier = 0x11
    elif key == 0xa4 or key == 0xa5 or key == 0x12:
        modifier = 0x12

    # ensure a key was reduced to a valid modifier
    # and that modifiers only exist once in the
    # modifier list

    if modifier is not None:
        if event == WM_KEYDOWN or event == WM_SYSKEYDOWN:
            if modifier not in _hook_modifiers:
                _hook_modifiers.append(modifier)
        elif event == WM_KEYUP or event == WM_SYSKEYUP:
            if modifier in _hook_modifiers:
                _hook_modifiers.remove(modifier)
        return True

    return False


def _hook(code, wparam, lparam):

    """
    Global low-level keyboard hook procedure
    :see https://msdn.microsoft.com/en-us/library/ms644985.aspx
    """

    if code < 0:
        return user32.CallNextHookEx(None, code, wparam, lparam)
    else:
        evptr = ctypes.cast(lparam, ctypes.POINTER(NativeKeyboardEvent))
        ev = evptr.contents
        if not _hook_modifier(wparam, ev.vkcode):
            for hook in _hooks:
                hook.post(wparam, ev.vkcode, _hook_modifiers)
        return user32.CallNextHookEx(None, code, wparam, lparam)

_hook_fn = _hook_delegate(_hook)


class GlobalHookManager:

    """
    Manages a low-level keyboard hook with the operating system,
    and matches key bindings with callbacks.
    """

    class Registration:

        def __init__(self, pattern, fn):
            self.key = None
            self.modifiers = []
            self.handler = fn
            self._parse_pattern(pattern)

        def _parse_pattern(self, pattern):
            keys = pattern.split('+')
            for key in keys:
                if key not in _hook_key_map:
                    raise ValueError("key %s not recognized for use in hook pattern" % key)
                if key == 'shift' or key == 'ctrl' or key == 'alt':
                    modifier = _hook_key_map[key]
                    if modifier not in self.modifiers:
                        self.modifiers.append(modifier)
                else:
                    self.key = _hook_key_map[key]

        def call(self, key, modifiers):
            if self.matches(key, modifiers):
                self.handler()

        def matches(self, key, modifiers):
            if self.key is None:
                return True
            if self.key == key and self.modifiers == modifiers:
                return True
            else:
                return False

    @staticmethod
    def __register_hook():

        """
        Registers a low-level keyboard hook with the operating system
        and also registers a callback with `atexit` to ensure the
        hook is removed to avoid problems.

        :return: operating system hook id
        """

        handle = kernel32.GetModuleHandleA(None)
        hkid = user32.SetWindowsHookExA(13, _hook_fn, handle, 0)
        if hkid != 0:
            atexit.register(user32.UnhookWindowsHookEx, hkid)
        return hkid

    @staticmethod
    def poll():
        msg = ctypes.wintypes.MSG()
        user32.WaitMessage()
        while user32.PeekMessageA(byref(msg), None, 0, 0, 0x0001) != 0:
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageA(byref(msg))

    def __init__(self):
        self.registrations = collections.defaultdict(list)
        self.registrations[WM_KEYDOWN] = list()
        self.registrations[WM_KEYUP] = list()
        self.hook_id = self.__register_hook()
        if self.hook_id != 0:
            _hooks.append(self)

    def __del__(self):
        if self.hook_id != 0:
            _hooks.remove(self)
            user32.UnhookWindowsHookEx(self.hook_id)

    def post(self, event, key, modifiers):
        for registration in self.registrations[event]:
            registration.call(key, modifiers)

    def register(self, event, pattern, fn):
        self.registrations[event].append(
            self.Registration(pattern, fn))

    def keyup(self, pattern=None):

        """
        Decorator for registering a key released binding.

        :param pattern: key-binding pattern (e.g. ctrl+shift+a)
        :return: decorator
        """

        def decorator(fn):
            self.register(WM_KEYUP, pattern, fn)
            return fn
        return decorator

    def keydown(self, pattern=None):

        """
        Decorator for registering a key pressed binding.

        :param pattern: key-binding pattern (e.g. ctrl+shift+a)
        :return: decorator
        """

        def decorator(fn):
            self.register(WM_KEYDOWN, pattern, fn)
            return fn
        return decorator