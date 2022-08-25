import pygame
from vector import Vector

class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
    
    def sdf(self, point):
        return (point - self.center).get_norm() - self.radius

    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (self.center.x, self.center.y), self.radius)

class Box:
    def __init__(self, center, half_size):
        self.center = center
        self.half_size = half_size

    def sdf(self, point):
        corner_offset = (point - self.center).absolute() - self.half_size

        distance_outside = Vector(max(corner_offset.x, 0), max(corner_offset.y, 0)).get_norm()
        offset_inside = Vector(min(corner_offset.x, 0), min(corner_offset.y, 0))
        distance_inside = max(offset_inside.x, offset_inside.y)

        return distance_inside + distance_outside

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, pygame.Rect(self.center.x - self.half_size.x, self.center.y - self.half_size.y, self.half_size.x * 2, self.half_size.y * 2))

class Capsule:
    def __init__(self, focus1, focus2, thickness):
        self.focus1 = focus1
        self.focus2 = focus2
        self.thickness = thickness
    
    def sdf(self, point):
        focus_offset = point - self.focus1
        capsule_core = self.focus2 - self.focus1
        clamped_projection_length = max(0, min(focus_offset.dot(capsule_core) / (capsule_core.get_norm() ** 2), 1))
        return (focus_offset - (capsule_core * clamped_projection_length)).get_norm() - self.thickness
    
    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (self.focus1.x, self.focus1.y), self.thickness)
        pygame.draw.circle(surface, color, (self.focus2.x, self.focus2.y), self.thickness)
        offset = (self.focus2 - self.focus1).normal().normalize() * self.thickness
        points = (self.focus1 + offset, self.focus1 - offset, self.focus2 - offset, self.focus2 + offset)
        pygame.draw.polygon(surface, color, [(point.x, point.y) for point in points])

def ray_cast(shapes, origin, direction):
    tip = origin
    circles = []

    # while the minimum distance to an obstacle is more than 0
    while True:

        # find the minimum distance to an obstacle
        for i in range(len(shapes)):
            distance = shapes[i].sdf(tip)
            if i == 0 or distance < min_distance:
                min_distance = distance
                target = i

        # if the distance is 0 the ray_cast has hit something
        if round(min_distance) == 0:
            return tip, target, circles
        
        circles.append((tip, min_distance))
        # move the position from which to find the minimum distance to the edge of the last minimum distance
        tip += direction * min_distance

        # stop the ray from shooting into infinity
        if (tip.x < 0 or tip.x > 1280 or tip.y < 0 or tip.y > 720):
            return tip, None, circles

#main function
def main():
    # initialize the pygame module
    pygame.init()
    
    #create a surface on screen that has the size of 1280 x 720
    screen = pygame.display.set_mode((1280, 720))
    
    #define a variable to control the main loop
    running = True

    #define variables
    shapes = (Circle(Vector(300, 300), 100), Circle(Vector(500, 600), 50), Box(Vector(1000, 600), Vector(100, 50)), Capsule(Vector(900, 100), Vector(700, 500), 50))
    origin = Vector(0, 0)
    direction = Vector(3, 1).normalize()

    #main loop
    while running:

        screen.fill((255, 255, 255))

        #launch a ray cast from the position of the mouse
        hit_location, target, circles = ray_cast(shapes, origin, direction)

        #draw the obstacles
        for i in range(len(shapes)):
            color = (0, 0, 0)
            if i == target:
                color = (150, 0, 0)
            shapes[i].draw(screen, color)

        #draw the distance circles of the raymarch
        for i in range(len(circles)):
            pygame.draw.circle(screen, (255, 0, 0), (circles[i][0].x, circles[i][0].y), circles[i][1], 1)
        
        #draw the ray and its hit location
        for i in range(len(circles) - 1):
            pygame.draw.line(screen, (255, 0, 0), (circles[i][0].x, circles[i][0].y), (circles[i+1][0].x, circles[i+1][0].y), 3)
        if len(circles) > 0:
            pygame.draw.line(screen, (255, 0, 0), (circles[-1][0].x, circles[-1][0].y), (hit_location.x, hit_location.y), 3)
            if target != None:
                pygame.draw.line(screen, (255, 0, 0), (hit_location.x - 15, hit_location.y - 15), (hit_location.x + 15, hit_location.y + 15), 3)
                pygame.draw.line(screen, (255, 0, 0), (hit_location.x + 15, hit_location.y - 15), (hit_location.x - 15, hit_location.y + 15), 3)
        
        pygame.display.flip()
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # exit the main loop
                running = False
            # call quit event if escape is pressed
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
            # set ray origin to mouse position
            elif event.type == pygame.MOUSEMOTION:
                origin = Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()