import pygame
import math

class CelestialBody:
    def __init__(self, x, y, mass, radius, color, is_static=False):
        self.mass = mass
        self.radius = radius
        self.color = color
        self.is_static = is_static
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.trail = []

    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, (255, 255, 255), False, self.trail, 1)
        if self.is_static:  # or any condition you want
            pygame.draw.circle(screen, (255, 109, 11), (int(self.pos.x), int(self.pos.y)), self.radius + 2, 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.radius + 10, 4)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def apply_force(self, force):
        if not self.is_static:
            self.acc += force / self.mass

    def update(self, dt):
        if not self.is_static:
            self.vel += self.acc * dt
            self.pos += self.vel * dt
        self.acc = pygame.Vector2(0, 0)
        self.trail.append(self.pos.copy())
        if len(self.trail) > 1000:
            self.trail.pop(0)


class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.bodies = []
        self.clock = pygame.time.Clock()
        self.running = True
        self.G = 100
        self.dt = 0
        pygame.display.set_caption("Space Simulation")

    def add_body(self, body):
        self.bodies.append(body)

    def compute_gravity(self, b1, b2):
        direction = b2.pos - b1.pos
        distance = max(direction.length_squared(), 100)
        force_mag = self.G * b1.mass * b2.mass / distance
        force = direction.normalize() * force_mag
        return force

    def check_collision(self, b1, b2):
        distance = (b1.pos - b2.pos).length()
        return distance <= (b1.radius - b2.radius)

    def handle_collision(self, b1, b2):
        total_mass = b1.mass + b2.mass
        total_radius = b1.radius + b2.radius
        new_vel = (b1.vel * b1.mass + b2.vel * b2.mass) / total_mass
        new_pos = (b1.pos * b1.mass + b2.pos * b2.mass) / total_mass

        if b1.is_static or b2.is_static:
            new_body = CelestialBody(new_pos.x, new_pos.y, total_mass, b1.radius if b1.is_static else b2.radius, (0, 0, 0), True)
        else:
            new_body = CelestialBody(new_pos.x, new_pos.y, total_mass, total_radius, (255, 206, 41))
        return new_body

    def update_physics(self):
        for i, b1 in enumerate(self.bodies):
            for b2 in self.bodies[i+1:]:
                if self.check_collision(b1, b2):
                    new_body = self.handle_collision(b1, b2)
                    self.bodies.append(new_body)
                    self.bodies.remove(b1)
                    self.bodies.remove(b2)
                force = self.compute_gravity(b1, b2)
                b1.apply_force(force)
                b2.apply_force(-force)
        for body in self.bodies:
            body.update(self.dt)

    def compute_orbit_vel(self, planet, star):
        r_vec = planet.pos - star.pos
        speed = math.sqrt(self.G * star.mass / r_vec.length())
        tangential_dir = pygame.Vector2(-r_vec.y, r_vec.x).normalize()
        planet.vel = tangential_dir * speed

    def draw(self):
        self.screen.fill((0, 0, 0))
        for body in self.bodies:
            body.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.update_physics()
            self.draw()
        pygame.quit()

def main():
    width, height = 1000, 1000
    sim = Simulation()

    star = CelestialBody(width // 2, height // 2, 30000, 100, (0, 0, 0), True)
    sim.add_body(star)

    planet = CelestialBody(width // 2 - 75 - star.radius, height // 2, 200, 20, (77, 157, 236))
    sim.add_body(planet)

    planet2 = CelestialBody(width // 2 + 200 + star.radius, height // 2, 300, 15, (85, 168, 101))
    sim.add_body(planet2)

    planet3 = CelestialBody(width // 2, height // 2 - 100 - star.radius, 100, 25, (192, 139, 219))
    sim.add_body(planet3)

    sim.compute_orbit_vel(planet, star)
    sim.compute_orbit_vel(planet2, star)
    sim.compute_orbit_vel(planet3, star)
    sim.run()

if __name__ == '__main__':
    main()


