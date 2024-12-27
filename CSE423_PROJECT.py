from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
from math import cos, sin
import time

W_Width, W_Height = 500,500
plane_coordinates = {
    'fuselage': [(-220, 0), (-145, 0), (-145, 9), (-220, 9)],
    'cockpit': [(-148, 9), (-139, 4), (-145, 0)],
    'windows': [(-211, 6), (-205, 6), (-199, 6), (-193, 6), (-187, 6), (-181, 6), (-175, 6), (-169, 6), (-163, 6), (-157, 6)],
    'bottom_wing': [(-190, 0), (-169, -12), (-154, 0)],
    'top_wing': [(-187, 9), (-169, 18), (-157, 9)],
    'tail': [(-217, 9), (-226, 18), (-223, 9)],
}

plane_y_change = -100
birds = []  # List to store active birds
passed_birds = []  # List to store birds that have passed without collision
rockets = []  # [Active, x_position, y_position]
beam = [False, -220, 0]  # [Active, x_position, y_position]
beams = []  # List to store active beams
clouds = []  # List to store active clouds
score = 0
level = 1
play = True  # Start the game in the playing state
game_over = False
building_x = 250
timer = 0
target_time=0
game_complete = False
birds_killed = 0

def convert_coordinate(x,y):
    global W_Width, W_Height
    a = x - (W_Width/2)
    b = (W_Height/2) - y 
    return a,b

def draw_points(x, y, s=1):
    glPointSize(s)
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def reset_game():
    global plane_y_change, birds, passed_birds, rockets, beam, beams, clouds, score, level, game_over, play
    plane_y_change = -100
    birds = []
    passed_birds = []
    rockets = []
    beam = [False, -220, 0]
    beams = []
    clouds = []
    score = 0
    level = 1
    game_over = False
    play = True
    print("Restarting the game...")  # Log message to the console
    
def keyboardListener(key, x, y):
    global plane_y_change, beams, play
    if key == b'w':
        plane_y_change += 60
    if key == b's':
        plane_y_change -= 20
    if key == b' ':  # Shoot beam when space is pressed
        beams.append([-145, plane_y_change + 4])  # Add a new beam starting at the plane's nose position
    if key == b'p':  # Toggle play/pause state when 'p' is pressed
        play = not play

    glutPostRedisplay()
    
def mouseListener(button, state, x, y):
    global play, game_over, score
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            x, y = convert_coordinate(x, y)
            # Check if the click is within the play/pause button area
            if -5 <= x <= 15 and 225 <= y <= 245:
                play = not play  # Toggle play/pause state
            # Check if the click is within the exit button area
            if 225 <= x <= 240 and 225 <= y <= 245:
                game_over = True  # Set game over state
            # Check if the click is within the restart button area
            if -240 <= x <= -220 and 225 <= y <= 245:
                reset_game()  # Reset the game state
    glutPostRedisplay()

def drawCircle(r,x1,y1):
    d = 1-r
    x=0
    y=r
    while x<y:
        draw_points(x+x1,y+y1)
        draw_points(-x+x1,-y+y1)
        draw_points(x+x1,-y+y1)
        draw_points(-x+x1,y+y1)
        draw_points(y+x1,x+y1)
        draw_points(-y+x1,-x+y1)
        draw_points(-y+x1,x+y1)
        draw_points(y+x1,-x+y1)
        if d>=0:
            d += 2*x-2*y+5
            y -= 1
        else:
            d += 2*x +3
        x+=1
        
def checkLineZone(x1,y1,x2,y2):
    dx = x2-x1
    dy = y2-y1
    if abs(dx)>=abs(dy):
        if dx>=0 and dy>=0:
            return 0
        elif dx<0 and dy>=0:
            return 3
        elif dx<0 and dy<0:
            return 4
        else:
            return 7
    else:
        if dx>=0 and dy>=0:
            return 1
        elif dx<0 and dy>=0:
            return 2
        elif dx<0 and dy<0:
            return 5
        else:
            return 6
        
def convertToZone0(x,y,zone):
    if zone == 0:
        return x,y
    elif zone == 1:
        return y,x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x,y
    elif zone == 4:
        return -x,-y
    elif zone == 5:
        return -y,-x
    elif zone == 6:
        return -y,x
    elif zone == 7:
        return x,-y

def convertFromZone0(x,y,zone):
    if zone == 0:
        return x,y
    elif zone == 1:
        return y,x
    elif zone == 2:
        return -y,x
    elif zone == 3:
        return -x,y
    elif zone == 4:
        return -x,-y
    elif zone == 5:
        return -y,-x
    elif zone == 6:
        return y,-x
    elif zone == 7:
        return x,-y

def drawLine(x1,y1,x2,y2,s=1):
    zone = checkLineZone(x1,y1,x2,y2)
    x1,y1 = convertToZone0(x1,y1,zone)
    x2,y2 = convertToZone0(x2,y2,zone)
    dx= x2-x1
    dy=y2-y1
    d=(2*dy) - dx
    incE = 2*dy
    incNE = 2*(dy-dx)
    y=y1
    coordinates = []
    for i in range(int(x1),int(x2)+1):
        if d>0:
            d+=incNE
            y=y+1
        else:
            d+=incE
        coordinates.append((i,y))
    for i in coordinates:
        x,y = convertFromZone0(i[0],i[1],zone)
        draw_points(x,y,s)

def check_aabb_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)

def animate():
    global plane_y_change, rockets, beams, clouds, score, level, birds, play,timer,target_time, building_x, game_complete, birds_killed, game_over

    if not play or game_over or game_complete:
        return

    plane_y_change -= 5
    if level == 2 and score >= 30:
        level = 3
        timer = time.time()
        target_time = timer + random.randint(15, 20)
        print("Level 3")
    if level == 1 and score >= 10:
        level = 2
        print("Level 2")

    if plane_y_change <= -230 or plane_y_change >= 230:
        game_over= True

    for i in range(len(birds)):
        if i >= len(birds):
            break
        bird = birds[i]
        if check_aabb_collision(-183, 3 + plane_y_change, 87, 30, bird[2], bird[3] + bird[1], 20, 10):
            birds_killed += 1
            birds.pop(i)
            i -= 1
            score -= 1
            print("Don't kill the birds! You have killed", birds_killed, "birds.")
            print(f"Score: {score}")
            if birds_killed >= 3:
                game_over = True
                return
            continue

        for j in range(len(beams)):
            if j >= len(beams):
                break
            beam = beams[j]
            if check_aabb_collision(bird[2], bird[3] + bird[1], 20, 10, beam[0], beam[1], 20, 2):
                beams.pop(j)  # Deactivate beam
                j -= 1
                birds.pop(i)
                i -= 1
                score -= 1
                birds_killed += 1
                print("Don't kill the birds! You have killed", birds_killed, "birds.")
                print(f"Score: {score}")
                if birds_killed >= 3:
                    game_over = True
                    return
                continue
        
        bird[2] -= 5
        if bird[2] < -250:
            birds.pop(i)
            i -= 1
            score += 1  # Increase score for each bird that passes without collision
            print(f"Score: {score}")

        if bird[1] > 15:
            bird[0] = False
        elif bird[1] < -15:
            bird[0] = True
        if bird[0]:
            bird[1] += 3
        else:
            bird[1] -= 3

    if level > 1 and random.randint(1, 100) <= 2:
        birds.append([True, 0, 250, random.randint(-200, 200)])

    # Move beams
    for beam in beams:
        beam[0] += 10
    beams = [beam for beam in beams if beam[0] <= 250]  # Remove beams that go off screen

    # Move clouds
    for cloud in clouds:
        cloud[0] -= 3  # Move cloud to the left

    # Remove clouds that go off screen and update score if they pass without collision
    for i in range(len(clouds)):
        if i >= len(clouds):
            break
        cloud = clouds[i]
        if cloud[0] <= -250:
            clouds.pop(i)
            i -= 1
            continue
        # Check for collision with plane
        if check_aabb_collision(cloud[0], cloud[1], 40, 30, -183, 3 + plane_y_change, 87, 30):
            score += 1
            clouds.pop(i)
            i -= 1
            print(f"Score: {score}")

    # Add new cloud at random intervals
    if random.randint(1, 100) <= 3:  # Adjust the frequency as needed
        clouds.append([250, random.randint(-200, 200)])  # Add a new cloud starting from the right

    # Check for beam collisions with rocket
    for j in range(len(beams)):
        if j >= len(beams):
            break
        beam = beams[j]
        for i in range(len(rockets)):
            if i >= len(rockets):
                break
            rocket = rockets[i]
            if check_aabb_collision(beam[0], beam[1], 20, 10, rocket[1], rocket[2], 34, 24):
                beams.pop(j)  # Deactivate beam
                j -= 1
                rockets.pop(i)
                i -= 1
                score += 1  # Increase score
                print(f"Score: {score}")

    if level == 3 and random.randint(1, 100) <= 3:
        rockets.append([True, 250, random.randint(-200, 200)])
    # Check if plane collides with rocket
    for i in range(len(rockets)):
        if i >= len(rockets):
            break
        rocket = rockets[i]
        if rocket[0]:
            rocket[1] -= 5
            if rocket[1] < -250:
                rockets.pop(i)
                i -= 1
                continue
        # Check for collision with plane
        if check_aabb_collision(-183, 3 + plane_y_change, 87, 30, rocket[1], rocket[2], 20, 10):
            game_over = True
            break

    if level == 3 and time.time() >= target_time and not game_over:
        building_x -= 5
        # Check if plane collides with building
        if check_aabb_collision(-183, 3 + plane_y_change, 87, 30, building_x, -245, 50, 200):
            game_complete=True

    glutPostRedisplay()

char_map = {
    'G': [
        ((5, 0), (0, 0)),   # Bottom horizontal line
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 5)),  # Upper right vertical line
        ((10, 5), (5, 5)),   # Middle horizontal line
        ((5, 5), (5, 7)),   # Short vertical line
        ((5, 7), (7, 7))    # Bottom right horizontal line
    ],
    'S': [
        ((10, 0), (0, 0)),  # Bottom horizontal line
        ((0, 0), (0, 5)),   # Left bottom vertical line
        ((0, 5), (10, 5)),  # Middle horizontal line
        ((10, 5), (10, 10)),  # Right top vertical line
        ((10, 10), (0, 10)),  # Top horizontal line
        ((0, 10), (0, 5))   # Left top vertical line
    ],
    'A': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((0, 5), (10, 5))  # Middle horizontal line
    ],
    'M': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (5, 5)),  # Diagonal line to middle
        ((5, 5), (10, 10)),  # Diagonal line to top right
        ((10, 10), (10, 0))  # Right vertical line
    ],
    'E': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((0, 5), (7, 5)),  # Middle horizontal line
        ((0, 0), (10, 0))  # Bottom horizontal line
    ],
    'O': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((10, 0), (0, 0))  # Bottom horizontal line
    ],
    'V': [
        ((0, 10), (5, 0)),  # Left diagonal line
        ((5, 0), (10, 10))  # Right diagonal line
    ],
    'R': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 5)),  # Right vertical line
        ((0, 5), (10, 0))  # Diagonal line to bottom right
    ],
    'C': [
        ((10, 0), (0, 0)),  # Bottom horizontal line
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10))  # Top horizontal line
    ],
    ':': [
        ((5, 4), (5, 6)),  # Lower dot
        ((5, 9), (5, 11))  # Upper dot
    ],
    '0': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((10, 0), (0, 0))  # Bottom horizontal line
    ],
    '1': [
        ((5, 0), (5, 10))  # Vertical line
    ],
    '2': [
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 5)),  # Upper right vertical line
        ((10, 5), (0, 0)),  # Diagonal line to bottom left
        ((0, 0), (10, 0))  # Bottom horizontal line
    ],
    '3': [
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((0, 5), (10, 5)),  # Middle horizontal line
        ((0, 0), (10, 0))  # Bottom horizontal line
    ],
    '4': [
        ((0, 10), (0, 5)),  # Left vertical line
        ((0, 5), (10, 5)),  # Middle horizontal line
        ((10, 0), (10, 10))  # Right vertical line
    ],
    '5': [
        ((10, 0), (0, 0)),  # Bottom horizontal line
        ((0, 0), (0, 5)),  # Left bottom vertical line
        ((0, 5), (10, 5)),  # Middle horizontal line
        ((10, 5), (10, 10)),  # Right top vertical line
        ((10, 10), (0, 10))  # Top horizontal line
    ],
    '6': [
        ((10, 0), (0, 0)),  # Bottom horizontal line
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 5)),  # Upper right vertical line
        ((10, 5), (0, 5))  # Middle horizontal line
    ],
    '7': [
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0))  # Right vertical line
    ],
    '8': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((10, 0), (0, 0)),  # Bottom horizontal line
        ((0, 5), (10, 5))  # Middle horizontal line
    ],
    '9': [
        ((0, 0), (0, 10)),  # Left vertical line
        ((0, 10), (10, 10)),  # Top horizontal line
        ((10, 10), (10, 0)),  # Right vertical line
        ((0, 5), (10, 5)),  # Middle horizontal line
        ((10, 5), (10, 0))  # Bottom right vertical line
    ],
    ' ': []
}

def draw_character(char, x_offset, y_offset, scale=1):
    if char not in char_map:
        return
    lines = char_map[char]
    for (x1, y1), (x2, y2) in lines:
        drawLine(x_offset + x1 * scale, y_offset + y1 * scale, x_offset + x2 * scale, y_offset + y2 * scale, 2)

def draw_text(text, x, y, scale=1):
    for i, char in enumerate(text):
        draw_character(char, x + i * 12 * scale, y, scale)

def draw_game_over_message():
    draw_text("GAME OVER!", -50, 20, 2)

def draw_score_message(score):
    draw_text(f"SCORE: {score}", -50, -20, 2)
        
def init():
    glClearColor(0,0,0,0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104,	1,	1,	1000.0)

def controlButtons():
    global play  # Use the global play variable

    glColor3f(0, 0, 0)
    for i in range(225, 255):
        drawLine(-250, i, 250, i, 2)

    # Left arrow button
    glColor3f(0, 0.4, 0.6)
    drawLine(-240, 235, -220, 235, 2)
    drawLine(-240, 235, -230, 245, 2)
    drawLine(-240, 235, -230, 225, 2)

    # Cross button at the right
    glColor3f(0.8, 0.2, 0)
    drawLine(240, 245, 225, 225, 2)
    drawLine(240, 225, 225, 245, 2)

    # Play/Pause button at the center
    if play:
        glColor3f(1, 0.7, 0)
        drawLine(-5, 245, -5, 225, 2)
        drawLine(5, 245, 5, 225, 2)
    else:
        glColor3f(1, 0.7, 0)
        drawLine(-5, 245, -5, 225, 2)
        drawLine(-5, 245, 15, 235, 2)
        drawLine(-5, 225, 15, 235, 2)

    glColor3f(1, 0.7, 0)

def drawScenery():
    # Sky color
    glColor3f(0.529, 0.808, 0.922)
    drawLine(-250, 0, 250, 0, 1000)
    
    # Sun with rings
    glColor3f(1.0, 0.843, 0.0)
    drawFilledCircle(30, -180, 180)
    # Sun rays
    for i in range(0, 360, 30):
        drawLine(-180, 180, -180+int(45*cos(i)), 180+int(45*sin(i)), 2)
    
    # Ground at bottom
    glColor3f(0.2, 0.2, 0.2)
    drawLine(-250, -250, 250, -250, 10)

def drawPlane():
    global plane_coordinates,plane_y_change
    # Draw elements
    glColor3f(1.0, 1.0, 1.0)  # White color
    # Fuselage
    fuselage = plane_coordinates["fuselage"]
    for i in range(len(fuselage)):
        drawLine(fuselage[i][0],fuselage[i][1]+plane_y_change, fuselage[(i + 1) % len(fuselage)][0], fuselage[(i + 1) % len(fuselage)][1]+plane_y_change, 4)

    # Cockpit
    glColor3f(0.5, 0.8, 1.0)  # Light blue
    cockpit = plane_coordinates["cockpit"]
    for i in range(len(cockpit) - 1):
        drawLine(cockpit[i][0],cockpit[i][1]+plane_y_change, cockpit[i + 1][0],cockpit[i + 1][1]+plane_y_change, 2)

    # Windows
    glColor3f(0.0, 0.0, 0.0)  # Black
    for window in plane_coordinates["windows"]:
        wx, wy = int(window[0]), int(window[1])
        drawCircle(1, wx, wy+plane_y_change)

    # Bottom Wing
    glColor3f(1.0, 1.0, 1.0)  # White
    bottom_wing = plane_coordinates["bottom_wing"]
    for i in range(len(bottom_wing) - 1):
        drawLine(bottom_wing[i][0],bottom_wing[i][1]+plane_y_change, bottom_wing[i + 1][0],bottom_wing[i + 1][1]+plane_y_change, 4)

    # Top Wing
    top_wing = plane_coordinates["top_wing"]
    for i in range(len(top_wing) - 1):
        drawLine(top_wing[i][0],top_wing[i][1]+plane_y_change, top_wing[i + 1][0], top_wing[i + 1][1]+plane_y_change, 4)

    # Tail
    tail = plane_coordinates["tail"]
    for i in range(len(tail) - 1):
        drawLine(tail[i][0],tail[i][1]+plane_y_change, tail[i + 1][0],tail[i + 1][1]+plane_y_change, 4)            

def draw_rocket_midpoint():
    global rockets,level
    if level<3: return
    for i in range(len(rockets)):
        if i >= len(rockets):
            break
        rocket = rockets[i]
        if rocket[0]:
            rocket_x = rocket[1]
            rocket_y = rocket[2]
            rocket_width = 5 * 2
            rocket_height = 12 * 2

            # Fill Rocket Body
            glColor3f(1.0, 0.5, 0.0)  # Orange
            for y in range(rocket_y, rocket_y + rocket_width + 1):
                drawLine(rocket_x, y, rocket_x - rocket_height, y, s=2)

            # Nose Cone
            glColor3f(1.0, 0.0, 0.0)  # Red
            drawLine(rocket_x - rocket_height, rocket_y, rocket_x - rocket_height - 5 * 2, rocket_y + rocket_width // 2, s=2)
            drawLine(rocket_x - rocket_height, rocket_y + rocket_width, rocket_x - rocket_height - 5 * 2, rocket_y + rocket_width // 2, s=2)

            # Top Fin
            glColor3f(0.0, 0.0, 1.0)  # Blue
            drawLine(rocket_x - rocket_height // 2, rocket_y + rocket_width, rocket_x - rocket_height // 2 + 2 * 2, rocket_y + rocket_width + 5 * 2, s=2)
            drawLine(rocket_x - rocket_height // 2 + 2 * 2, rocket_y + rocket_width + 5 * 2, rocket_x - rocket_height // 2 - 2 * 2, rocket_y + rocket_width, s=2)

            # Bottom Fin
            drawLine(rocket_x - rocket_height // 2, rocket_y, rocket_x - rocket_height // 2 + 2 * 2, rocket_y - 5 * 2, s=2)
            drawLine(rocket_x - rocket_height // 2 + 2 * 2, rocket_y - 5 * 2, rocket_x - rocket_height // 2 - 2 * 2, rocket_y, s=2)

            # Flames
            glColor3f(1.0, 0.8, 0.0)  # Yellow
            drawLine(rocket_x + 2 * 2, rocket_y + 2 * 2, rocket_x + 8 * 2, rocket_y, s=2)
            drawLine(rocket_x + 2 * 2, rocket_y + rocket_width - 2 * 2, rocket_x + 8 * 2, rocket_y + rocket_width, s=2)

def draw_beam():
    global beam
    if beam[0]:
        beam_x = beam[1]
        beam_y = beam[2]
        glColor3f(1.0, 1.0, 0.0)  # Yellow beam
        drawLine(beam_x, beam_y, beam_x + 20, beam_y, 4)
        
def draw_beams():
    global beams
    glColor3f(1.0, 1.0, 0.0)  # Yellow beam
    for beam in beams:
        beam_x = beam[0]
        beam_y = beam[1]
        # Draw the edges of the beam using the midpoint line algorithm
        drawLine(beam_x, beam_y, beam_x + 20, beam_y, 2)  # Bottom edge
        drawLine(beam_x + 20, beam_y, beam_x + 20, beam_y + 2, 2)  # Right edge
        drawLine(beam_x + 20, beam_y + 2, beam_x, beam_y + 2, 2)  # Top edge
        drawLine(beam_x, beam_y + 2, beam_x, beam_y, 2)  # Left edge
             
def drawBird():
    global birds
    # Bird coordinates (start from right side)
    for bird in birds:
        bird_x = bird[2]
        bird_y = bird[3] + bird[1]
        # Body
        glColor3f(1,0.8,0)
        for i in range(1,10):
            drawCircle(i, bird_x, bird_y)
        
        # Head
        glColor3f(1, 0.5, 0)
        for i in range(1,7):
            drawCircle(i, bird_x - 8, bird_y + 5)
        
        # Beak
        glColor3f(1.0, 0.7, 0.0)  # Orange
        drawLine(bird_x - 12, bird_y + 7, bird_x - 18, bird_y + 5, 2)
        drawLine(bird_x - 18, bird_y + 5, bird_x - 12, bird_y + 3, 2)
        
        # Wings in flying position
        glColor3f(1, 0.8, 0) 
        # Upper wing
        drawLine(bird_x, bird_y + 5, bird_x + 15, bird_y + 15, 2)
        drawLine(bird_x + 15, bird_y + 15, bird_x + 5, bird_y + 5, 2)
        # Lower wing
        drawLine(bird_x, bird_y - 5, bird_x + 15, bird_y - 15, 2)
        drawLine(bird_x + 15, bird_y - 15, bird_x + 5, bird_y - 5, 2)
        
        # Tail
        drawLine(bird_x + 8, bird_y, bird_x + 15, bird_y + 5, 2)
        drawLine(bird_x + 15, bird_y + 5, bird_x + 12, bird_y, 2)
        drawLine(bird_x + 12, bird_y, bird_x + 15, bird_y - 5, 2)
        drawLine(bird_x + 15, bird_y - 5, bird_x + 8, bird_y, 2)

def drawFilledCircle(radius, cx, cy):
    for i in range(1,radius+1):
        drawCircle(i, cx, cy)

def draw_clouds():
    global clouds
    glColor3f(1.0, 1.0, 1.0)  # White color for the cloud
    for cloud in clouds:
        cx = cloud[0]
        cy = cloud[1]
        radius = 10  # Adjust the cloud size as needed

        # Draw overlapping circles to form a cloud
        drawFilledCircle(radius, cx, cy)                    # Center circle
        drawFilledCircle(radius, cx - radius, cy)           # Left circle
        drawFilledCircle(radius, cx + radius, cy)           # Right circle
        drawFilledCircle(radius, cx - radius // 2, cy + 10) # Upper left circle
        drawFilledCircle(radius, cx + radius // 2, cy + 10) # Upper right circle
                
def draw_building(x, y, height, width, has_top_tower=True):
    glColor3f(0.5, 0.5, 0.5)  # Gray for building
    drawLine(x, y, x + width, y)  # Bottom edge
    drawLine(x, y + height, x + width, y + height)  # Top edge
    drawLine(x, y, x, y + height)  # Left edge
    drawLine(x + width, y, x + width, y + height)  # Right edge

    num_floors = 15  # Number of floors
    floor_height = height / num_floors
    for i in range(1, num_floors):
        drawLine(x, y + int(i * floor_height), x + width, y + int(i * floor_height))

    # Add windows for beautification
    window_width = width // 4
    window_height = floor_height // 2
    glColor3f(1.0, 1.0, 1.0)  # White for windows
    for i in range(num_floors):
        for j in range(4):
            wx = x + j * window_width + 2
            wy = y + i * floor_height + (floor_height - window_height) // 2
            drawLine(wx, wy, wx + window_width - 4, wy)
            drawLine(wx, wy, wx, wy + window_height - 2)
            drawLine(wx + window_width - 4, wy, wx + window_width - 4, wy + window_height - 2)
            drawLine(wx, wy + window_height - 2, wx + window_width - 4, wy + window_height - 2)

    if has_top_tower:
        tower_height = 20
        tower_base_height = 20
        glColor3f(1.0, 0.0, 0.0)  # Red for top tower
        drawLine(x + width // 2, y + height, x + width // 2, y + height + tower_height)
        drawCircle(5, x + width // 2, y + height + tower_height + 5)
        
def draw_twin_buildings():
    global building_x, level
    if level < 3:
        return
    building_width = 50  # Adjusted width to be smaller
    building_height = 200  # Adjusted height to be shorter to fit within the screen
    gap = 20  # Gap between buildings
    x_offset = building_x  # Shift to the left to position buildings more within the screen
    y_offset = -245  # Position buildings with their base touching the bottom of the blue sky area

    # Draw the first building
    draw_building(x_offset, y_offset, building_height, building_width, has_top_tower=True)

    # Draw the second building next to the first one
    draw_building(x_offset + building_width + gap, y_offset, building_height, building_width, has_top_tower=False)
    
def display():
    global level, game_over, score
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    
    if game_over:
        # Display game over message and score
        glColor3f(1.0, 0.0, 0.0)  # Red color
        draw_game_over_message()
        draw_score_message(score)
    else:
        drawScenery()
        drawPlane()
        draw_rocket_midpoint()
        draw_twin_buildings()  # Draw buildings on the right side
        draw_clouds()  # Draw clouds
        if level > 1:
            drawBird()
        draw_beams()  # Draw beams
        controlButtons()
    
    glutSwapBuffers()

glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
wind = glutCreateWindow(b"9/11 Simulator Game")
init()
glutDisplayFunc(display)
glutIdleFunc(animate)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseListener)
glutMainLoop()