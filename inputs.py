from pygame import (
    K_0,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_7,
    K_8,
    K_9,
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_LSHIFT,
    K_RIGHT,
    K_SPACE,
    K_UP,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    QUIT,
    K_a,
    K_c,
    K_d,
    K_i,
    K_k,
    K_p,
    K_s,
    K_t,
    K_w,
    mouse,
    key,
    event,
)

NUMBER_KEYS = [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0]

JUMP = K_w
LEFT = K_a
RIGHT = K_d
FAST = K_LSHIFT
SLOW = K_s
PAUSE = K_p

CAM_LEFT = K_LEFT
CAM_RIGHT = K_RIGHT
CAM_UP = K_UP
CAM_DOWN = K_DOWN

CAMERA_TOGGLE = K_c
TELEPORT = K_t
CLONE = K_i
SAVE = K_k
FLY = K_SPACE

EXIT = K_ESCAPE


def handle_keys():
    quit_game = False
    keydown = False
    jump = False
    camera_toggle = False
    teleport = False
    clone = False
    save = False
    mouse_button = 0
    mouse_button_down = False
    number_key = 0
    pause = False
    fly_toggle = False

    for e in event.get():
        quit_game = e.type == QUIT
        if e.type == KEYDOWN:
            keydown = True
            quit_game = e.key == EXIT
            jump = e.key == JUMP
            camera_toggle = e.key == CAMERA_TOGGLE
            teleport = e.key == TELEPORT
            clone = e.key == CLONE
            save = e.key == SAVE
            pause = e.key == PAUSE
            fly_toggle = e.key == FLY
        elif e.type == MOUSEBUTTONDOWN:
            mouse_button_down = True

    mouse_pos = mouse.get_pos()
    mouse_pressed = mouse.get_pressed()

    if mouse_pressed[0]:
        mouse_button = 1
    elif mouse_pressed[2]:
        mouse_button = 2

    keys = key.get_pressed()

    cam_left = keys[CAM_LEFT]
    cam_right = keys[CAM_RIGHT]
    cam_up = keys[CAM_UP]
    cam_down = keys[CAM_DOWN]

    left = keys[LEFT]
    right = keys[RIGHT]
    fast = keys[FAST]
    slow = keys[SLOW]

    for num_key in NUMBER_KEYS:
        if keys[num_key]:
            break
        number_key += 1
    else:
        number_key = -1

    return (
        quit_game,
        keydown,
        jump,
        camera_toggle,
        teleport,
        clone,
        save,
        mouse_button,
        mouse_button_down,
        mouse_pos,
        cam_left,
        cam_right,
        cam_up,
        cam_down,
        left,
        right,
        fast,
        slow,
        number_key,
        pause,
        fly_toggle,
    )
