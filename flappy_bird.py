import pygame, sys, random

#game vars
GAME_WIDTH = 360
GAME_HEIGHT = 640

#bird class
bird_x = GAME_WIDTH/8
bird_y = GAME_HEIGHT/2
bird_width = 34
bird_height = 24

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img

#pipe class
pipe_x = GAME_WIDTH
pipe_y = 0
pipe_width = 64
pipe_height = 512

class Pipe(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.passed = False

#images
background = pygame.image.load("images/flappybirdbg.png")

bird_img = pygame.image.load("images/flappybird.png")
bird_img = pygame.transform.scale(bird_img, (bird_width, bird_height))

top_pipe_img = pygame.image.load("images/toppipe.png")
top_pipe_img = pygame.transform.scale(top_pipe_img, (pipe_width, pipe_height))
bottom_pipe_img = pygame.image.load("images/bottompipe.png")
bottom_pipe_img = pygame.transform.scale(bottom_pipe_img, (pipe_width, pipe_height))

over_msg = pygame.image.load("images/message.png")
over_msg = pygame.transform.scale(over_msg, (276, 401))
over_msg_rect = over_msg.get_rect(center=(GAME_WIDTH/2,GAME_HEIGHT/2-30))

icon = pygame.image.load("images/flappybirdicon.ico")

#game
bird = Bird(bird_img)
pipes = []
velocity_x = -2 #moves pipes to the left (speed)
velocity_y = 0 #moves bird up and down (speed)
gravity = 0.4
score = 0
high_score = 0
game_over = False

#when it is a new game, it gets the current highscore
with open("high_scores.txt", "r") as f:
    scores = f.readlines()
    if len(scores) > 0:
        high_score = float(scores[0].strip())

def draw():
    window.blit(background, (0,0))
    window.blit(bird.img, bird) #image, coordinates

    for pipe in pipes:
        window.blit(pipe.img, pipe)
 
    text_str_score = str(int(score))
    text_font = pygame.font.Font("fonts/04B_19.TTF", 40)

    if game_over:
        text_str_score = "Score: " + text_str_score
        text_high_score = "High Score: " + str(int(high_score))

        text_render_score = text_font.render(text_str_score, False, "black")
        text_render_high_score = text_font.render(text_high_score, False, "black")

        score_rect = text_render_score.get_rect(center=(GAME_WIDTH/2, 100))
        high_rect = text_render_high_score.get_rect(center=(GAME_WIDTH/2, GAME_HEIGHT-125))
        
        window.blit(text_render_score, score_rect)
        window.blit(text_render_high_score, high_rect)
        window.blit(over_msg, over_msg_rect)
    else:
        text_render_score = text_font.render(text_str_score, False, "white")
        window.blit(text_render_score, (GAME_WIDTH/2,5))

def move():
    global velocity_y, score, game_over

    velocity_y += gravity
    bird.y += velocity_y
    bird.y = max(bird.y, 0)

    if bird.y > GAME_HEIGHT: #if bird falls off screen
        game_over = True
        die_sound.play()
        return

    for pipe in pipes:
        pipe.x += velocity_x

        if not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 0.5
            pipe.passed = True
            if score % 1 == 0:
                point_sound.play()
        
        if bird.colliderect(pipe):
            game_over = True
            hit_sound.play()
            # pipes.clear()
            # draw()
            return

    while len(pipes) > 0 and pipes[0].x < -pipe_width:
        pipes.pop(0)

def create_pipes():
    random_pipe_y = pipe_y - pipe_height/4 - random.random()*(pipe_height/2) #0-h/2
    opening_space = GAME_HEIGHT/4

    top_pipe = Pipe(top_pipe_img)
    top_pipe.y = random_pipe_y
    pipes.append(top_pipe)

    bottom_pipe = Pipe(bottom_pipe_img)
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_space
    pipes.append(bottom_pipe)

    print(len(pipes))

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird!")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

create_pipes_timer = pygame.USEREVENT + 0 #max is 9, this is the first event
pygame.time.set_timer(create_pipes_timer, 1500)

# audios
flap_sound = pygame.mixer.Sound("audio/sfx_wing.wav")
die_sound = pygame.mixer.Sound("audio/sfx_die.wav")
hit_sound = pygame.mixer.Sound("audio/sfx_hit.wav") #hit the pip
point_sound = pygame.mixer.Sound("audio/sfx_point.wav")


#game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == create_pipes_timer and not game_over:
            create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key  in (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_RETURN, pygame.K_KP_ENTER):
                velocity_y = -6
                flap_sound.play()

                #reset game
                if game_over:
                    bird.y = bird_y
                    pipes.clear()

                    """
                        once the game is over, it highschores and adds the new score 
                        it makes sure that there are only 10 high scores so it eliminates
                        scores as necessary
                    """
                    with open("high_scores.txt", "r+") as f: 
                        content = f.readlines() 
                        scores =[]

                        #get and add the new score
                        for s in content:
                            scores.append(float(s))
                        scores.append(score)
                        scores.sort(reverse=True)
                        
                        high_score = float(scores[0])

                        #keep a maxmun of 10 highscores
                        if len(scores) > 10:
                            scores = scores[:10]
                        # print("Past ", end=" ")
                        
                        f.seek(0) #go back to the start

                        f.truncate() #erases old content

                        for s in scores: 
                            f.write(f"{s}\n")

                    score = 0  
                    game_over = False
        
    if not game_over:
        move()
        draw()
        pygame.display.update()
        clock.tick(60)