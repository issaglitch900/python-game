 #################################################### EGGSISTENTIAL CRISIS ##################################################

#  Move with arrow keys. Spatulas block paths.
#  Stay on hot pans too long and your egg gets fried.
#  Survive 3 minutes to win.
#
#  Controls: Arrow keys = move | C = cheat | WASD = camera | R = restart
#
#  Member 1: Adib Anwar             - Environment and Heat System
#  Member 2: Khalid Mumin Chowdhury - Player Mechanics
#  Member 3: Nafisa Tabassum        - Game Logic and Interaction


from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import math
import random

# window size
WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 800

# grid 3x3
COLS    = 3
ROWS    = 3
SPACING = 300

def stove_pos(idx):
    row = idx // COLS
    col = idx  % COLS
    x   = (col - 1) * SPACING
    y   = (1 - row) * SPACING
    return (float(x), float(y))

STOVE_POS = [stove_pos(i) for i in range(9)]

# all valid movement paths (no diagonal)
ALL_PATHS = [
    (0,1),(1,2),
    (3,4),(4,5),
    (6,7),(7,8),
    (0,3),(3,6),
    (1,4),(4,7),
    (2,5),(5,8),
]

# paths spatulas can spawn
SPATULA_PATHS = [
    (1,4),(3,4),(4,5),(4,7),
    (1,2),(0,1),(6,7),(7,8),
    (0,3),(3,6),(2,5),(5,8),
]

# pans reachable from each pan
NEIGHBOURS = {
    0:[1,3],
    1:[0,2,4],
    2:[1,5],
    3:[0,4,6],
    4:[1,3,5,7],
    5:[2,4,8],
    6:[3,7],
    7:[4,6,8],
    8:[5,7],
}

# stove/pan sizing
STOVE_H    = 70
STOVE_W    = 110
STOVE_D    = 90
PAN_RADIUS = 80
PAN_TOP_Z  = STOVE_H + 8

last_time = 0.0


#============================================================

#  MEMBER 1 - Adib Anwar- Environment and Heat System


pan_state = [0] * 9
pan_timer = [random.uniform(0, 1.5) for _ in range(9)]

COOL_DUR = 3.5
HOT_DUR  = 7.0


def init_pans():
    cool_pans = random.sample(range(9), 2)
    for i in range(9):
        if i in cool_pans:
            pan_state[i] = 0
            pan_timer[i] = random.uniform(0, 3.5)
        else:
            pan_state[i] = 1
            pan_timer[i] = random.uniform(0, 7.0)

init_pans()


def pan_color(idx):
    if pan_state[idx] == 0:
        return (0.45, 0.55, 0.75)
    else:
        t = min(1.0, pan_timer[idx] / HOT_DUR)
        r = 0.85 + t * 0.15
        g = 0.35 - t * 0.25
        b = 0.05
        return (r, g, b)


def update_pans(dt):
    
    for i in range(9):
        pan_timer[i] += dt

        if pan_state[i] == 0:
            if pan_timer[i] >= COOL_DUR:
                pan_state[i] = 1
                pan_timer[i] = 0.0

        elif pan_state[i] == 1:
            if pan_timer[i] >= HOT_DUR:
                cool_count = sum(1 for j in range(9) if pan_state[j] == 0)
                if cool_count >= 2:
                    pan_timer[i] = 0.0   #stay hot, reset timer
                else:
                    pan_state[i] = 0
                    pan_timer[i] = 0.0


def reset_pan_cool(idx):
    if pan_state[idx] == 0:
        pan_timer[idx] = 0.0


def draw_stove(idx):
    sx, sy     = STOVE_POS[idx]
    pr, pg, pb = pan_color(idx)

    glPushMatrix()
    glTranslatef(sx, sy, 0)

    # legs
    glColor3f(0.15, 0.15, 0.15)
    leg_offsets = [
        (-STOVE_W + 15, -STOVE_D + 15),
        ( STOVE_W - 15, -STOVE_D + 15),
        (-STOVE_W + 15,  STOVE_D - 15),
        ( STOVE_W - 15,  STOVE_D - 15),
    ]
    for lx, ly in leg_offsets:
        glPushMatrix()
        glTranslatef(lx, ly, 0)
        gluCylinder(gluNewQuadric(), 6, 6, STOVE_H - 4, 8, 2)
        glPopMatrix()

    # main body
    glPushMatrix()
    glTranslatef(0, 0, STOVE_H / 2)
    glColor3f(0.72, 0.72, 0.75)
    glScalef(STOVE_W * 2, STOVE_D * 2, STOVE_H)
    glutSolidCube(1)
    glPopMatrix()

    # dark top slab
    glPushMatrix()
    glTranslatef(0, 0, STOVE_H + 2)
    glColor3f(0.18, 0.18, 0.20)
    glScalef(STOVE_W * 2, STOVE_D * 2, 5)
    glutSolidCube(1)
    glPopMatrix()

    # burner rings
    heat = pan_state[idx]
    glow = (pan_timer[idx] / HOT_DUR) if heat == 1 else 0.0
    glColor3f(0.25 + glow * 0.65, 0.10 + glow * 0.05, 0.05)

    burner_positions = [(-32, -24), (32, -24), (-32, 24), (32, 24)]
    for bx, by in burner_positions:
        glPushMatrix()
        glTranslatef(bx, by, STOVE_H + 5)
        glScalef(1, 1, 0.12)
        glutWireTorus(3, 16, 8, 18)
        glPopMatrix()

    # pan disc
    glColor3f(pr, pg, pb)
    glPushMatrix()
    glTranslatef(0, 0, STOVE_H + 8)
    gluDisk(gluNewQuadric(), 0, PAN_RADIUS, 28, 1)
    glPopMatrix()

    # pan rim
    glColor3f(0.22, 0.22, 0.24)
    glPushMatrix()
    glTranslatef(0, 0, STOVE_H + 9)
    glScalef(1, 1, 0.12)
    glutWireTorus(5, PAN_RADIUS - 5, 6, 28)
    glPopMatrix()

    glPopMatrix()


def draw_kitchen():
    # tiled floor + back wall with horizontal grout lines
    TILE = 100
    EXT  = 700

    for row in range(-7, 7):
        for col in range(-7, 7):
            x0 = col * TILE
            y0 = row * TILE
            if (row + col) % 2 == 0:
                glColor3f(0.88, 0.86, 0.82)
            else:
                glColor3f(0.76, 0.74, 0.70)
            glBegin(GL_QUADS)
            glVertex3f(x0,        y0,        -2)
            glVertex3f(x0 + TILE, y0,        -2)
            glVertex3f(x0 + TILE, y0 + TILE, -2)
            glVertex3f(x0,        y0 + TILE, -2)
            glEnd()

    # back wall
    glColor3f(0.85, 0.82, 0.78)
    glBegin(GL_QUADS)
    glVertex3f(-EXT,  EXT, -2)
    glVertex3f( EXT,  EXT, -2)
    glVertex3f( EXT,  EXT, 400)
    glVertex3f(-EXT,  EXT, 400)
    glEnd()

    # wall lines
    glColor3f(0.68, 0.66, 0.62)
    for wz in range(0, 400, 70):
        glBegin(GL_LINES)
        glVertex3f(-EXT, EXT, wz)
        glVertex3f( EXT, EXT, wz)
        glEnd()




# ============================================================
#  MEMBER 2 - Khalid Mumin Chowdhury- Player Mechanics

player_pan       = 4
player_health    = 100
fry_timer        = 0.0
next_health_drop = 3.0
last_pan_was_hot = False


is_jumping    = False
jump_t        = 0.0
JUMP_DUR      = 0.3
jump_elapsed  = 0.0
jump_src      = 4
jump_dst      = 4
jump_src_x    = 0.0
jump_src_y    = 0.0
jump_dst_x    = 0.0
jump_dst_y    = 0.0
JUMP_HEIGHT   = 180

# brief pause after landing before next move is allowed
station_wait    = False
station_elapsed = 0.0
STATION_DUR     = 0.4

pending_move   = None
fried_progress = 0.0


def egg_health_color(health):
    if health >= 80:
        t = (health - 80) / 20.0
        return (0.55 + t*0.10, 0.72 + t*0.10, 0.95)
    elif health >= 60:
        t = (health - 60) / 20.0
        return (0.85 + t*0.20, 0.85 + t*0.05, 0.85 + t*0.10)
    elif health >= 40:
        t = (health - 40) / 20.0
        return (0.95, 0.90*t + 0.50*(1-t), 0.30*t)
    elif health >= 20:
        t = (health - 20) / 20.0
        return (0.95, 0.50*t + 0.15*(1-t), 0.05*t)
    else:
        t = health / 20.0
        return (0.75 + t*0.20, 0.10*t, 0.0)


def player_world_pos():
    if not is_jumping:
        sx, sy = STOVE_POS[player_pan]
        return sx, sy, PAN_TOP_Z + 28

    t = jump_t
    x = jump_src_x + (jump_dst_x - jump_src_x) * t
    y = jump_src_y + (jump_dst_y - jump_src_y) * t
    z = PAN_TOP_Z + 28 + JUMP_HEIGHT * 4 * t * (1 - t)
    return x, y, z


def draw_player_egg():
    px, py, pz = player_world_pos()
    r, g, b    = egg_health_color(player_health)

    glPushMatrix()
    glTranslatef(px, py, pz)

    if fried_progress > 0:
        sw = 1.0 + fried_progress * 3.5
        sz = max(0.06, 1.0 - fried_progress * 0.94)
        glScalef(sw, sw, sz)
        glColor3f(0.65, 0.10, 0.05)
    else:
   
        t   = glutGet(GLUT_ELAPSED_TIME) * 0.001
        wob = 1.0 + 0.04 * math.sin(t * 3.0)
        glScalef(1.0, 1.0, 1.28 * wob)
        glColor3f(r, g, b)

    gluSphere(gluNewQuadric(), 28, 20, 20)


    if player_health > 40 and fried_progress == 0:
        glColor3f(1.0, 0.85, 0.10)
        glPushMatrix()
        glTranslatef(0, 0, 8)
        gluSphere(gluNewQuadric(), 10, 10, 10)
        glPopMatrix()

    glPopMatrix()


def start_jump(src, dst):
    global is_jumping, jump_t, jump_elapsed
    global jump_src, jump_dst
    global jump_src_x, jump_src_y, jump_dst_x, jump_dst_y

    jump_src   = src
    jump_dst   = dst
    jump_src_x, jump_src_y = STOVE_POS[src]
    jump_dst_x, jump_dst_y = STOVE_POS[dst]
    jump_t       = 0.0
    jump_elapsed = 0.0
    is_jumping   = True


def update_jump(dt):
    # advance jump arc
    global is_jumping, jump_t, jump_elapsed
    global station_wait, station_elapsed
    global player_pan, player_health, fry_timer, next_health_drop
    global last_pan_was_hot

    if not is_jumping:
        return

    jump_elapsed += dt
    jump_t = min(1.0, jump_elapsed / JUMP_DUR)

    if jump_t >= 1.0:
        is_jumping  = False
        src_was_hot = (pan_state[jump_src] == 1)
        player_pan  = jump_dst
        reset_pan_cool(player_pan)

        # landed on cool after hot -> reward +20 hp and reset fry timer
        if pan_state[player_pan] == 0 and src_was_hot:
            player_health    = min(100, player_health + 20)
            fry_timer        = 0.0
            next_health_drop = fry_timer + 3.0
            last_pan_was_hot = False
        else:
            last_pan_was_hot = (pan_state[player_pan] == 1)

        station_wait    = True
        station_elapsed = 0.0


def update_station(dt):
    global station_wait, station_elapsed, pending_move

    if not station_wait:
        return

    station_elapsed += dt

    if station_elapsed >= STATION_DUR:
        station_wait = False
        if pending_move is not None:
            attempt_move(pending_move)
            pending_move = None


def update_fry_timer(dt):
   
    global fry_timer, player_health, next_health_drop

    if is_jumping:
        return

    if pan_state[player_pan] == 1:
        fry_timer += dt
    else:
        fry_timer = max(0.0, fry_timer - dt * 0.3)

    while fry_timer >= next_health_drop and player_health > 0:
        player_health    = max(0, player_health - 20)
        next_health_drop += 3.0


def attempt_move(direction):
    global pending_move

    if is_jumping or station_wait:
        pending_move = direction
        return False

    row = player_pan // COLS
    col = player_pan  % COLS

    target = None
    if direction == 'up'    and row > 0:        target = player_pan - COLS
    if direction == 'down'  and row < ROWS - 1: target = player_pan + COLS
    if direction == 'left'  and col > 0:        target = player_pan - 1
    if direction == 'right' and col < COLS - 1: target = player_pan + 1

    if target is None:
        return False

    if is_path_blocked(player_pan, target):
        return False

    start_jump(player_pan, target)
    return True



#============================================================

#  MEMBER 3 - Nafisa Tabassum- Game Logic and Interaction



spatulas           = []
MAX_SPATULAS       = 3
last_spatula_spawn = 0.0
next_spatula_spawn = 4.0


def is_path_blocked(a, b):
    pair = tuple(sorted([a, b]))
    for sp in spatulas:
        if tuple(sorted(sp['path'])) == pair:
            return True
    return False


def player_has_at_least_one_move():
    for n in NEIGHBOURS[player_pan]:
        if not is_path_blocked(player_pan, n):
            return True
    return False


def try_spawn_spatula(current_time):
    global last_spatula_spawn, next_spatula_spawn

    if current_time - last_spatula_spawn < next_spatula_spawn:
        return

    last_spatula_spawn = current_time
    next_spatula_spawn = 4.0

    fill_attempts = 0
    while len(spatulas) < MAX_SPATULAS and fill_attempts < 20:
        fill_attempts += 1

        paths = list(SPATULA_PATHS)
        random.shuffle(paths)

        placed = False
        for path in paths:
            if is_path_blocked(path[0], path[1]):
                continue

            duration    = random.uniform(6.0, 12.0)
            new_spatula = {'path': path, 'elapsed': 0.0, 'duration': duration}
            spatulas.append(new_spatula)

            if player_has_at_least_one_move():
                placed = True
                break
            else:
                spatulas.remove(new_spatula)   # would trap player

        if not placed:
            break


def update_spatulas(dt):
    expired = [sp for sp in spatulas if sp['elapsed'] + dt >= sp['duration']]
    for sp in expired:
        spatulas.remove(sp)
    for sp in spatulas:
        sp['elapsed'] += dt


def draw_spatula(sp):
    a, b   = sp['path']
    ax, ay = STOVE_POS[a]
    bx, by = STOVE_POS[b]
    mx     = (ax + bx) / 2.0
    my     = (ay + by) / 2.0
    mz     = PAN_TOP_Z + 90

    horizontal = (ay == by) 

    glPushMatrix()
    glTranslatef(mx, my, mz)

    if horizontal:
        glRotatef(90, 0, 0, 1)

    # handle
    glColor3f(0.45, 0.28, 0.12)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 4, 85, 8, 3)
    glPopMatrix()

    # blade
    glColor3f(0.70, 0.70, 0.74)
    glPushMatrix()
    glTranslatef(0, 85, 0)
    glScalef(50, 55, 5)
    glutSolidCube(1)
    glPopMatrix()

    # 3 slot holes
    glColor3f(0.22, 0.22, 0.26)
    for hx in [-15, 0, 15]:
        glPushMatrix()
        glTranslatef(hx, 100, 0)
        glScalef(7, 16, 7)
        glutSolidCube(1)
        glPopMatrix()

    glPopMatrix()


#Cheat Mode


cheat_mode     = False
cheat_elapsed  = 0.0
CHEAT_DUR      = 10.0
cheat_move_acc = 0.0


def toggle_cheat():
    global cheat_mode, cheat_elapsed, cheat_move_acc
    if not cheat_mode:
        cheat_mode     = True
        cheat_elapsed  = 0.0
        cheat_move_acc = 0.0


def update_cheat(dt):
    global cheat_mode, cheat_elapsed
    if cheat_mode:
        cheat_elapsed += dt
        if cheat_elapsed >= CHEAT_DUR:
            cheat_mode = False


def cheat_auto_move(dt):
    global cheat_move_acc

    if not cheat_mode or is_jumping or station_wait:
        return

    cheat_move_acc += dt
    if cheat_move_acc < 0.7:
        return

    cheat_move_acc = 0.0

    reachable = [
        (pan_state[n], n)
        for n in NEIGHBOURS[player_pan]
        if not is_path_blocked(player_pan, n)
    ]

    if not reachable:
        return

    reachable.sort(key=lambda x: x[0]) 
    best = reachable[0][1]

    if best != player_pan:
        start_jump(player_pan, best)


# Camera

cam_h_angle = 25.0
cam_v_angle = 38.0
CAM_DIST    = 1050


def setup_camera():
    # WASD rotates
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 4000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    h  = math.radians(cam_h_angle)
    v  = math.radians(cam_v_angle)
    ex = CAM_DIST * math.cos(v) * math.sin(h)
    ey = CAM_DIST * math.cos(v) * (-math.cos(h))
    ez = CAM_DIST * math.sin(v) + STOVE_H

    gluLookAt(ex, ey, ez, 0, 0, STOVE_H, 0, 0, 1)


#Game State

game_over       = False
game_won        = False
game_start_time = 0.0
WIN_TIME        = 180.0   #3 min


def check_game_state(current_time):
    global game_over, game_won, fried_progress

    if game_over or game_won:
        if game_over:
            fried_progress = min(1.0, fried_progress + 0.010)
        return

    if player_health <= 0:
        game_over = True

    if current_time - game_start_time >= WIN_TIME:
        game_won = True


#HUD

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_health_bar():
    #5 colored segments (20 hp each)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    seg_w = 36
    seg_h = 18
    gap   = 3
    x0    = 90
    y0    = WINDOW_HEIGHT - 36

    seg_colors = [
        (0.55, 0.72, 0.95),   # blue  - full health
        (0.90, 0.90, 0.90),   # white
        (0.95, 0.90, 0.40),   # yellow
        (0.95, 0.45, 0.10),   # orange
        (0.80, 0.12, 0.08),   # red   - critical
    ]

    filled = max(0, (player_health + 19) // 20)

    for i in range(5):
        x     = x0 + i * (seg_w + gap)
        color = seg_colors[4 - i] if i < filled else (0.25, 0.25, 0.25)

        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x,         y0)
        glVertex2f(x + seg_w, y0)
        glVertex2f(x + seg_w, y0 + seg_h)
        glVertex2f(x,         y0 + seg_h)
        glEnd()

        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x,         y0)
        glVertex2f(x + seg_w, y0)
        glVertex2f(x + seg_w, y0 + seg_h)
        glVertex2f(x,         y0 + seg_h)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_hud(current_time):
    elapsed   = current_time - game_start_time
    remaining = max(0.0, WIN_TIME - elapsed)
    mins      = int(remaining) // 60
    secs      = int(remaining) % 60

    pan_label = "COOL" if pan_state[player_pan] == 0 else "HOT"

    draw_text(10, WINDOW_HEIGHT - 28,  "Health:")
    draw_health_bar()
    draw_text(10, WINDOW_HEIGHT - 57,  "Current pan: " + str(player_pan) + "  [" + pan_label + "]")
    draw_text(10, WINDOW_HEIGHT - 82,  "Spatulas blocking: " + str(len(spatulas)))
    draw_text(10, WINDOW_HEIGHT - 107, "Survive: " + str(mins).zfill(2) + ":" + str(secs).zfill(2) + " remaining")

    draw_text(10, 38, "Arrow keys: move    C: hard-boil cheat    W/A/S/D: camera    R: restart")
    draw_text(10, 14, "Cool pan = blue-grey    Hot pan = orange-red    Spatula = blocked path")

    if game_over:
        draw_text(WINDOW_WIDTH // 2 - 175, WINDOW_HEIGHT // 2 + 10,
                  "YOU WERE FRIED!   Press R to restart")

    if game_won:
        draw_text(WINDOW_WIDTH // 2 - 175, WINDOW_HEIGHT // 2 + 10,
                  "YOU SURVIVED 3 MINUTES!   Press R to play again")





#Input, Idle Loop, Display, Reset, Main

def keyboard_listener(key, x, y):
    global cam_h_angle, cam_v_angle

    if key == b'r':
        reset_game()
        return

    if game_over or game_won:
        return

    if key == b'c':
        toggle_cheat()
    elif key == b'a':
        cam_h_angle -= 5
    elif key == b'd':
        cam_h_angle += 5
    elif key == b'w':
        cam_v_angle = min(80, cam_v_angle + 4)
    elif key == b's':
        cam_v_angle = max(10, cam_v_angle - 4)

    glutPostRedisplay()


def special_key_listener(key, x, y):
    if game_over or game_won:
        return
    if key == GLUT_KEY_UP:
        attempt_move('up')
    elif key == GLUT_KEY_DOWN:
        attempt_move('down')
    elif key == GLUT_KEY_LEFT:
        attempt_move('left')
    elif key == GLUT_KEY_RIGHT:
        attempt_move('right')
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    pass


def idle():
    global last_time

    current_ms   = glutGet(GLUT_ELAPSED_TIME)
    current_time = current_ms / 1000.0
    dt           = min(current_time - last_time, 0.05)
    last_time    = current_time

    if not game_over and not game_won:
        update_pans(dt)
        update_jump(dt)
        update_station(dt)

        if not cheat_mode:
            update_fry_timer(dt)

        update_spatulas(dt)
        try_spawn_spatula(current_time)
        update_cheat(dt)
        cheat_auto_move(dt)

    check_game_state(current_time)
    glutPostRedisplay()


def show_screen():
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setup_camera()
    draw_kitchen()

    for i in range(9):
        draw_stove(i)

    for sp in spatulas:
        draw_spatula(sp)

    draw_player_egg()
    draw_hud(current_time)

    glutSwapBuffers()


def reset_game():
    global player_pan, player_health,  fry_timer, next_health_drop
    global last_pan_was_hot, is_jumping, jump_t, jump_elapsed
    global station_wait, station_elapsed, pending_move, fried_progress
    global cheat_mode, cheat_elapsed,  cheat_move_acc
    global game_over, game_won
    global last_spatula_spawn, next_spatula_spawn
    global game_start_time, last_time

    player_pan       = 4
    player_health    = 100
    fry_timer        = 0.0
    next_health_drop = 3.0
    last_pan_was_hot = False
    is_jumping       = False
    jump_t           = 0.0
    jump_elapsed     = 0.0
    station_wait     = False
    station_elapsed  = 0.0
    pending_move     = None
    fried_progress   = 0.0
    cheat_mode       = False
    cheat_elapsed    = 0.0
    cheat_move_acc   = 0.0
    game_over        = False
    game_won         = False

    spatulas.clear()

    cool_pans = random.sample(range(9), 2)
    for i in range(9):
        if i in cool_pans:
            pan_state[i] = 0
            pan_timer[i] = random.uniform(0, 3.5)
        else:
            pan_state[i] = 1
            pan_timer[i] = random.uniform(0, 7.0)

    current_time       = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    last_time          = current_time
    game_start_time    = current_time
    last_spatula_spawn = current_time
    next_spatula_spawn = 4.0


def main():
    global last_time, game_start_time
    global last_spatula_spawn, next_spatula_spawn

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Eggsistential Crisis")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.50, 0.55, 0.65, 1.0)

    current_time       = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    last_time          = current_time
    game_start_time    = current_time
    last_spatula_spawn = current_time
    next_spatula_spawn = 4.0

    glutDisplayFunc(show_screen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouseListener)

    glutMainLoop()


if __name__ == "__main__":
    main()