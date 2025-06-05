import pygame
import random
import math
import os
import numpy as np

# Power-up class
class PowerUp:
    TYPES = [
        {"name": "speed", "color": (255, 255, 0), "duration": 5, "icon": "⚡"},
        {"name": "magnet", "color": (255, 0, 255), "duration": 7, "icon": "🧲"},
        {"name": "invincible", "color": (0, 255, 255), "duration": 4, "icon": "⭐"},
        {"name": "growth", "color": (255, 150, 0), "duration": 6, "icon": "⬆️"}
    ]
    
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.x = x  # Screen coordinates, will be updated by camera
        self.y = y
        self.size = 15
        self.bounce = 0
        self.bounce_dir = 1
        self.rotation = random.randint(0, 360)
        self.anim_offset = random.randint(0, 100)
        self.anim_speed = random.uniform(0.02, 0.05)
        
        # Choose a random power-up type
        self.type = random.choice(PowerUp.TYPES)
        self.color = self.type["color"]
        self.name = self.type["name"]
        self.duration = self.type["duration"]
        self.icon = self.type["icon"]
        
    def update(self):
        # Simple animation
        self.bounce += 0.1 * self.bounce_dir
        if abs(self.bounce) > 3:
            self.bounce_dir *= -1
        
        # Rotate slowly
        self.rotation = (self.rotation + 1) % 360
    
    def draw(self, camera):
        # Convert world coordinates to screen coordinates
        self.x, self.y = camera.apply(self.world_x, self.world_y)
        
        # Only draw if on screen (with a small buffer)
        if (-self.size*2 <= self.x <= SCREEN_WIDTH + self.size*2 and
            -self.size*2 <= self.y <= SCREEN_HEIGHT + self.size*2):
            
            # Apply bounce animation
            y_offset = math.sin(pygame.time.get_ticks() * self.anim_speed + self.anim_offset) * 5
            
            # Draw glowing effect
            glow_size = self.size * 1.5 + math.sin(pygame.time.get_ticks() * 0.01) * 2
            glow_surface = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
            for i in range(3):
                alpha = 100 - i * 30
                size = glow_size - i * 2
                pygame.draw.circle(glow_surface, (*self.color, alpha), 
                                 (int(glow_size), int(glow_size)), int(size))
            screen.blit(glow_surface, 
                      (int(self.x - glow_size), int(self.y - glow_size + y_offset)))
            
            # Draw power-up
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y + y_offset)), int(self.size))
            
            # Draw icon or symbol
            font = pygame.font.Font(None, 24)
            icon_text = font.render(self.icon, True, WHITE)
            screen.blit(icon_text, (int(self.x - icon_text.get_width()/2), 
                                  int(self.y - icon_text.get_height()/2 + y_offset)))
    
    def check_collision(self, player):
        # Calculate distance between centers in world coordinates
        distance = math.sqrt((self.world_x - player.world_x)**2 + (self.world_y - player.world_y)**2)
        # Check if circles overlap
        return distance < (self.size + player.size)

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Get the screen info for fullscreen support
screen_info = pygame.display.Info()
DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600

# Game constants
SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PLAYER_START_SIZE = 20
WIN_SIZE = 100
SHRINK_FACTOR = 0.9
GROW_FACTOR = 1.1
WORLD_SIZE = 3000  # Large world size

# Sound settings
sound_enabled = True

# Set up the display (windowed by default)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Katamari Adventure")
clock = pygame.time.Clock()

# Fullscreen flag
fullscreen = False

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets_dir, exist_ok=True)
sounds_dir = os.path.join(assets_dir, "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Create a simple sound directly in memory
def create_simple_sound(frequency=440, duration=0.3, volume=0.5):
    # Create a simple beep sound
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    buf = np.zeros((num_samples, 2), dtype=np.float32)
    
    # Generate a simple sine wave
    t = np.linspace(0, duration, num_samples, False)
    tone = np.sin(2 * np.pi * frequency * t) * volume
    
    # Apply fade in/out
    fade = 0.05
    fade_samples = int(fade * sample_rate)
    if fade_samples > 0:
        if fade_samples * 2 < num_samples:
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    # Convert to 16-bit data
    buf[:, 0] = tone
    buf[:, 1] = tone
    
    return pygame.sndarray.make_sound(buf)

# Create sound files if they don't exist
def create_sound_files():
    print("Creating placeholder sounds in memory...")
    
    # Create simple sounds with different frequencies
    grow_sound = create_simple_sound(frequency=800, duration=0.3)
    shrink_sound = create_simple_sound(frequency=300, duration=0.3)
    win_sound = create_simple_sound(frequency=600, duration=1.0)
    bg_sound = create_simple_sound(frequency=200, duration=2.0, volume=0.2)
    
    return {
        "grow": grow_sound,
        "shrink": shrink_sound,
        "win": win_sound,
        "background": bg_sound
    }

# Load or create sounds
try:
    print("Attempting to load sound files...")
    sounds = {
        "grow": pygame.mixer.Sound(os.path.join(sounds_dir, "grow.wav")),
        "shrink": pygame.mixer.Sound(os.path.join(sounds_dir, "shrink.wav")),
        "win": pygame.mixer.Sound(os.path.join(sounds_dir, "win.wav")),
        "background": pygame.mixer.Sound(os.path.join(sounds_dir, "background.wav"))
    }
    print("Sound files loaded successfully!")
except Exception as e:
    print(f"Error loading sound files: {e}")
    print("Creating placeholder sounds instead...")
    # If sounds don't exist, create them in memory
    sounds = create_sound_files()

# Generate realistic grass texture
def create_grass_texture():
    texture = pygame.Surface((100, 100))
    
    # Create a more natural-looking base
    for y in range(100):
        for x in range(100):
            # Create a subtle noise pattern for the base
            noise = random.randint(-10, 10)
            # Vary the green based on position and noise
            green_value = 100 + int((y / 100) * 30) + noise
            green_value = max(80, min(160, green_value))  # Keep in reasonable range
            base_color = (30, green_value, 30)
            texture.set_at((x, y), base_color)
    
    # Add more varied grass blades
    for _ in range(120):
        x = random.randint(0, 99)
        y = random.randint(20, 99)  # Start a bit down for more ground coverage
        height = random.randint(3, 12)
        width = random.randint(1, 2)
        
        # More natural green variations
        green_shade = random.randint(130, 220)
        red_value = random.randint(20, 60)
        blue_value = random.randint(20, 60)
        color = (red_value, green_shade, blue_value)
        
        # Draw grass blade with slight angle
        angle = random.randint(-20, 20)
        end_x = x + int(math.sin(math.radians(angle)) * height)
        end_y = y - height
        pygame.draw.line(texture, color, (x, y), (end_x, end_y), width)
    
    # Add some dirt/soil patches
    for _ in range(8):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        size = random.randint(4, 8)
        brown_shade = random.randint(80, 120)
        color = (brown_shade, brown_shade//2, 0)
        pygame.draw.circle(texture, color, (x, y), size)
        
        # Add texture to the dirt
        for i in range(4):
            small_x = x + random.randint(-size//2, size//2)
            small_y = y + random.randint(-size//2, size//2)
            small_size = random.randint(1, 2)
            dark_brown = (brown_shade-30, (brown_shade-30)//2, 0)
            pygame.draw.circle(texture, dark_brown, (small_x, small_y), small_size)
    
    # Add some small flowers or details
    for _ in range(6):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        size = random.randint(2, 3)
        # Random flower colors
        color_choice = random.randint(0, 3)
        if color_choice == 0:
            color = (255, 255, 255)  # White
        elif color_choice == 1:
            color = (255, 255, 0)    # Yellow
        elif color_choice == 2:
            color = (255, 200, 200)  # Light pink
        else:
            color = (200, 200, 255)  # Light blue
            
        pygame.draw.circle(texture, color, (x, y), size)
        
        # Add center to flower
        center_color = (255, 220, 0)  # Yellow center
        pygame.draw.circle(texture, center_color, (x, y), size//2)
    
    return texture

# Create grass texture
grass_texture = create_grass_texture()

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
    
    def update(self, target_x, target_y):
        # Center camera on target
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2
        
        # Keep camera within world bounds
        self.x = max(0, min(self.x, WORLD_SIZE - self.width))
        self.y = max(0, min(self.y, WORLD_SIZE - self.height))
    
    def apply(self, x, y):
        # Convert world coordinates to screen coordinates
        return int(x - self.x), int(y - self.y)
    
    def apply_rect(self, rect):
        # Convert world rect to screen rect
        return pygame.Rect(int(rect.x - self.x), int(rect.y - self.y), rect.width, rect.height)

class Player:
    def __init__(self, x, y, size):
        self.world_x = x
        self.world_y = y
        self.x = x
        self.y = y
        self.size = size
        self.color = BLUE
        self.base_speed = 5
        self.speed = self.base_speed
        self.rotation = 0
        self.rotation_speed = 3
        self.particles = []
        self.score = 0
        self.objects_collected = 0
        
        # Physics properties
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5
        self.friction = 0.9
        
        # Power-up properties
        self.active_powerups = []
        self.magnet_range = 0
        self.is_invincible = False
        self.growth_multiplier = 1.0
        
        # Visual effects
        self.absorption_particles = []
        self.trail_color = BLUE
    
    def move(self, dx, dy):
        # Apply acceleration based on input
        if dx != 0:
            self.velocity_x += dx * self.acceleration
        if dy != 0:
            self.velocity_y += dy * self.acceleration
        
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Apply velocity
        self.world_x += self.velocity_x
        self.world_y += self.velocity_y
        
        # Keep player within world bounds
        self.world_x = max(self.size, min(WORLD_SIZE - self.size, self.world_x))
        self.world_y = max(self.size, min(WORLD_SIZE - self.size, self.world_y))
        
        # Rotate when moving
        if dx != 0 or dy != 0:
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0
    
    def draw(self, camera):
        # Convert world coordinates to screen coordinates
        self.x, self.y = camera.apply(self.world_x, self.world_y)
        
        # Draw absorption particles
        for particle in self.absorption_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.absorption_particles.remove(particle)
                continue
                
            # Fade out
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            # Move toward player
            dx = self.x - particle['x']
            dy = self.y - particle['y']
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                particle['x'] += dx * 0.2
                particle['y'] += dy * 0.2
            
            # Draw particle
            s = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(s, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
        
        # Draw trail particles
        for i, particle in enumerate(self.particles):
            alpha = int(255 * (1 - i/len(self.particles)))
            color = (self.trail_color[0], self.trail_color[1], self.trail_color[2], alpha)
            s = pygame.Surface((int(particle[2]*2), int(particle[2]*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(particle[2]), int(particle[2])), int(particle[2]))
            screen.blit(s, (int(particle[0] - particle[2]), int(particle[1] - particle[2])))
        
        # Draw magnet range if active
        if self.magnet_range > 0:
            s = pygame.Surface((int(self.magnet_range*2), int(self.magnet_range*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 255, 30), 
                             (int(self.magnet_range), int(self.magnet_range)), 
                             int(self.magnet_range))
            screen.blit(s, (int(self.x - self.magnet_range), int(self.y - self.magnet_range)))
        
        # Draw player with a pattern
        if self.is_invincible:
            # Draw invincibility glow
            glow_size = self.size * 1.2
            glow_surface = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (0, 255, 255, 100), 
                             (int(glow_size), int(glow_size)), int(glow_size))
            screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw player body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        
        # Draw stripes or pattern on player
        for i in range(0, 360, 45):
            angle = math.radians(i + self.rotation)
            end_x = self.x + math.cos(angle) * self.size * 0.8
            end_y = self.y + math.sin(angle) * self.size * 0.8
            pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), max(2, int(self.size // 10)))
        
        # Draw inner circle
        pygame.draw.circle(screen, (50, 100, 255), (int(self.x), int(self.y)), int(self.size * 0.6))
        
        # Draw active power-up indicators
        if self.active_powerups:
            indicator_y = self.y - self.size - 20
            for i, powerup in enumerate(self.active_powerups):
                indicator_x = self.x - 30 + i * 20
                pygame.draw.circle(screen, powerup['color'], (int(indicator_x), int(indicator_y)), 8)
                
                # Draw timer arc
                remaining = powerup['time_left'] / powerup['duration']
                pygame.draw.arc(screen, WHITE, 
                              (int(indicator_x) - 10, int(indicator_y) - 10, 20, 20),
                              0, remaining * 2 * math.pi, 2)
    
    def update_particles(self):
        # Add current position to particles list
        self.particles.append((self.x, self.y, self.size * 0.5))
        
        # Limit number of particles
        if len(self.particles) > 5:
            self.particles.pop(0)
    
    def grow(self, factor=GROW_FACTOR, points=1):
        # Apply growth multiplier if active
        actual_factor = factor * self.growth_multiplier
        
        self.size *= actual_factor
        self.score += points
        self.objects_collected += 1
        
        # Adjust speed based on size (bigger = slower)
        self.speed = max(2, self.base_speed - (self.size / 20))
        
        # Play grow sound
        global sound_enabled
        if sound_enabled:
            try:
                sounds["grow"].play()
            except:
                pass
    
    def shrink(self, factor=SHRINK_FACTOR):
        # Don't shrink if invincible
        if self.is_invincible:
            return
            
        self.size *= factor
        # Minimum size
        self.size = max(10, self.size)
        
        # Adjust speed based on size (smaller = faster)
        self.speed = max(2, self.base_speed - (self.size / 20))
        
        # Play shrink sound
        global sound_enabled
        if sound_enabled:
            try:
                sounds["shrink"].play()
            except:
                pass
    
    def add_absorption_particle(self, x, y, color):
        particle = {
            'x': x,
            'y': y,
            'color': color,
            'size': random.randint(2, 5),
            'life': random.randint(15, 30),
            'max_life': 30
        }
        self.absorption_particles.append(particle)
    
    def apply_powerup(self, powerup):
        effect = {
            'name': powerup.name,
            'duration': powerup.duration,
            'time_left': powerup.duration,
            'color': powerup.color
        }
        self.active_powerups.append(effect)
        
        # Apply effect
        if powerup.name == "speed":
            self.base_speed *= 1.5
            self.trail_color = powerup.color
        elif powerup.name == "magnet":
            self.magnet_range = self.size * 5
        elif powerup.name == "invincible":
            self.is_invincible = True
        elif powerup.name == "growth":
            self.growth_multiplier = 1.5
        
        # Play power-up sound
        global sound_enabled
        if sound_enabled:
            try:
                sounds["grow"].play()  # Reuse grow sound for now
            except:
                pass
    
    def update_powerups(self):
        for powerup in self.active_powerups[:]:
            powerup['time_left'] -= 1/60  # Assuming 60 FPS
            
            if powerup['time_left'] <= 0:
                # Remove effect
                if powerup['name'] == "speed":
                    self.base_speed /= 1.5
                    self.trail_color = BLUE
                elif powerup['name'] == "magnet":
                    self.magnet_range = 0
                elif powerup['name'] == "invincible":
                    self.is_invincible = False
                elif powerup['name'] == "growth":
                    self.growth_multiplier = 1.0
                
                self.active_powerups.remove(powerup)

class Object:
    TYPES = [
        {"name": "rabbit", "color": (200, 200, 200), "shape": "circle", "points": 2},
        {"name": "stone", "color": GRAY, "shape": "circle", "points": 1},
        {"name": "bush", "color": DARK_GREEN, "shape": "circle", "points": 1},
        {"name": "flower", "color": PINK, "shape": "circle", "points": 1},
        {"name": "mushroom", "color": ORANGE, "shape": "circle", "points": 2},
        {"name": "butterfly", "color": PURPLE, "shape": "circle", "points": 3},
        {"name": "frog", "color": GREEN, "shape": "circle", "points": 2},
        {"name": "bird", "color": YELLOW, "shape": "circle", "points": 3},
        {"name": "squirrel", "color": BROWN, "shape": "circle", "points": 2},
        {"name": "fish", "color": (0, 191, 255), "shape": "circle", "points": 2}
    ]
    
    def __init__(self, x, y, size):
        self.world_x = x
        self.world_y = y
        self.x = x  # Screen coordinates, will be updated by camera
        self.y = y
        self.size = size
        self.bounce = 0
        self.bounce_dir = 1
        self.rotation = random.randint(0, 360)
        
        # Choose a random object type
        self.type = random.choice(Object.TYPES)
        self.color = self.type["color"]
        self.shape = self.type["shape"]
        self.name = self.type["name"]
        self.points = self.type["points"]
        
        # Animation variables
        self.anim_offset = random.randint(0, 100)
        self.anim_speed = random.uniform(0.02, 0.05)
    
    def update(self):
        # Simple animation
        self.bounce += 0.1 * self.bounce_dir
        if abs(self.bounce) > 3:
            self.bounce_dir *= -1
        
        # Rotate slowly
        self.rotation = (self.rotation + 0.5) % 360
    
    def draw(self, camera):
        # Convert world coordinates to screen coordinates
        self.x, self.y = camera.apply(self.world_x, self.world_y)
        
        # Only draw if on screen (with a small buffer)
        if (-self.size*2 <= self.x <= SCREEN_WIDTH + self.size*2 and
            -self.size*2 <= self.y <= SCREEN_HEIGHT + self.size*2):
            
            # Apply bounce animation
            y_offset = math.sin(pygame.time.get_ticks() * self.anim_speed + self.anim_offset) * 3
            
            if self.name == "rabbit":
                # Draw body
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + y_offset)), int(self.size))
                
                # Draw ears
                ear_size = self.size * 0.4
                pygame.draw.ellipse(screen, self.color, 
                                  (int(self.x - ear_size/2 - self.size/2), 
                                   int(self.y - ear_size*1.5 + y_offset), 
                                   int(ear_size), int(ear_size*1.5)))
                pygame.draw.ellipse(screen, self.color, 
                                  (int(self.x - ear_size/2 + self.size/2), 
                                   int(self.y - ear_size*1.5 + y_offset), 
                                   int(ear_size), int(ear_size*1.5)))
                
                # Draw eyes
                eye_size = max(2, int(self.size * 0.15))
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x - self.size*0.3), int(self.y - self.size*0.2 + y_offset)), 
                                 eye_size)
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x + self.size*0.3), int(self.y - self.size*0.2 + y_offset)), 
                                 eye_size)
                
            elif self.name == "stone":
                # Draw stone with texture
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
                
                # Add texture lines
                for i in range(3):
                    angle = math.radians(self.rotation + i * 120)
                    x1 = self.x + math.cos(angle) * self.size * 0.5
                    y1 = self.y + math.sin(angle) * self.size * 0.5
                    x2 = self.x + math.cos(angle + math.pi/4) * self.size * 0.7
                    y2 = self.y + math.sin(angle + math.pi/4) * self.size * 0.7
                    pygame.draw.line(screen, (100, 100, 100), 
                                   (int(x1), int(y1)), 
                                   (int(x2), int(y2)), 
                                   max(1, int(self.size/10)))
                
            elif self.name == "mushroom":
                # Draw cap
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y - self.size*0.2 + y_offset)), int(self.size))
                
                # Draw stem
                stem_width = self.size * 0.6
                stem_height = self.size * 0.8
                pygame.draw.rect(screen, WHITE, 
                               (int(self.x - stem_width/2), 
                                int(self.y + y_offset), 
                                int(stem_width), int(stem_height)))
                
                # Draw spots
                for _ in range(3):
                    spot_x = self.x + random.uniform(-0.6, 0.6) * self.size
                    spot_y = self.y - self.size*0.2 + random.uniform(-0.6, 0.6) * self.size + y_offset
                    spot_size = self.size * 0.15
                    pygame.draw.circle(screen, WHITE, (int(spot_x), int(spot_y)), int(spot_size))
                
            elif self.name == "flower":
                # Draw center
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y + y_offset)), int(self.size * 0.3))
                
                # Draw petals
                for angle in range(0, 360, 45):
                    rad = math.radians(angle + self.rotation)
                    petal_x = self.x + math.cos(rad) * self.size * 0.7
                    petal_y = self.y + math.sin(rad) * self.size * 0.7 + y_offset
                    pygame.draw.circle(screen, self.color, (int(petal_x), int(petal_y)), int(self.size * 0.4))
                
                # Draw stem
                pygame.draw.line(screen, GREEN, 
                               (int(self.x), int(self.y + self.size*0.3 + y_offset)), 
                               (int(self.x), int(self.y + self.size*1.2 + y_offset)), 
                               max(2, int(self.size/10)))
                
            elif self.name == "bush":
                # Draw multiple circles for bush
                for i in range(5):
                    offset_x = math.cos(math.radians(i * 72 + self.rotation)) * self.size * 0.5
                    offset_y = math.sin(math.radians(i * 72 + self.rotation)) * self.size * 0.5
                    pygame.draw.circle(screen, self.color, 
                                     (int(self.x + offset_x), int(self.y + offset_y + y_offset)), 
                                     int(self.size * 0.6))
                
                # Draw main bush body
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + y_offset)), int(self.size * 0.7))
                
            elif self.name == "butterfly":
                # Draw body
                pygame.draw.line(screen, BLACK, 
                               (int(self.x), int(self.y - self.size*0.5 + y_offset)), 
                               (int(self.x), int(self.y + self.size*0.5 + y_offset)), 
                               max(2, int(self.size/8)))
                
                # Draw wings with animation
                wing_flutter = math.sin(pygame.time.get_ticks() * 0.01 + self.anim_offset) * 0.5 + 0.5
                wing_size_x = self.size * (0.8 + wing_flutter * 0.3)
                wing_size_y = self.size * 0.7
                
                # Left wing
                pygame.draw.ellipse(screen, self.color, 
                                  (int(self.x - wing_size_x), 
                                   int(self.y - wing_size_y/2 + y_offset), 
                                   int(wing_size_x), int(wing_size_y)))
                
                # Right wing
                pygame.draw.ellipse(screen, self.color, 
                                  (int(self.x), 
                                   int(self.y - wing_size_y/2 + y_offset), 
                                   int(wing_size_x), int(wing_size_y)))
                
                # Wing patterns
                pattern_color = (255, 255, 255, 150)
                s = pygame.Surface((int(wing_size_x*0.7), int(wing_size_y*0.7)), pygame.SRCALPHA)
                pygame.draw.ellipse(s, pattern_color, 
                                  (0, 0, int(wing_size_x*0.7), int(wing_size_y*0.7)))
                
                screen.blit(s, (int(self.x - wing_size_x*0.8), int(self.y - wing_size_y*0.35 + y_offset)))
                screen.blit(s, (int(self.x + wing_size_x*0.1), int(self.y - wing_size_y*0.35 + y_offset)))
                
            elif self.name == "frog":
                # Draw body
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + y_offset)), int(self.size))
                
                # Draw eyes
                eye_size = max(2, int(self.size * 0.25))
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.x - self.size*0.3), int(self.y - self.size*0.4 + y_offset)), 
                                 eye_size)
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.x + self.size*0.3), int(self.y - self.size*0.4 + y_offset)), 
                                 eye_size)
                
                # Draw pupils
                pupil_size = max(1, int(eye_size * 0.5))
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x - self.size*0.3), int(self.y - self.size*0.4 + y_offset)), 
                                 pupil_size)
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x + self.size*0.3), int(self.y - self.size*0.4 + y_offset)), 
                                 pupil_size)
                
                # Draw mouth
                pygame.draw.arc(screen, (50, 100, 50), 
                              (int(self.x - self.size*0.5), int(self.y - self.size*0.1 + y_offset), 
                               int(self.size), int(self.size*0.5)), 
                              0, math.pi, max(1, int(self.size/10)))
                
            elif self.name == "bird":
                # Draw body
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + y_offset)), int(self.size * 0.8))
                
                # Draw head
                pygame.draw.circle(screen, self.color, 
                                 (int(self.x + self.size*0.5), int(self.y - self.size*0.3 + y_offset)), 
                                 int(self.size * 0.5))
                
                # Draw beak
                beak_points = [
                    (self.x + self.size*0.9, self.y - self.size*0.3 + y_offset),
                    (self.x + self.size*1.2, self.y - self.size*0.2 + y_offset),
                    (self.x + self.size*0.9, self.y - self.size*0.1 + y_offset)
                ]
                pygame.draw.polygon(screen, ORANGE, [(int(x), int(y)) for x, y in beak_points])
                
                # Draw eye
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x + self.size*0.6), int(self.y - self.size*0.4 + y_offset)), 
                                 max(2, int(self.size * 0.1)))
                
                # Draw wing
                wing_y_offset = math.sin(pygame.time.get_ticks() * 0.005 + self.anim_offset) * 3
                wing_points = [
                    (self.x - self.size*0.1, self.y - self.size*0.1 + y_offset),
                    (self.x - self.size*0.8, self.y - self.size*0.5 + wing_y_offset + y_offset),
                    (self.x - self.size*0.2, self.y + self.size*0.3 + y_offset)
                ]
                pygame.draw.polygon(screen, self.color, [(int(x), int(y)) for x, y in wing_points])
                
            elif self.name == "squirrel":
                # Draw body
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + y_offset)), int(self.size))
                
                # Draw head
                pygame.draw.circle(screen, self.color, 
                                 (int(self.x + self.size*0.5), int(self.y - self.size*0.3 + y_offset)), 
                                 int(self.size * 0.6))
                
                # Draw tail
                tail_points = [
                    (self.x - self.size*0.3, self.y + y_offset),
                    (self.x - self.size*0.8, self.y - self.size*0.8 + y_offset),
                    (self.x - self.size*1.2, self.y - self.size*0.5 + y_offset),
                    (self.x - self.size*0.9, self.y + y_offset)
                ]
                pygame.draw.polygon(screen, self.color, [(int(x), int(y)) for x, y in tail_points])
                
                # Draw eye
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x + self.size*0.7), int(self.y - self.size*0.4 + y_offset)), 
                                 max(2, int(self.size * 0.1)))
                
                # Draw ear
                pygame.draw.circle(screen, self.color, 
                                 (int(self.x + self.size*0.7), int(self.y - self.size*0.8 + y_offset)), 
                                 int(self.size * 0.2))
                
            elif self.name == "fish":
                # Draw body
                body_points = [
                    (self.x + self.size*0.8, self.y + y_offset),
                    (self.x - self.size*0.5, self.y - self.size*0.5 + y_offset),
                    (self.x - self.size*0.5, self.y + self.size*0.5 + y_offset)
                ]
                pygame.draw.polygon(screen, self.color, [(int(x), int(y)) for x, y in body_points])
                
                # Draw tail with animation
                tail_wave = math.sin(pygame.time.get_ticks() * 0.01 + self.anim_offset) * 0.3
                tail_points = [
                    (self.x - self.size*0.5, self.y - self.size*0.3 + y_offset),
                    (self.x - self.size*1.0, self.y + tail_wave + y_offset),
                    (self.x - self.size*0.5, self.y + self.size*0.3 + y_offset)
                ]
                pygame.draw.polygon(screen, self.color, [(int(x), int(y)) for x, y in tail_points])
                
                # Draw eye
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x + self.size*0.4), int(self.y - self.size*0.1 + y_offset)), 
                                 max(2, int(self.size * 0.15)))
                
                # Draw fin
                fin_points = [
                    (self.x, self.y - self.size*0.1 + y_offset),
                    (self.x + self.size*0.3, self.y - self.size*0.6 + y_offset),
                    (self.x + self.size*0.5, self.y - self.size*0.1 + y_offset)
                ]
                pygame.draw.polygon(screen, self.color, [(int(x), int(y)) for x, y in fin_points])
    
    def check_collision(self, player):
        # Calculate distance between centers in world coordinates
        distance = math.sqrt((self.world_x - player.world_x)**2 + (self.world_y - player.world_y)**2)
        # Check if circles overlap
        return distance < (self.size + player.size)

def generate_objects(count, player_x, player_y, player_size, existing_objects=None):
    objects = [] if existing_objects is None else existing_objects
    
    # Define area around player where objects shouldn't spawn
    safe_radius = player_size * 3
    
    for _ in range(count):
        # Generate random size
        size = random.randint(5, 40)
        
        # Ensure objects don't spawn too close to player
        while True:
            # Generate position anywhere in the world
            x = random.randint(size, WORLD_SIZE - size)
            y = random.randint(size, WORLD_SIZE - size)
            
            # Check distance from player
            if math.sqrt((x - player_x)**2 + (y - player_y)**2) > safe_radius:
                # Also check distance from other objects to prevent overlap
                valid_position = True
                for obj in objects:
                    if math.sqrt((x - obj.world_x)**2 + (y - obj.world_y)**2) < (size + obj.size):
                        valid_position = False
                        break
                
                if valid_position:
                    break
        
        # Create object
        objects.append(Object(x, y, size))
    
    return objects

def generate_powerups(count, player_x, player_y, player_size, existing_powerups=None):
    powerups = [] if existing_powerups is None else existing_powerups
    
    # Define area around player where powerups shouldn't spawn
    safe_radius = player_size * 3
    
    for _ in range(count):
        # Ensure powerups don't spawn too close to player
        while True:
            # Generate position anywhere in the world
            x = random.randint(20, WORLD_SIZE - 20)
            y = random.randint(20, WORLD_SIZE - 20)
            
            # Check distance from player
            if math.sqrt((x - player_x)**2 + (y - player_y)**2) > safe_radius:
                # Also check distance from other objects to prevent overlap
                valid_position = True
                for pu in powerups:
                    if math.sqrt((x - pu.world_x)**2 + (y - pu.world_y)**2) < 40:
                        valid_position = False
                        break
                
                if valid_position:
                    break
        
        # Create powerup
        powerups.append(PowerUp(x, y))
    
    return powerups

def draw_grass_background(camera):
    # Calculate visible area in world coordinates
    visible_x = camera.x
    visible_y = camera.y
    visible_width = SCREEN_WIDTH
    visible_height = SCREEN_HEIGHT
    
    # Draw base color first - more natural earthy green
    screen.fill((45, 85, 45))
    
    # Store the last camera position to maintain consistency between frames
    if not hasattr(draw_grass_background, "last_camera_pos"):
        draw_grass_background.last_camera_pos = (camera.x, camera.y)
        draw_grass_background.terrain_features = []
    
    # Only regenerate terrain features when camera moves significantly
    camera_moved = (abs(camera.x - draw_grass_background.last_camera_pos[0]) > 200 or
                   abs(camera.y - draw_grass_background.last_camera_pos[1]) > 200)
    
    if camera_moved or not draw_grass_background.terrain_features:
        # Update last camera position
        draw_grass_background.last_camera_pos = (camera.x, camera.y)
        
        # Clear previous features
        draw_grass_background.terrain_features = []
        
        # Generate new terrain features based on camera position
        # Use fixed positions based on a grid to ensure consistency
        grid_size = 500
        for grid_x in range(int((camera.x - SCREEN_WIDTH) // grid_size), 
                           int((camera.x + SCREEN_WIDTH * 2) // grid_size) + 1):
            for grid_y in range(int((camera.y - SCREEN_HEIGHT) // grid_size), 
                               int((camera.y + SCREEN_HEIGHT * 2) // grid_size) + 1):
                
                # Generate a consistent seed for this grid cell
                base_x = grid_x * grid_size
                base_y = grid_y * grid_size
                
                # Add some features to each grid cell
                for i in range(5):  # Limit number of features per cell
                    # Use a hash of the position to get consistent random values
                    feature_seed = hash((grid_x, grid_y, i)) % 10000
                    random.seed(feature_seed)
                    
                    # Calculate position within the grid cell
                    offset_x = random.randint(50, grid_size - 50)
                    offset_y = random.randint(50, grid_size - 50)
                    pos_x = base_x + offset_x
                    pos_y = base_y + offset_y
                    
                    # Determine terrain feature type
                    feature_type = random.randint(0, 10)
                    
                    # Store feature data
                    feature = {
                        "world_x": pos_x,
                        "world_y": pos_y,
                        "type": feature_type,
                        "seed": feature_seed,
                        "size": random.randint(50, 300) if feature_type <= 5 else random.randint(15, 40)
                    }
                    
                    draw_grass_background.terrain_features.append(feature)
    
    # Reset random seed to avoid affecting game logic
    random.seed()
    
    # Draw all terrain features
    for feature in draw_grass_background.terrain_features:
        # Calculate screen position
        screen_x, screen_y = camera.apply(feature["world_x"], feature["world_y"])
        
        # Only draw if potentially visible (with buffer)
        if (-300 <= screen_x <= SCREEN_WIDTH + 300 and
            -300 <= screen_y <= SCREEN_HEIGHT + 300):
            
            # Set the random seed for this feature to ensure consistent appearance
            random.seed(feature["seed"])
            
            if feature["type"] <= 3:  # Grass patch (40% chance)
                # Lighter or darker grass patch
                if random.random() < 0.5:
                    color = (60, 100, 60)  # Lighter
                else:
                    color = (35, 75, 35)   # Darker
                
                size = feature["size"]
                # Draw an irregular shape instead of a perfect circle
                points = []
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dist = size * (0.7 + random.random() * 0.6)
                    px = screen_x + math.cos(rad) * dist
                    py = screen_y + math.sin(rad) * dist
                    points.append((px, py))
                
                pygame.draw.polygon(screen, color, points)
                
            elif feature["type"] <= 5:  # Dirt patch (20% chance)
                color = (80, 65, 45)
                size = feature["size"]
                pygame.draw.circle(screen, color, (screen_x, screen_y), size)
                
                # Add some texture to the dirt
                for _ in range(10):
                    small_x = screen_x + random.randint(-size//2, size//2)
                    small_y = screen_y + random.randint(-size//2, size//2)
                    small_size = random.randint(5, 15)
                    dark_brown = (70, 55, 35)
                    pygame.draw.circle(screen, dark_brown, (small_x, small_y), small_size)
                    
            elif feature["type"] <= 7:  # Flower patch (20% chance)
                base_color = (50, 90, 50)
                size = feature["size"]
                pygame.draw.circle(screen, base_color, (screen_x, screen_y), size)
                
                # Add flowers
                flower_count = random.randint(10, 30)
                for _ in range(flower_count):
                    fx = screen_x + random.randint(-size, size)
                    fy = screen_y + random.randint(-size, size)
                    
                    # Only draw if within the patch (roughly)
                    if math.sqrt((fx - screen_x)**2 + (fy - screen_y)**2) <= size:
                        flower_size = random.randint(3, 8)
                        
                        # Choose flower color
                        if random.random() < 0.3:
                            flower_color = (255, 255, 255)  # White
                        elif random.random() < 0.5:
                            flower_color = (255, 255, 100)  # Yellow
                        else:
                            flower_color = (255, 150, 150)  # Pink
                            
                        # Draw petals
                        for angle in range(0, 360, 45):
                            rad = math.radians(angle)
                            px = fx + math.cos(rad) * flower_size
                            py = fy + math.sin(rad) * flower_size
                            pygame.draw.circle(screen, flower_color, (int(px), int(py)), flower_size//2)
                        
                        # Draw center
                        pygame.draw.circle(screen, (255, 220, 0), (int(fx), int(fy)), flower_size//2)
                        
            else:  # Stone formation (20% chance)
                for _ in range(random.randint(3, 8)):
                    stone_x = screen_x + random.randint(-100, 100)
                    stone_y = screen_y + random.randint(-100, 100)
                    stone_size = random.randint(15, 40)
                    stone_color = (100 + random.randint(-20, 20), 
                                 100 + random.randint(-20, 20), 
                                 100 + random.randint(-20, 20))
                    pygame.draw.circle(screen, stone_color, (stone_x, stone_y), stone_size)
    
    # Reset random seed to avoid affecting game logic
    random.seed()
    
    # Store ambient particles if they don't exist yet
    if not hasattr(draw_grass_background, "ambient_particles"):
        draw_grass_background.ambient_particles = []
        for i in range(8):  # Reduced number of particles
            particle = {
                "base_x": random.random() * SCREEN_WIDTH,
                "base_y": random.random() * SCREEN_HEIGHT,
                "offset_x": 0,
                "offset_y": 0,
                "speed": random.uniform(0.1, 0.3),  # Even slower speed
                "size": random.randint(1, 2),  # Smaller particles
                "type": random.randint(0, 2),
                "phase": random.random() * math.pi * 2  # Random starting phase
            }
            draw_grass_background.ambient_particles.append(particle)
    
    # Update and draw ambient particles with much gentler movement
    time_factor = pygame.time.get_ticks() / 8000  # Much slower time factor
    for particle in draw_grass_background.ambient_particles:
        # Update position with gentle sine wave movement
        particle["offset_x"] = math.sin(time_factor * particle["speed"] + particle["phase"]) * 20
        particle["offset_y"] = math.cos(time_factor * particle["speed"] + particle["phase"] * 0.7) * 15
        
        particle_x = (particle["base_x"] + particle["offset_x"]) % SCREEN_WIDTH
        particle_y = (particle["base_y"] + particle["offset_y"]) % SCREEN_HEIGHT
        
        # Different particle types
        if particle["type"] == 0:  # Butterfly
            size = particle["size"] + 1
            color = (255, 220, 100)  # Yellow butterfly
            pygame.draw.circle(screen, color, (int(particle_x), int(particle_y)), size)
            
            # Wings with gentle flutter
            wing_flutter = math.sin(time_factor * 1.5 + particle["phase"]) * 1.0  # Even gentler flutter
            pygame.draw.ellipse(screen, color, 
                              (int(particle_x - 4 - wing_flutter), 
                               int(particle_y - 2), 
                               4, 4))
            pygame.draw.ellipse(screen, color, 
                              (int(particle_x + wing_flutter), 
                               int(particle_y - 2), 
                               4, 4))
                               
        elif particle["type"] == 1:  # Pollen/dust
            size = particle["size"]
            color = (255, 255, 220, 80)  # More transparent
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size, size), size)
            screen.blit(s, (int(particle_x - size), int(particle_y - size)))
            
        else:  # Light reflection
            size = particle["size"]
            color = (255, 255, 255, 50)  # Very transparent
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size, size), size)
            screen.blit(s, (int(particle_x - size), int(particle_y - size)))

def draw_ui(player, game_over=False, current_level=1, level_goals=[100]):
    # Get screen dimensions for responsive UI
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Calculate UI element sizes based on screen dimensions
    info_width = int(screen_width * 0.2)  # 20% of screen width
    info_height = int(screen_height * 0.15)  # 15% of screen height
    
    # Draw a semi-transparent overlay for the info bar
    s = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
    s.fill((20, 20, 50, 180))  # Dark blue with transparency
    screen.blit(s, (0, 0))
    
    # Add a subtle border
    pygame.draw.rect(screen, (100, 100, 200, 200), 
                   (0, 0, info_width, info_height), 
                   1)
    
    # Get current level goal
    current_goal = level_goals[current_level-1] if current_level <= len(level_goals) else level_goals[-1]
    
    # Draw size progress bar in the top center of the screen
    bar_width = int(screen_width * 0.35)  # 35% of screen width
    bar_height = int(screen_height * 0.04)  # 4% of screen height
    border_width = 2
    
    # Draw border
    pygame.draw.rect(screen, WHITE, 
                   (screen_width//2 - bar_width//2 - border_width, 
                    15 - border_width, 
                    bar_width + border_width*2, 
                    bar_height + border_width*2))
    
    # Draw background
    pygame.draw.rect(screen, BLACK, 
                   (screen_width//2 - bar_width//2, 
                    15, 
                    bar_width, 
                    bar_height))
    
    # Draw progress based on current level goal
    progress = min(1.0, player.size / current_goal)
    progress_color = (50, 200, 50)
    pygame.draw.rect(screen, progress_color, 
                   (screen_width//2 - bar_width//2, 
                    15, 
                    int(bar_width * progress), 
                    bar_height))
    
    # Scale font sizes based on screen dimensions
    font_size_small = max(14, int(screen_width * 0.02))
    font_size_medium = max(18, int(screen_width * 0.025))
    font_size_large = max(22, int(screen_width * 0.03))
    
    # Draw text
    font = pygame.font.Font(None, font_size_medium)
    size_text = font.render(f"Size: {int(player.size)}/{current_goal}", True, WHITE)
    screen.blit(size_text, (screen_width//2 - size_text.get_width()//2, 15 + bar_height//2 - size_text.get_height()//2))
    
    # Draw level information below the progress bar
    level_font = pygame.font.Font(None, font_size_medium)
    level_text = level_font.render(f"Level {current_level}", True, WHITE)
    screen.blit(level_text, (screen_width//2 - level_text.get_width()//2, 20 + bar_height))
    
    # Draw info bar content
    y_offset = int(info_height * 0.1)  # 10% of info bar height
    header_font = pygame.font.Font(None, font_size_large)
    
    # Score section
    score_text = header_font.render(f"Score: {player.score}", True, (255, 255, 150))
    screen.blit(score_text, (10, y_offset))
    y_offset += int(info_height * 0.3)  # 30% of info bar height
    
    # Objects collected
    obj_text = header_font.render(f"Objects: {player.objects_collected}", True, (150, 255, 150))
    screen.blit(obj_text, (10, y_offset))
    y_offset += int(info_height * 0.3)  # 30% of info bar height
    
    # Sound status
    if sound_enabled:
        sound_text = header_font.render("Sound: ON (M)", True, (150, 150, 255))
    else:
        sound_text = header_font.render("Sound: OFF (M)", True, (255, 150, 150))
    screen.blit(sound_text, (10, y_offset))
    
    # Draw mini-map in top-right corner
    map_size = int(screen_width * 0.15)  # 15% of screen width
    map_x = screen_width - map_size - int(screen_width * 0.02)  # 2% padding
    map_y = int(screen_height * 0.03)  # 3% of screen height
    
    # Draw map background with border
    pygame.draw.rect(screen, (50, 50, 100), 
                   (map_x - 2, 
                    map_y - 2, 
                    map_size + 4, 
                    map_size + 4))
    
    pygame.draw.rect(screen, (20, 60, 20), 
                   (map_x, map_y, map_size, map_size))
    
    # Draw grid lines on map
    grid_count = 4
    for i in range(1, grid_count):
        # Vertical lines
        line_x = map_x + (i * map_size // grid_count)
        pygame.draw.line(screen, (40, 80, 40), (line_x, map_y), (line_x, map_y + map_size), 1)
        
        # Horizontal lines
        line_y = map_y + (i * map_size // grid_count)
        pygame.draw.line(screen, (40, 80, 40), (map_x, line_y), (map_x + map_size, line_y), 1)
    
    # Draw player on map with a pulsing effect
    pulse = math.sin(pygame.time.get_ticks() * 0.01) * 1.5 + 4
    player_map_x = map_x + int(player.world_x / WORLD_SIZE * map_size)
    player_map_y = map_y + int(player.world_y / WORLD_SIZE * map_size)
    
    # Draw player position indicator
    pygame.draw.circle(screen, (100, 100, 255, 150), (player_map_x, player_map_y), int(pulse))
    pygame.draw.circle(screen, BLUE, (player_map_x, player_map_y), 3)
    
    # Draw "MAP" label
    map_label = font.render("MAP", True, WHITE)
    screen.blit(map_label, (map_x + map_size//2 - map_label.get_width()//2, map_y - map_label.get_height() - 5))
    
    # Draw active power-ups
    if player.active_powerups:
        pu_y = info_height + 30
        pu_font = pygame.font.Font(None, font_size_small)
        pu_title = pu_font.render("Active Power-ups:", True, (200, 200, 255))
        screen.blit(pu_title, (10, pu_y))
        pu_y += 25
        
        for i, powerup in enumerate(player.active_powerups):
            # Draw power-up icon
            pygame.draw.circle(screen, powerup['color'], (20, pu_y), 10)
            
            # Draw timer bar
            remaining = powerup['time_left'] / powerup['duration']
            bar_length = int(info_width * 0.6)  # 60% of info bar width
            pygame.draw.rect(screen, (50, 50, 70), (35, pu_y - 5, bar_length, 10))
            pygame.draw.rect(screen, powerup['color'], (35, pu_y - 5, int(bar_length * remaining), 10))
            
            # Draw name
            name_text = pu_font.render(powerup['name'].capitalize(), True, WHITE)
            screen.blit(name_text, (40 + bar_length, pu_y - 5))
            
            pu_y += 20
    
    # Draw game over message
    if game_over:
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw win message
        win_font = pygame.font.Font(None, int(screen_width * 0.08))  # 8% of screen width
        win_text = win_font.render("You Win!", True, WHITE)
        screen.blit(win_text, (screen_width//2 - win_text.get_width()//2, screen_height//2 - win_text.get_height()))
        
        # Draw restart instruction
        sub_font = pygame.font.Font(None, int(screen_width * 0.04))  # 4% of screen width
        sub_text = sub_font.render("Press SPACE to play again", True, WHITE)
        screen.blit(sub_text, (screen_width//2 - sub_text.get_width()//2, screen_height//2 + 50))

def show_message(text, size=36):
    # Get screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Scale font size based on screen dimensions
    font_size = max(size, int(screen_width * size/800))
    
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(screen_width/2, screen_height/2))
    screen.blit(text_surface, text_rect)

def draw_start_screen():
    # Get screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Fill background
    screen.fill((20, 70, 20))
    
    # Scale font sizes based on screen dimensions
    title_size = max(48, int(screen_width * 0.08))
    instruction_size = max(24, int(screen_width * 0.03))
    space_size = max(32, int(screen_width * 0.04))
    
    # Draw title
    title_font = pygame.font.Font(None, title_size)
    title_text = title_font.render("Katamari Adventure", True, WHITE)
    screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, screen_height//4))
    
    # Draw instructions
    instructions = [
        "Roll around and absorb smaller objects to grow bigger!",
        "Avoid larger objects or you'll shrink!",
        "Complete all 5 levels to win!",
        "",
        "New Features:",
        "- Collect power-ups for special abilities",
        "- Physics-based movement",
        "- Multiple levels with increasing goals",
        "",
        "Controls:",
        "Arrow keys or WASD to move",
        "M to toggle sound on/off",
        "F to toggle fullscreen",
        "Space to start game"
    ]
    
    font = pygame.font.Font(None, instruction_size)
    y_offset = screen_height//2 - 50
    
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (screen_width//2 - text.get_width()//2, y_offset))
        y_offset += int(screen_height * 0.04)  # 4% of screen height
    
    # Draw animated player
    player_size = int(screen_width * 0.05) + math.sin(pygame.time.get_ticks() * 0.003) * int(screen_width * 0.01)
    player_x = screen_width//2
    player_y = screen_height//4 - int(screen_height * 0.1)
    
    pygame.draw.circle(screen, BLUE, (player_x, player_y), int(player_size))
    
    # Draw stripes on player
    rotation = (pygame.time.get_ticks() * 0.05) % 360
    for i in range(0, 360, 45):
        angle = math.radians(i + rotation)
        end_x = player_x + math.cos(angle) * player_size * 0.8
        end_y = player_y + math.sin(angle) * player_size * 0.8
        pygame.draw.line(screen, WHITE, (player_x, player_y), 
                       (int(end_x), int(end_y)), max(2, int(player_size // 10)))
    
    # Draw inner circle
    pygame.draw.circle(screen, (50, 100, 255), (player_x, player_y), int(player_size * 0.6))
    
    # Draw animated objects around the player
    for i in range(8):
        angle = math.radians(i * 45 + pygame.time.get_ticks() * 0.05)
        distance = int(screen_width * 0.15) + math.sin(pygame.time.get_ticks() * 0.002 + i) * int(screen_width * 0.02)
        x = player_x + math.cos(angle) * distance
        y = player_y + math.sin(angle) * distance
        obj_size = int(screen_width * 0.015) + math.sin(pygame.time.get_ticks() * 0.003 + i * 0.5) * int(screen_width * 0.005)
        
        # Choose color based on position
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK, BROWN]
        pygame.draw.circle(screen, colors[i], (int(x), int(y)), int(obj_size))
        
    # Draw power-ups
    for i in range(4):
        pu_x = screen_width//4 + i * (screen_width//2)//4
        pu_y = screen_height - int(screen_height * 0.15)
        pu_size = int(screen_width * 0.015) + math.sin(pygame.time.get_ticks() * 0.003 + i) * int(screen_width * 0.003)
        
        # Power-up colors
        pu_colors = [(255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 150, 0)]
        
        # Draw glowing effect
        glow_size = pu_size * 1.5 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 2
        glow_surface = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
        for j in range(3):
            alpha = 100 - j * 30
            size = glow_size - j * 2
            pygame.draw.circle(glow_surface, (*pu_colors[i], alpha), 
                             (int(glow_size), int(glow_size)), int(size))
        screen.blit(glow_surface, (int(pu_x - glow_size), int(pu_y - glow_size)))
        
        # Draw power-up
        pygame.draw.circle(screen, pu_colors[i], (int(pu_x), int(pu_y)), int(pu_size))
        
    # Draw "Press SPACE to start" with pulsing effect
    space_font = pygame.font.Font(None, space_size)
    pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.2 + 0.8
    space_color = (int(255 * pulse), int(255 * pulse), int(255 * pulse))
    space_text = space_font.render("Press SPACE to start", True, space_color)
    screen.blit(space_text, (screen_width//2 - space_text.get_width()//2, screen_height - int(screen_height * 0.08)))

def main():
    # Access global variables
    global fullscreen, SCREEN_WIDTH, SCREEN_HEIGHT, screen, sound_enabled
    
    # Game state
    game_state = "start"  # "start", "playing", "game_over"
    
    # Create player at center of world
    player = Player(WORLD_SIZE/2, WORLD_SIZE/2, PLAYER_START_SIZE)
    
    # Create camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Generate initial objects
    objects = generate_objects(100, player.world_x, player.world_y, player.size)
    
    # Generate initial powerups
    powerups = generate_powerups(5, player.world_x, player.world_y, player.size)
    
    # Start background music
    try:
        pygame.mixer.music.load(os.path.join(sounds_dir, "background.wav"))
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except Exception as e:
        print(f"Could not load background music: {e}")
        print("Continuing without background music.")
    
    # Game variables
    running = True
    
    # Level system
    current_level = 1
    level_goals = [100, 200, 300, 400, 500]  # Size goals for each level
    level_complete = False
    level_message_timer = 0
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "start":
                        game_state = "playing"
                    elif game_state == "game_over":
                        # Restart game
                        player = Player(WORLD_SIZE/2, WORLD_SIZE/2, PLAYER_START_SIZE)
                        objects = generate_objects(100, player.world_x, player.world_y, player.size)
                        powerups = generate_powerups(5, player.world_x, player.world_y, player.size)
                        current_level = 1
                        game_state = "playing"
                    elif level_complete:
                        # Go to next level
                        level_complete = False
                        current_level += 1
                        
                        # Reset player size for the new level
                        player = Player(player.world_x, player.world_y, PLAYER_START_SIZE)
                        player.score = player.score  # Keep the score from previous level
                        
                        if current_level > len(level_goals):
                            game_state = "game_over"
                        else:
                            # Generate more objects for the new level
                            objects = generate_objects(100, player.world_x, player.world_y, player.size)
                            powerups = generate_powerups(5, player.world_x, player.world_y, player.size)
                elif event.key == pygame.K_m:
                    # Toggle sound
                    sound_enabled = not sound_enabled
                    if sound_enabled:
                        try:
                            pygame.mixer.music.unpause()
                        except:
                            pass
                    else:
                        try:
                            pygame.mixer.music.pause()
                        except:
                            pass
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    fullscreen = not fullscreen
                    if fullscreen:
                        # Get the current screen info
                        screen_info = pygame.display.Info()
                        # Set to fullscreen mode
                        SCREEN_WIDTH = screen_info.current_w
                        SCREEN_HEIGHT = screen_info.current_h
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        # Return to windowed mode
                        SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
                        SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    
                    # Update camera dimensions
                    camera.width = SCREEN_WIDTH
                    camera.height = SCREEN_HEIGHT
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize events
                if not fullscreen:
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    # Update camera dimensions
                    camera.width = SCREEN_WIDTH
                    camera.height = SCREEN_HEIGHT
        
        if game_state == "start":
            # Draw start screen
            draw_start_screen()
            
        elif game_state == "playing":
            # Handle movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += player.speed
            
            # Move player
            player.move(dx, dy)
            
            # Update player particles
            player.update_particles()
            
            # Update player powerups
            player.update_powerups()
            
            # Update camera to follow player
            camera.update(player.world_x, player.world_y)
            
            # Update objects
            for obj in objects:
                obj.update()
                
                # If magnet is active, move smaller objects toward player
                if player.magnet_range > 0 and obj.size < player.size:
                    dist = math.sqrt((obj.world_x - player.world_x)**2 + (obj.world_y - player.world_y)**2)
                    if dist < player.magnet_range:
                        # Calculate direction to player
                        dx = player.world_x - obj.world_x
                        dy = player.world_y - obj.world_y
                        # Normalize
                        if dist > 0:
                            dx /= dist
                            dy /= dist
                        # Move object toward player
                        pull_strength = 2 * (1 - dist/player.magnet_range)
                        obj.world_x += dx * pull_strength
                        obj.world_y += dy * pull_strength
            
            # Update powerups
            for powerup in powerups:
                powerup.update()
            
            # Check collisions with objects
            objects_to_remove = []
            for obj in objects:
                if obj.check_collision(player):
                    if obj.size < player.size:
                        # Absorb smaller objects
                        player.grow(GROW_FACTOR, obj.points)
                        
                        # Create absorption particles
                        obj_screen_x, obj_screen_y = camera.apply(obj.world_x, obj.world_y)
                        for _ in range(5):
                            particle_x = obj_screen_x + random.randint(-int(obj.size), int(obj.size))
                            particle_y = obj_screen_y + random.randint(-int(obj.size), int(obj.size))
                            player.add_absorption_particle(particle_x, particle_y, obj.color)
                            
                        objects_to_remove.append(obj)
                    else:
                        # Shrink when hitting larger objects
                        player.shrink()
            
            # Check collisions with powerups
            powerups_to_remove = []
            for powerup in powerups:
                if powerup.check_collision(player):
                    player.apply_powerup(powerup)
                    powerups_to_remove.append(powerup)
            
            # Remove absorbed objects
            for obj in objects_to_remove:
                objects.remove(obj)
                
            # Remove collected powerups
            for powerup in powerups_to_remove:
                powerups.remove(powerup)
            
            # Check level completion
            current_goal = level_goals[current_level-1] if current_level <= len(level_goals) else level_goals[-1]
            if not level_complete and current_level <= len(level_goals) and player.size >= current_goal:
                level_complete = True
                level_message_timer = 180  # Show message for 3 seconds (60 FPS)
                if sound_enabled:
                    try:
                        sounds["win"].play()
                    except:
                        pass
            
            # Check win condition (completed all levels)
            if current_level > len(level_goals):
                game_state = "game_over"
                if sound_enabled:
                    try:
                        sounds["win"].play()
                    except:
                        pass
            
            # Generate new objects if needed
            if len(objects) < 100:
                objects = generate_objects(20, player.world_x, player.world_y, player.size, objects)
                
            # Generate new powerups if needed
            if len(powerups) < 5:
                powerups = generate_powerups(1, player.world_x, player.world_y, player.size, powerups)
            
            # Draw everything
            screen.fill(BLACK)
            
            # Draw grass background
            draw_grass_background(camera)
            
            # Draw objects
            for obj in objects:
                obj.draw(camera)
                
            # Draw powerups
            for powerup in powerups:
                powerup.draw(camera)
            
            # Draw player
            player.draw(camera)
            
            # Draw UI with level information
            draw_ui(player, game_state == "game_over", current_level, level_goals)
            
            # Draw level complete message
            if level_complete:
                level_message_timer -= 1
                
                # Create a semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Scale font size based on screen dimensions
                title_font_size = max(48, int(SCREEN_WIDTH * 0.06))
                subtitle_font_size = max(32, int(SCREEN_WIDTH * 0.04))
                
                font = pygame.font.Font(None, title_font_size)
                complete_text = font.render(f"Level {current_level} Complete!", True, WHITE)
                screen.blit(complete_text, (SCREEN_WIDTH//2 - complete_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
                
                if current_level < len(level_goals):
                    font = pygame.font.Font(None, subtitle_font_size)
                    next_text = font.render("Press SPACE for next level", True, WHITE)
                    screen.blit(next_text, (SCREEN_WIDTH//2 - next_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
                else:
                    font = pygame.font.Font(None, subtitle_font_size)
                    win_text = font.render("You've completed all levels!", True, WHITE)
                    screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            
        elif game_state == "game_over":
            # Keep drawing the game but with win message
            screen.fill(BLACK)
            draw_grass_background(camera)
            for obj in objects:
                obj.draw(camera)
            for powerup in powerups:
                powerup.draw(camera)
            player.draw(camera)
            draw_ui(player, True, current_level, level_goals)
            
            # Draw final score
            font_size = max(48, int(SCREEN_WIDTH * 0.06))
            font = pygame.font.Font(None, font_size)
            score_text = font.render(f"Final Score: {player.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        # Draw fullscreen toggle hint
        hint_font = pygame.font.Font(None, max(16, int(SCREEN_WIDTH * 0.02)))
        hint_text = hint_font.render("Press F to toggle fullscreen", True, (200, 200, 200))
        screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, SCREEN_HEIGHT - hint_text.get_height() - 10))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
# Power-up class
class PowerUp:
    TYPES = [
        {"name": "speed", "color": (255, 255, 0), "duration": 5, "icon": "⚡"},
        {"name": "magnet", "color": (255, 0, 255), "duration": 7, "icon": "🧲"},
        {"name": "invincible", "color": (0, 255, 255), "duration": 4, "icon": "⭐"},
        {"name": "growth", "color": (255, 150, 0), "duration": 6, "icon": "⬆️"}
    ]
    
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.x = x  # Screen coordinates, will be updated by camera
        self.y = y
        self.size = 15
        self.bounce = 0
        self.bounce_dir = 1
        self.rotation = random.randint(0, 360)
        self.anim_offset = random.randint(0, 100)
        self.anim_speed = random.uniform(0.02, 0.05)
        
        # Choose a random power-up type
        self.type = random.choice(PowerUp.TYPES)
        self.color = self.type["color"]
        self.name = self.type["name"]
        self.duration = self.type["duration"]
        self.icon = self.type["icon"]
        
    def update(self):
        # Simple animation
        self.bounce += 0.1 * self.bounce_dir
        if abs(self.bounce) > 3:
            self.bounce_dir *= -1
        
        # Rotate slowly
        self.rotation = (self.rotation + 1) % 360
    
    def draw(self, camera):
        # Convert world coordinates to screen coordinates
        self.x, self.y = camera.apply(self.world_x, self.world_y)
        
        # Only draw if on screen (with a small buffer)
        if (-self.size*2 <= self.x <= SCREEN_WIDTH + self.size*2 and
            -self.size*2 <= self.y <= SCREEN_HEIGHT + self.size*2):
            
            # Apply bounce animation
            y_offset = math.sin(pygame.time.get_ticks() * self.anim_speed + self.anim_offset) * 5
            
            # Draw glowing effect
            glow_size = self.size * 1.5 + math.sin(pygame.time.get_ticks() * 0.01) * 2
            glow_surface = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
            for i in range(3):
                alpha = 100 - i * 30
                size = glow_size - i * 2
                pygame.draw.circle(glow_surface, (*self.color, alpha), 
                                 (int(glow_size), int(glow_size)), int(size))
            screen.blit(glow_surface, 
                      (int(self.x - glow_size), int(self.y - glow_size + y_offset)))
            
            # Draw power-up
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y + y_offset)), int(self.size))
            
            # Draw icon or symbol
            font = pygame.font.Font(None, 24)
            icon_text = font.render(self.icon, True, WHITE)
            screen.blit(icon_text, (int(self.x - icon_text.get_width()/2), 
                                  int(self.y - icon_text.get_height()/2 + y_offset)))
    
    def check_collision(self, player):
        # Calculate distance between centers in world coordinates
        distance = math.sqrt((self.world_x - player.world_x)**2 + (self.world_y - player.world_y)**2)
        # Check if circles overlap
        return distance < (self.size + player.size)
