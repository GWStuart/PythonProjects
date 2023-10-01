import pygame, random
pygame.init()
 
LENGTH, WIDTH = 1280, 720
win = pygame.display.set_mode((LENGTH, WIDTH), pygame.FULLSCREEN)
pygame.display.set_caption("Matrix Rain")
clock = pygame.time.Clock()
 
grid_width = 7
frequency = 70  # inversely proportional
chr_range = (33, 126)
 
colour = (0, 255, 0)
 
 
class Character:
    FONT = pygame.font.Font(None, grid_width * 2)
 
    def __init__(self, value, pos, colour=(0, 255, 0)):
        self.value = value
        self.pos = pos
        self.original = Character.FONT.render(chr(self.value), True, colour)
        self.alpha_img = pygame.Surface(self.original.get_size(), pygame.SRCALPHA)
        self.transparency = 255
 
        self.fade_speed = 3
 
    def draw(self):
        text = self.original.copy()
        self.alpha_img.fill((255, 255, 255, self.transparency))
        text.blit(self.alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        win.blit(text, self.pos)
 
        self.transparency -= self.fade_speed
        if self.transparency < 0:
            characters.remove(self)
 
 
characters = []
columns = [0] * (LENGTH // grid_width)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
 
    for column in range(len(columns)):
        if columns[column] == 0:
            if random.randint(0, frequency) == 0:
                characters.append(Character(random.randint(chr_range[0], chr_range[1]), (column * grid_width, 0),
                                            colour=colour))
                columns[column] += 1
        else:
            characters.append(Character(random.randint(chr_range[0], chr_range[1]),
                                        (column * grid_width, columns[column] * grid_width), colour=colour))
            columns[column] += 1
            if columns[column] * grid_width > WIDTH:
                columns[column] = 0
 
    win.fill((0, 0, 0))
    for character in characters:
        character.draw()
 
    pygame.display.update()
