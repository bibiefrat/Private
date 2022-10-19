# Implementation of classic arcade game Pong

try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    

# initialize globals - pos and vel encode vertical info for paddles
WIDTH = 600
HEIGHT = 400       
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
LEFT = False
RIGHT = True
ball_pos = [WIDTH / 2, HEIGHT / 2]
vel = [+120.0 / 60.0,  60.0 / 60.0]
r=[1,1]
paddle1_pos = HEIGHT / 2
paddle2_pos = HEIGHT / 2
paddle1_vel = 0
paddle2_vel = 0
score2 = 0
score1 = 0

# initialize ball_pos and ball_vel for new bal in middle of table
def button_handler():
    new_game()
# if direction is RIGHT, the ball's velocity is upper right, else upper left
def spawn_ball(direction):
    global ball_pos, ball_vel,vel # these are vectors stored as lists
    ball_pos = [WIDTH / 2, HEIGHT / 2]
    vel = [(direction[0]*120.0) / 60.0,  direction[1] * 60.0 / 60.0]
    
# define event handlers
def new_game():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel  # these are numbers
    global score1, score2,ball_pos,r  # these are ints
    score1=0
    score1=0
    paddle1_pos= HEIGHT / 2
    paddle2_pos= HEIGHT / 2
    r[0]=random.choice( [-1, 1] )
    r[1]=random.choice( [-1, 1] )   
    spawn_ball(r)
    
    
def draw(canvas):
    global score1, score2, paddle1_pos, paddle2_pos, ball_pos, ball_vel,paddle1_vel, paddle2_vel
 
        
    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "White")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "White")
    canvas.draw_line([WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1, "White")
    
    
    
    
    
    # update ball
            
    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 2, "Red", "White")
    # Update ball position
    ball_pos[0] += vel[0]
    ball_pos[1] += vel[1]
    
    

    
    
    # update paddle's vertical position, keep paddle on the screen
    
    # draw paddles
    #canvas.draw_polygon([[0, 0], [PAD_WIDTH, 0], [PAD_WIDTH, PAD_HEIGHT],[0,PAD_HEIGHT]], 1, 'White','White')
    #canvas.draw_polygon([[0+WIDTH-PAD_WIDTH, 0], [PAD_WIDTH+WIDTH-PAD_WIDTH, 0], [PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT],[0+WIDTH-PAD_WIDTH,PAD_HEIGHT]], 1, 'White','White')

    
    # determine whether paddle and ball collide    
    if ball_pos[0] <= BALL_RADIUS+PAD_WIDTH:
        vel[0] = -1 * vel[0]        
    elif ball_pos[0] >= WIDTH-BALL_RADIUS-PAD_WIDTH:
        vel[0] = -1 * vel[0]
    elif ball_pos[1] >= HEIGHT-BALL_RADIUS:
        vel[1] = -1 * vel[1]
    elif ball_pos[1] <= BALL_RADIUS:
        vel[1] = -1 * vel[1] 
    
    if ball_pos[1] > paddle1_pos and ball_pos[1] < paddle1_pos + PAD_HEIGHT and ball_pos[0] <= BALL_RADIUS+PAD_WIDTH:
        score2 = score2
        score1 = score1       
    if ball_pos[1] > paddle2_pos and ball_pos[1] < paddle2_pos + PAD_HEIGHT and ball_pos[0] >= WIDTH-BALL_RADIUS-PAD_WIDTH:
        score2 = score2
        score1 = score1      
    
    if not (ball_pos[1] > paddle1_pos and ball_pos[1] < paddle1_pos + PAD_HEIGHT) and ball_pos[0] <= BALL_RADIUS+PAD_WIDTH:
        score2 += 1
        score1 = score1       
    if not (ball_pos[1] > paddle2_pos and ball_pos[1] < paddle2_pos + PAD_HEIGHT) and ball_pos[0] >= WIDTH-BALL_RADIUS-PAD_WIDTH:
        score2 = score2
        score1 += 1
        
    if paddle1_pos + paddle1_vel > HEIGHT - PAD_HEIGHT:
        paddle1_pos =   HEIGHT - PAD_HEIGHT
        canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos],[HALF_PAD_WIDTH, PAD_HEIGHT+paddle1_pos], PAD_WIDTH, "White")
        canvas.draw_line([HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, paddle2_pos],[HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT+paddle2_pos], PAD_WIDTH, "White")

        return
    if paddle1_pos + paddle1_vel < 0:
        paddle1_pos =   0
        canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos],[HALF_PAD_WIDTH, PAD_HEIGHT+paddle1_pos], PAD_WIDTH, "White")
        canvas.draw_line([HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, paddle2_pos],[HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT+paddle2_pos], PAD_WIDTH, "White")

        return
    if paddle2_pos + paddle2_vel > HEIGHT - PAD_HEIGHT:
        paddle2_pos =   HEIGHT - PAD_HEIGHT
        canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos],[HALF_PAD_WIDTH, PAD_HEIGHT+paddle1_pos], PAD_WIDTH, "White")
        canvas.draw_line([HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, paddle2_pos],[HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT+paddle2_pos], PAD_WIDTH, "White")

        return
    if paddle2_pos + paddle2_vel < 0:
        paddle2_pos =   0
        canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos],[HALF_PAD_WIDTH, PAD_HEIGHT+paddle1_pos], PAD_WIDTH, "White")
        canvas.draw_line([HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, paddle2_pos],[HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT+paddle2_pos], PAD_WIDTH, "White")

        return
        

    paddle1_pos += paddle1_vel
    paddle2_pos += paddle2_vel
    canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos],[HALF_PAD_WIDTH, PAD_HEIGHT+paddle1_pos], PAD_WIDTH, "White")
    canvas.draw_line([HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, paddle2_pos],[HALF_PAD_WIDTH+WIDTH-PAD_WIDTH, PAD_HEIGHT+paddle2_pos], PAD_WIDTH, "White")
    
    
    # draw scores
    canvas.draw_text(str(score1), [ WIDTH / 2 - 100 ,50], 20, "White")
    canvas.draw_text(str(score2), [ WIDTH / 2 + 100, 50], 20, "White")
    
def keydown(key):
    global paddle1_vel, paddle2_vel,paddle1_pos, paddle2_pos
#    if paddle1_pos == HEIGHT - HALF_PAD_HEIGHT or paddle1_pos == HALF_PAD_HEIGHT:
#        paddle1_vel = 0
#        print paddle1_pos
#        return
#    if paddle2_pos == HEIGHT - HALF_PAD_HEIGHT or paddle2_pos == HALF_PAD_HEIGHT:
#        paddle2_vel = 0
#        return
    if key==simplegui.KEY_MAP["up"] :
            paddle1_vel = (-1 * 5)
    if key==simplegui.KEY_MAP["down"]:
            paddle1_vel = 5 
    if key==simplegui.KEY_MAP["w"] :
            paddle2_vel = (-1 * 5)
    if key==simplegui.KEY_MAP["s"] :
            paddle2_vel = 5
#    print str(paddle1_pos) + " " + str(paddle1_pos)
            
            
def keyup(key):
    global paddle1_vel, paddle2_vel
    if key==simplegui.KEY_MAP["up"]:
        paddle1_vel=0
    if key==simplegui.KEY_MAP["down"]:
        paddle1_vel=0
    if key==simplegui.KEY_MAP["w"]:
        paddle2_vel=0
    if key==simplegui.KEY_MAP["s"]:
        paddle2_vel=0
        
# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
button1 = frame.add_button('Restart', button_handler)





# start frame
#new_game()
frame.start()
