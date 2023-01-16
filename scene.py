from model import *
import glm
import Carrier
import pygame
import Mixer
import random
import threading
import time

def Bresenham3D(x1, y1, z1, x2, y2, z2):
    ListOfPoints = []
    ListOfPoints.append((x1, y1, z1))
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    if (x2 > x1):
        xs = 1
    else:
        xs = -1
    if (y2 > y1):
        ys = 1
    else:
        ys = -1
    if (z2 > z1):
        zs = 1
    else:
        zs = -1

    # Driving axis is X-axis"
    if (dx >= dy and dx >= dz):
        p1 = 2 * dy - dx
        p2 = 2 * dz - dx
        while (x1 != x2):
            x1 += xs
            if (p1 >= 0):
                y1 += ys
                p1 -= 2 * dx
            if (p2 >= 0):
                z1 += zs
                p2 -= 2 * dx
            p1 += 2 * dy
            p2 += 2 * dz
            ListOfPoints.append((x1, y1, z1))

    # Driving axis is Y-axis"
    elif (dy >= dx and dy >= dz):
        p1 = 2 * dx - dy
        p2 = 2 * dz - dy
        while (y1 != y2):
            y1 += ys
            if (p1 >= 0):
                x1 += xs
                p1 -= 2 * dy
            if (p2 >= 0):
                z1 += zs
                p2 -= 2 * dy
            p1 += 2 * dx
            p2 += 2 * dz
            ListOfPoints.append((x1, y1, z1))

    # Driving axis is Z-axis"
    else:
        p1 = 2 * dy - dz
        p2 = 2 * dx - dz
        while (z1 != z2):
            z1 += zs
            if (p1 >= 0):
                y1 += ys
                p1 -= 2 * dz
            if (p2 >= 0):
                x1 += xs
                p2 -= 2 * dz
            p1 += 2 * dy
            p2 += 2 * dx
            ListOfPoints.append((x1, y1, z1))
    return ListOfPoints

def Background_music():
    while True:
        music_list = ["Subwoofer Lullaby", "Clark", "Dry Hands", "Equinoxe", "Minecraft",
                    "Haggstrom", "Moog City", "Oxygene", "Sweden", "Wet Hands"]
        Mixer.audio.PlaySound("Content/Audio/Music/" + random.choice(music_list) + ".mp3")
        time.sleep(5 * 60)

class Scene:
    def __init__(self, app):
        self.app = app
        self.objects = []
        self.load()
        # skybox
        self.skybox = AdvancedSkyBox(app)
        self.pressed = False
        self.texture = 0
        self.mForce = glm.vec3(0, 0, 0)

    def add_object(self, obj):
        self.objects.append(obj)

    def load(self):
        app = self.app
        add = self.add_object

        x = threading.Thread(target=Background_music)
        x.start()

        # floor
        n, s = 20, 1
        for x in range(-n, n, s):
            for z in range(-n, n, s):
                add(Cube(app, pos=(x, -s, z)))

    def update(self):
        velocity = 0.005 * Carrier.carry.GetDeltaTime()
        direction = glm.vec3(self.app.camera.forward.x, 0, self.app.camera.forward.z)
        perp = glm.vec3(-direction.z, 0, direction.x)
        keys = pygame.key.get_pressed()
        update = glm.vec3(0, 0, 0)

        if keys[pygame.K_SPACE]:
            if not self.pressed:
                list_of_points = Bresenham3D(int(self.app.camera.position.x),
                                            int(self.app.camera.position.y),
                                            int(self.app.camera.position.z),
                                            int((self.app.camera.position.x + self.app.camera.forward.x * 10)),
                                            int((self.app.camera.position.y + self.app.camera.forward.y * 10)),
                                            int((self.app.camera.position.z + self.app.camera.forward.z * 10)))

                last_pos = glm.vec3(int(self.app.camera.position.x),
                                    int(self.app.camera.position.y),
                                    int(self.app.camera.position.z))

                for i in list_of_points:
                    for j in self.objects:
                        if i == j.pos:
                            self.pressed = True
                            self.add_object(Cube(self.app, pos= last_pos, tex_id= self.texture))
                            return
                    last_pos = i


                self.pressed = True
        else:
            self.pressed = False

        if keys[pygame.K_BACKSPACE]:
            list_of_points = Bresenham3D(int(self.app.camera.position.x),
                                        int(self.app.camera.position.y),
                                        int(self.app.camera.position.z),
                                        int((self.app.camera.position.x + self.app.camera.forward.x * 10)),
                                        int((self.app.camera.position.y + self.app.camera.forward.y * 10)),
                                        int((self.app.camera.position.z + self.app.camera.forward.z * 10)))

            last_pos = glm.vec3(int(self.app.camera.position.x),
                                int(self.app.camera.position.y),
                                int(self.app.camera.position.z))

            for i in list_of_points:
                for j in self.objects:
                    if i == j.pos:
                        self.pressed = True
                        self.objects.remove(j)
                        return
                last_pos = i

        stepping = False

        for i in self.objects:
            if i.pos == glm.vec3(int(self.app.camera.position.x),
                                        int(self.app.camera.position.y) - 2,
                                        int(self.app.camera.position.z)):
                stepping = True
                break

        if keys[pygame.K_u] and stepping:
            self.mForce += glm.vec3(0, 0.2, 0)

        if not stepping:
            self.mForce.y -= 0.016
        elif self.mForce.y < 0:
            self.mForce.y = 0

        self.app.camera.position += self.mForce

        update = glm.vec3(0, 0, 0)

        if keys[pygame.K_w]:
            update += direction * velocity
        if keys[pygame.K_s]:
            update -= direction * velocity
        if keys[pygame.K_a]:
            update -= perp * velocity
        if keys[pygame.K_d]:
            update += perp * velocity

        if keys[pygame.K_1]:
            self.texture = 0
        elif keys[pygame.K_2]:
            self.texture = 1
        elif keys[pygame.K_3]:
            self.texture = 2
        elif keys[pygame.K_3]:
            self.texture = 3
        elif keys[pygame.K_4]:
            self.texture = 4
        elif keys[pygame.K_5]:
            self.texture = 5
        elif keys[pygame.K_6]:
            self.texture = 6
        elif keys[pygame.K_7]:
            self.texture = 7
        elif keys[pygame.K_8]:
            self.texture = 8
        elif keys[pygame.K_9]:
            self.texture = 9
        elif keys[pygame.K_0]:
            self.texture = 10

        if update.x != 0 and update.z != 0:
            block = False
            for i in self.objects:
                if i.pos == glm.vec3(int(self.app.camera.position.x + update.x),
                                     int(self.app.camera.position.y),
                                     int(self.app.camera.position.z + glm.normalize(update).z)):
                    block = True
                    break

                if i.pos == glm.vec3(int(self.app.camera.position.x + update.x),
                                     int(self.app.camera.position.y) - 1,
                                     int(self.app.camera.position.z + update.z)):
                    block = True
                    break

            if not block:
                self.app.camera.position += glm.normalize(update) / 10

        rel_x, rel_y = pygame.mouse.get_rel()
        self.app.camera.yaw += rel_x * 0.05
        self.app.camera.pitch = max(-89.99, min(89.99, self.app.camera.pitch - rel_y * 0.05))


    def render(self):
        for obj in self.objects:
            obj.render()
        self.skybox.render()