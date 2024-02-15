import pygame,math,random,time
from UIpygame import PyUI as pyui
pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()

class Vector2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __add__(self,vec):
        return Vector2(self.x+vec.x,self.y+vec.y)
    def __sub__(self,vec):
        return Vector2(self.x-vec.x,self.y-vec.y)
    def __mul__(self,vec):
        return Vector2(self.x*vec.x,self.y*vec.y)
    def __truediv__(self,vec):
        return Vector2(self.x/vec.x,self.y/vec.y)
    def magnitude(self):
        return ((self.x)**2+(self.y)**2)**0.5
    def angle(self):
        return math.atan2(self.y,self.x)

def root(x):
    if x<0: return -((-x)**0.5)
    else: return x**0.5
  
class Ball:
    def __init__(self,system,x=-1,y=-1,v1=-1,v2=-1,r=-1):
        if v1 == -1: v1 = random.gauss(0,4)
        if v2 == -1: v2 = random.gauss(0,4)
        if r == -1: r = random.random()/2+0.3
        if x == -1: x = random.random()*(system.width-r*2)+r
        if y == -1: y = random.random()*(system.height-r*2)+r
        
        self.x = x
        self.y = y
        self.velocity = Vector2(v1,v2)
        self.energy = 0
        self.r = r
        self.mass = math.pi*self.r**2
        self.restitution = 0.6
        self.friction = 0.6
        
        
        self.col = [random.randint(0,255) for a in range(3)]
    def draw(self,surf,system):
        pygame.draw.circle(surf,self.col,(self.x*system.scale,self.y*system.scale),self.r*system.scale)
    def physics(self,system):

        self.prepos = Vector2(self.x,self.y)
        
        self.velocity.y+=9.81*system.delta_time
        self.x+=self.velocity.x*system.delta_time
        self.y+=self.velocity.y*system.delta_time
        self.energy = 0.5*self.mass*self.velocity.magnitude()**2+9.81*self.mass*(system.height-self.y-self.r)
        

        self.check_wall_collisions(system)
        
        self.deltaR = self.prepos-Vector2(self.x,self.y)
        if self.deltaR.magnitude() < 0.00001:
            self.velocity = Vector2(random.gauss(0,3),-random.random()*20)
        
    def check_wall_collisions(self,system):
        e = self.restitution*system.wall_restitution
        mu = self.friction*system.wall_friction
        if self.x-self.r<0:
            self.x = self.r
            self.solid_collide(system,-math.pi/2,e,mu)
        elif self.x+self.r>system.width:
            self.x = system.width-self.r
            self.solid_collide(system,math.pi/2,e,mu)
        if self.y-self.r<0:
            self.y = self.r
            self.solid_collide(system,0,e,mu)
        elif self.y+self.r>system.height:
            self.y = system.height-self.r
            self.solid_collide(system,0,e,mu)


    def solid_collide(self,system,theta,e,mu):
        # Bounce
        prevx = self.velocity.x
        prevy = self.velocity.y
        
        self.velocity.x = abs(self.velocity.x)*-math.sin(theta)*e + self.velocity.x*abs(math.cos(theta))
        self.velocity.y = abs(self.velocity.y)*-math.cos(theta)*e + self.velocity.y*abs(math.sin(theta))

        # Friction

        x_impulse = self.mass*(prevx-self.velocity.x)
        y_impulse = self.mass*(prevy-self.velocity.y)

        x_friction_energy = max(min(mu*y_impulse*abs(self.velocity.x)*system.delta_time*60,0.5*self.mass*self.velocity.x**2),0)
        y_friction_energy = max(min(mu*x_impulse*abs(self.velocity.y)*system.delta_time*60,0.5*self.mass*self.velocity.y**2),0)
        
        if self.velocity.x!=0: self.velocity.x = ((0.5*self.mass*self.velocity.x**2-x_friction_energy)*2/self.mass)**0.5*(self.velocity.x/abs(self.velocity.x))
        if self.velocity.y!=0: self.velocity.y = ((0.5*self.mass*self.velocity.y**2-y_friction_energy)*2/self.mass)**0.5*(self.velocity.y/abs(self.velocity.y))
        
    
    def vector_to_modarg(self):
        self.vel = self.velocity.magnitude()
        self.angle = self.velocity.angle()
    def modarg_to_vector(self):
        self.velocity.x = self.vel*math.cos(self.angle)
        self.velocity.y = self.vel*math.sin(self.angle)


class System:
    def __init__(self):
        self.scale = 100 # Pixels per meter
        self.grid_cell_size = 100 # cell size for grid algorithm
        self.width = 10  ## meters
        self.height = 8  ## meters
        
        self.width_pixels = self.width*self.scale
        self.height_pixels = self.height*self.scale
        self.x = 100
        self.y = 50
        self.border = 5
        self.time_tracker = time.perf_counter()

        self.speed_mul = 0.6

        self.wall_restitution = 0.5
        self.wall_friction = 0.8

        self.circles = [Ball(self) for a in range(50)]
##        self.circles = [Ball(self,0.5,7.5,1,0,0.5)]

    def draw(self,screen):
        surf = pygame.Surface((self.width_pixels,self.height_pixels))
        surf.fill((200,200,200))

        for y in range(self.height+1):
            pygame.draw.line(surf,(230,230,230),(0,y*self.scale),(self.width_pixels,y*self.scale),1)
        for x in range(self.width+1):
            pygame.draw.line(surf,(230,230,230),(x*self.scale,0),(x*self.scale,self.height_pixels),1)
            
        system_energy = 0
        for c in self.circles:
            c.draw(surf,self)
            system_energy+=c.energy
        ui.write(surf,5,5,str(int(system_energy))+'J',30,(15,15,15),False)

        pygame.draw.rect(screen,(150,150,150),(self.x-self.border,self.y-self.border,self.width_pixels+self.border*2,self.height_pixels+self.border*2),self.border)
        screen.blit(surf,(self.x,self.y))

    def physics(self):
        self.collision_grid = [[[] for x in range(self.width_pixels//self.grid_cell_size)] for y in range(self.height_pixels//self.grid_cell_size)]

        for c in self.circles:
            x = max(min(int((c.x*self.scale)//self.grid_cell_size),len(self.collision_grid[0])-1),0)
            y = max(min(int((c.y*self.scale)//self.grid_cell_size),len(self.collision_grid)-1),0)
            c.collision_grid_x = x
            c.collision_grid_y = y
            self.collision_grid[y][x].append(c)

        for c in self.circles:
            c.physics(self)
        
    def tick(self,screen):
        t = time.perf_counter()
        self.delta_time = (t-self.time_tracker)*self.speed_mul
        self.time_tracker = t
        
        
        self.draw(screen)
        self.physics()


system = System()

while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
    screen.fill(pyui.Style.wallpapercol)

    system.tick(screen)
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
