from ECSystem import *
import glm
import pygame
import Mixer
import random
import threading
import time
from Gameplay import Cube
import Skybox
import GraphicsPipeline
import VoxelPhysicSystem

# importing all files  from tkinter
from tkinter import *
from tkinter import ttk

# import only asksaveasfile from filedialog
# which is used to save file in any extension
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfilename

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
        self.skybox = Skybox.SkyBox(tex_id='Content/Textures/skybox1/')
        self.pressed = False
        self.texture = 'Content/Textures/img.png'
        self.mForce = glm.vec3(0, 0, 0)
        self.x = threading.Thread(target=Background_music)
        self.x.start()
        self.moving = False
        self.getTicksLastFrame = 0

    def add_object(self, obj):
        self.objects.append(obj)

    def load(self):
        app = self.app
        add = self.add_object

        VoxelPhysicSystem.Physx.SetBounds(glm.vec3(-250, -5, -250), glm.vec3(250, 250, 250))
        VoxelPhysicSystem.Physx.Setup()

        # floor
        n, s = 20, 1
        for x in range(-n, n, s):
            for z in range(-n, n, s):
                add(Cube.Cube(pos=glm.vec3(x, -s, z), tex_id= 'Content/Textures/img_5.png'))

    def SaveScene(self):
        files = [('Minepy map', '*.mnpy')]
        with asksaveasfile(filetypes=files, defaultextension=files) as file:
            savestring = ""
            for x in self.objects:
                savestring += str(x.mTransform.mPosition.x) + "$" + \
                              str(x.mTransform.mPosition.y) + "$" + \
                              str(x.mTransform.mPosition.z) + "$"
                savestring += x.mComponents[0].tex_id + "$"

            file.write(savestring)
            file.close()

    def OpenScene(self):
        self.objects.clear()
        files = [('Minepy map', '*.mnpy')]

        file_name = askopenfilename(filetypes=files, defaultextension=files)

        with open(file_name, "r") as file:
            savestring = file.read().split('$')

            for i in range(int(len(savestring) / 4)):
                pos_x = int(float(savestring[i * 4 + 0]))
                pos_y = int(float(savestring[i * 4 + 1]))
                pos_z = int(float(savestring[i * 4 + 2]))
                texture = savestring[i * 4 + 3]
                self.objects.append(Cube.Cube(pos=glm.vec3(pos_x, pos_y, pos_z), tex_id= texture))

    def update(self):
        velocity = 0.005 * GraphicsPipeline.Gfx.GetDeltaTime()
        direction = glm.vec3(self.app.camera.forward.x, 0, self.app.camera.forward.z)
        perp = glm.vec3(-direction.z, 0, direction.x)
        keys = pygame.key.get_pressed()
        update = glm.vec3(0, 0, 0)

        if keys[pygame.K_SPACE]:
            if not self.pressed:
                raycast = VoxelPhysicSystem.Physx.RaycastClosestPointInmediatePrevious(self.app.camera.position, self.app.camera.forward)

                if raycast != self.app.camera:
                    self.pressed = True
                    self.add_object(Cube.Cube(pos=glm.vec3(raycast[0], raycast[1], raycast[2]), tex_id=self.texture))
                    Mixer.audio.PlaySound("Content/Audio/Sfx/PlacingBlock.mp3")

                self.pressed = True
        else:
            self.pressed = False

        if keys[pygame.K_BACKSPACE]:
            raycast = VoxelPhysicSystem.Physx.RaycastClosestPoint(self.app.camera.position, self.app.camera.forward)

            if raycast != self.app.camera:
                for j in self.objects:
                    if j.mTransform.mPosition == raycast:
                        self.pressed = True
                        j.Destroy()
                        self.objects.remove(j)
                        Mixer.audio.PlaySound("Content/Audio/Sfx/Remove.mp3")
                        return

        stepping = VoxelPhysicSystem.Physx.IsColliding(self.app.camera.position, glm.vec3(0, -2, 0))

        if keys[pygame.K_u] and stepping:
            self.mForce += glm.vec3(0, 0.2, 0)

        if not stepping:
            self.mForce.y -= 0.016
        elif self.mForce.y < 0:
            self.mForce.y = 0
            self.app.camera.mPostition.y = int(self.app.camera.mPostition.y)

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
            self.texture = 'Content/Textures/img.png'
        elif keys[pygame.K_2]:
            self.texture = 'Content/Textures/img_1.png'
        elif keys[pygame.K_3]:
            self.texture = 'Content/Textures/img_2.png'
        elif keys[pygame.K_3]:
            self.texture = 'Content/Textures/img_3.png'
        elif keys[pygame.K_4]:
            self.texture = 'Content/Textures/img_4.png'
        elif keys[pygame.K_5]:
            self.texture = 'Content/Textures/img_5.png'
        elif keys[pygame.K_6]:
            self.texture = 'Content/Textures/img_6.png'
        elif keys[pygame.K_7]:
            self.texture = 'Content/Textures/img_7.png'
        elif keys[pygame.K_8]:
            self.texture = 'Content/Textures/img_8.png'
        elif keys[pygame.K_9]:
            self.texture = 'Content/Textures/img_9.png'
        elif keys[pygame.K_0]:
            self.texture = 'Content/Textures/img_10.png'

        if keys[pygame.K_o]:
            self.SaveScene()

        if keys[pygame.K_i]:
            self.OpenScene()

        if update.x != 0 and update.z != 0:
            block = VoxelPhysicSystem.Physx.IsColliding(self.app.camera.position,
                glm.normalize(update)) or VoxelPhysicSystem.Physx.IsColliding(
                self.app.camera.position - glm.vec3(0, 1, 0), glm.normalize(update))

            if not block:
                self.app.camera.position += glm.normalize(update) / 10

                if not self.moving:
                    Mixer.audio.PlaySound("Content/Audio/Sfx/Footsteps.mp3", -1)
                self.moving = True
            else:
                if self.moving:
                    Mixer.audio.Pause("Content/Audio/Sfx/Footsteps.mp3")
                self.moving = False
        else:
            if self.moving:
                Mixer.audio.Pause("Content/Audio/Sfx/Footsteps.mp3")
            self.moving = False

        rel_x, rel_y = pygame.mouse.get_rel()
        self.app.camera.yaw += rel_x * 0.05
        self.app.camera.pitch = max(-89.99, min(89.99, self.app.camera.pitch - rel_y * 0.05))

    def render(self):
        #t = pygame.time.get_ticks()
        # deltaTime in seconds.
        #deltaTime = (t - self.getTicksLastFrame) / 1000.0
        #self.getTicksLastFrame = t

        for obj in self.objects:
            obj.Render()
        self.skybox.Render()

    def Destroy(self):
        Quit = True