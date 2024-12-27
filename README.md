# 9/11 Simulator Game Project

## Features

### 1. Plane Movement

- The plane can move up and down using the 'w' and 's' keys.
- The plane's position is updated continuously to simulate flight.

### 2. Shooting Beams

- The plane can shoot beams using the space bar.
- Beams can destroy rockets and birds.

### 3. Birds

- Birds appear randomly and move across the screen in a zigzag pathway.
- Colliding with birds decreases the score and can end the game if too many birds are killed.

### 4. Rockets

- Rockets appear in level 3 and move towards the plane.
- Colliding with rockets ends the game.

### 5. Clouds

- Clouds appear randomly and move across the screen.
- Colliding with clouds increases the score.

### 6. Levels

- The game has three levels, each with increasing difficulty.
- Level 1: Basic flight and cloud collision.
- Level 2: Addition of birds in a high frequency.
- Level 3: Introduction of rockets and the mighty twin tower.

### 7. Buildings

- Building appears in level 3 and move towards the plane.
- Colliding with the twin tower completes the game.

### 8. Score and Game Over

- The score is displayed on the screen.
- The game ends if the plane collides with too many birds or rockets.
- A "Game Over" message is displayed when the game ends.

### 9. Game Controls

- 'w': Move plane up.
- 's': Move plane down.
- ' ': Shoot beam.
- 'p': Toggle play/pause.
- Mouse click: Control buttons for play/pause, restart, and exit.

### 10. Graphics

- The game uses OpenGL for rendering graphics.
- Includes detailed drawings of the plane, birds, rockets, clouds, and buildings.

### 11. Animation

- The game includes smooth animations for plane movement, bird flight, rocket launch, and cloud movement.

## How to Run

1. Ensure you have Python and the necessary libraries installed (`PyOpenGL`, `GLUT`).
2. Run the `CSE423_PROJECT.py` file to start the game.
3. Use the keyboard and mouse controls to play the game.

## Dependencies

- Python 3.x
- PyOpenGL
- GLUT

## Note

This game is a simulation and is intended for educational purposes only.
