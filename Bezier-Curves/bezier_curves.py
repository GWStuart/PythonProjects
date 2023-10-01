import pygame
import pygame.gfxdraw
import math


class Game:
    LENGTH, WIDTH = 800, 600

    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((Game.LENGTH, Game.WIDTH))
        pygame.display.set_caption("Bezier Curves")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("freesansbold.ttf", 15)

        self.draw_segments = True
        self.draw_path = True
        self.point_r = 5
        self.animate = False
        self.pause = False

        self.lines = []
        self.points = []
        self.path = []
        self.t = 0
        self.drag = False

        self.run = True
        while self.run:
            self.mainloop()

    def mainloop(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed(3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for l in self.lines:
                    print(l)
                self.run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.animate:
                    for p in self.points:
                        if math.dist(mouse, p) < self.point_r:
                            break
                    else:
                        self.points.append(mouse)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.animate:
                        self.lines = []
                        for i in range(len(self.points) - 1):
                            self.lines.append(Line(self.win, self.points[i], self.points[i+1]))
                    else:  # todo when space clicked don't clear everything
                        self.t = 0
                        self.path = []
                    self.animate = not self.animate
                if event.key == pygame.K_c:
                    self.animate = False
                    self.draw_segments = True
                    self.pause = False
                    self.t = 0
                    self.lines = []
                    self.points = []
                    self.path = []
                if event.key == pygame.K_h and self.animate:
                    self.draw_segments = not self.draw_segments
                if event.key == pygame.K_DELETE and not self.animate:
                    for p in self.points:
                        if math.dist(mouse, p) < self.point_r:
                            self.points.remove(p)
                            break
                if event.key == pygame.K_o:
                    self.draw_path = not self.draw_path
                if event.key == pygame.K_p and self.animate:
                    self.pause = not self.pause
                    self.path = []
                    self.t = 0

        self.win.fill((90, 105, 242))

        if self.animate:
            if self.pause:
                for segment in self.lines:
                    segment.draw()
                self.draw_curve()
                # pygame.gfxdraw.bezier(self.win, self.points, 100, (255, 0, 0))

                if self.drag:
                    if not pressed[0]:
                        self.drag = False
                    else:
                        if self.drag[1]:
                            self.drag[1][0].update_points(mouse, self.drag[1][0].p2)
                        if self.drag[2]:
                            self.drag[2][0].update_points(self.drag[2][0].p1, mouse)
                        self.points[self.drag[0]] = mouse
                else:
                    if pressed[0]:
                        for p in self.points:
                            if math.dist(mouse, p) < self.point_r:
                                self.drag = (self.points.index(p), tuple(filter(lambda x: x.p1 == p, self.lines)),
                                             tuple(filter(lambda x: x.p2 == p, self.lines)))
                                break
            else:
                p = self.bezier_curve(self.t, draw_curve=self.draw_segments, draw_last_point=True)
                self.path.append(p)

                if len(self.path) > 1 and self.draw_path:
                    pygame.draw.lines(self.win, (255, 255, 255), False, self.path, 4)
                # for p in self.path:
                #     pygame.draw.circle(self.win, (0, 0, 255), p, 2)

                self.t += 0.005
                if self.t > 1:
                    self.t = 0
                    self.path = []

            t_text = self.font.render(f"t = {round(self.t, 2)}", True, (0, 0, 0))
            self.win.blit(t_text, (10, 10))
        else:
            if len(self.points) > 1:
                pygame.draw.lines(self.win, (0, 0, 0), False, self.points, 3)
                for point in self.points:
                    pygame.draw.circle(self.win, (255, 255, 255), point, self.point_r)
            elif len(self.points) > 0:
                pygame.draw.circle(self.win, (255, 255, 255), self.points[0], self.point_r)

        pygame.display.update()
        self.clock.tick(60)

    def bezier_curve(self, t, draw_curve=False, draw_last_point=False):
        lines_current = self.lines.copy()
        points_current = [1, 2, 3]
        while len(points_current) > 1:
            points_current = []
            for segment in lines_current:
                if draw_curve:
                    segment.draw()
                points_current.append(segment.lerp(t, draw=draw_curve))
            lines_current = []
            for i in range(len(points_current) - 1):
                lines_current.append(Line(self.win, points_current[i], points_current[i + 1]))
        if draw_last_point:
            pygame.draw.circle(self.win, (0, 255, 0), points_current[0], 4)
        return points_current[0]

    def draw_curve(self, precision=0.005):
        points = []
        i = 0
        while i <= 1:
            i += precision
            points.append(self.bezier_curve(i))

        if len(points) > 1:
            pygame.draw.lines(self.win, (255, 255, 255), False, points, 4)
        # for p in points:
        #     pygame.draw.circle(self.win, (0, 0, 255), p, 2)


class Line:
    def __init__(self, win, p1, p2):
        self.win = win
        self.p1 = p1
        self.p2 = p2
        self.dir = 1 if self.p1[0] <= self.p2[0] else -1
        if self.p1[0] == self.p2[0]:
            self.dir = 1 if self.p1[1] < self.p2[1] else -1

    def update_points(self, new_p1, new_p2):
        self.p1 = new_p1
        self.p2 = new_p2
        self.dir = 1 if self.p1[0] <= self.p2[0] else -1
        if self.p1[0] == self.p2[0]:
            self.dir = 1 if self.p1[1] < self.p2[1] else -1

    def draw(self):
        pygame.draw.line(self.win, (0, 0, 0), self.p1, self.p2, 3)
        pygame.draw.circle(self.win, (255, 255, 255), self.p1, 5)
        pygame.draw.circle(self.win, (255, 255, 255), self.p2, 5)

    def lerp(self, t, draw=False):
        point = (((1 - t) * self.p1[0] + (t * self.p2[0])), ((1 - t) * self.p1[1] + (t * self.p2[1])))
        if draw:
            pygame.draw.circle(self.win, (0, 255, 0), point, 5)
        return point

    def __str__(self):
        return f"Line(self.win, {self.p1}, {self.p2})"


if __name__ == '__main__':
    Game()
