from ursina import *
import math
import random

app = Ursina()

def create_player():
    player = Entity(
        model="cube",
        color=color.azure,
        scale=(1, 1, 1),
        position=(0, 0, 0),
        collider="box",
    )
    player.health = 1000
    return player

def create_enemy():
    enemy = Entity(
        model="cube",
        color=color.red,
        scale=1,
        position=(random.uniform(-8, 8), 0, random.uniform(-8, 8)),
        collider="box",
    )
    enemy.health = 5
    enemy.target = Vec3(random.uniform(-8, 8), 0, random.uniform(-8, 8))
    enemy.hit_recently = False
    return enemy

def create_block(x, z):
    return Entity(
        model="cube",
        color=color.gray,
        scale=(1, 1, 1),
        position=(x, 0.5, z),
        collider="box",
    )

def reset_game():
    global player, player_reflection, enemies, bullets, health_text, mini_map_player, mini_map_enemies, play_again_button, enemy_health_texts, blocks

    destroy(player)
    destroy(player_reflection)
    for enemy in enemies:
        destroy(enemy)
    for bullet in bullets:
        destroy(bullet)
    bullets.clear()
    for block in blocks:
        destroy(block)
    blocks.clear()
    destroy(health_text)
    destroy(mini_map_player)
    for marker in mini_map_enemies:
        destroy(marker)
    mini_map_enemies.clear()
    for text in enemy_health_texts:
        destroy(text)
    enemy_health_texts.clear()
    if play_again_button:
        destroy(play_again_button)

    player = create_player()
    player_reflection = duplicate(
        player, scale_y=-1, color=color.rgba(0, 255, 255, 100)
    )
    enemies = [create_enemy() for _ in range(5)]
    bullets = []

    health_text = Text(text=f"Health: {player.health}", position=(-0.85, 0.45), scale=2)

    enemy_health_texts = []
    for i, enemy in enumerate(enemies):
        t = Text(
            text=f"Enemy {i+1} Health: {enemy.health}",
            position=(-0.85, 0.4 - i * 0.05),
            scale=1.5,
        )
        enemy_health_texts.append(t)

    mini_map_player = Entity(
        parent=mini_map_bg, model="circle", scale=0.02, color=color.cyan
    )
    mini_map_enemies = [
        Entity(parent=mini_map_bg, model="circle", scale=0.02, color=color.red)
        for _ in range(5)
    ]

    for _ in range(20):
        x = random.randint(-8, 8)
        z = random.randint(-8, 8)
        if abs(x) > 2 or abs(z) > 2:
            blocks.append(create_block(x, z))

    play_again_button = None

# --- Game Setup ---
player = create_player()
player_reflection = duplicate(player, scale_y=-1, color=color.rgba(0, 255, 255, 100))

ground = Entity(model="plane", scale=(20, 1, 20), color=color.black, collider="box")

enemies = [create_enemy() for _ in range(5)]
bullets = []
blocks = []

camera.position = (0, 20, -20)
camera.rotation_x = 45

health_text = Text(text=f"Health: {player.health}", position=(-0.85, 0.45), scale=2)
enemy_health_texts = [
    Text(
        text=f"Enemy {i+1} Health: {enemy.health}",
        position=(-0.85, 0.4 - i * 0.05),
        scale=1.5,
    )
    for i, enemy in enumerate(enemies)
]
#Eslam khaled task 
# --- Mini-Map ---
mini_map_bg = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.2, 0.2),
    position=(0.7, 0.4),
    color=color.black66,
)
mini_map_player = Entity(
    parent=mini_map_bg, model="circle", scale=0.02, color=color.cyan
)
mini_map_enemies = [
    Entity(parent=mini_map_bg, model="circle", scale=0.02, color=color.red)
    for _ in range(5)
]

play_again_button = None

def is_blocked(new_position):
    # Check if new_position would hit a block
    for block in blocks:
        if distance(new_position, block.position) < 1:
            return True
    return False

def update():
    global play_again_button

    if not player.enabled:
        return

    speed = 5 * time.dt

    move_vector = Vec3(0, 0, 0)

    # --- Player movement with block collision ---
    if held_keys["s"]:
        move_vector += Vec3(0, 0, -speed)
    if held_keys["w"]:
        move_vector += Vec3(0, 0, speed)
    if held_keys["a"]:
        move_vector += Vec3(-speed, 0, 0)
    if held_keys["d"]:
        move_vector += Vec3(speed, 0, 0)

    future_pos = player.position + move_vector
    if not is_blocked(future_pos):
        player.position = future_pos

    # Border Wrap
    border = 10
    if player.x > border:
        player.x = -border
    if player.x < -border:
        player.x = border
    if player.z > border:
        player.z = -border
    if player.z < -border:
        player.z = border
#finish my task
    # Reflection follows
    player_reflection.x = player.x
    player_reflection.z = player.z
    player_reflection.y = -player.y + 0.1

    # Bullet movement
    for bullet in bullets[:]:
        bullet.position += bullet.direction * bullet.speed * time.dt
        bullet.rotation_y += 360 * time.dt

        if abs(bullet.x) > 15 or abs(bullet.z) > 15:
            bullets.remove(bullet)
            destroy(bullet)

        for block in blocks:
            if bullet.intersects(block).hit:
                bullets.remove(bullet)
                destroy(bullet)
                break

    # Enemy movement and bullet collisions
    for i, enemy in enumerate(enemies[:]):
        if enemy.enabled:
            direction = (enemy.target - enemy.position).normalized()
            future_pos = enemy.position + direction * 2 * time.dt

            if not is_blocked(future_pos):
                enemy.position = future_pos
            else:
                enemy.target = Vec3(
                    random.uniform(-8, 8), 0, random.uniform(-8, 8)
                )  # Pick a new target if blocked

            if distance(enemy.position, enemy.target) < 0.5:
                enemy.target = Vec3(random.uniform(-8, 8), 0, random.uniform(-8, 8))

            enemy.scale_x = 1 + 0.1 * math.sin(time.time() * 2)
            enemy.scale_y = 1 + 0.1 * math.sin(time.time() * 2)
            enemy.scale_z = 1 + 0.1 * math.sin(time.time() * 2)

            for bullet in bullets[:]:
                if distance(bullet.position, enemy.position) < 0.7:
                    enemy.health -= 1
                    if not enemy.hit_recently:
                        enemy.hit_recently = True
                    bullets.remove(bullet)
                    destroy(bullet)

                    enemy_health_texts[i].text = f"Enemy {i+1} Health: {enemy.health}"

                    if enemy.health <= 0:
                        enemy.disable()
                        destroy(mini_map_enemies[i])
                        mini_map_enemies[i] = None
                        enemy_health_texts[i].text = f"Enemy {i+1}: DEAD"

            if enemy.intersects(player).hit:
                player.health -= 1
                health_text.text = f"Health: {player.health}"
                enemy.target = Vec3(random.uniform(-8, 8), 0, random.uniform(-8, 8))

    if player.health <= 0:
        health_text.text = "YOU DIED!"
        player.disable()

        play_again_button = Button(
            text="Play Again", color=color.azure, scale=(0.2, 0.1), position=(0, 0)
        )
        play_again_button.on_click = reset_game

    if all(not enemy.enabled for enemy in enemies):
        health_text.text = "YOU WIN!"
        player.disable()

        if not play_again_button:
            play_again_button = Button(
                text="Play Again", color=color.green, scale=(0.2, 0.1), position=(0, 0)
            )
            play_again_button.on_click = reset_game

    # Mini-Map update
    map_size = 0.18
    world_border = 10

    mini_map_player.x = (player.x / world_border) * (map_size / 2)
    mini_map_player.y = (player.z / world_border) * (map_size / 2)

    for i, enemy in enumerate(enemies):
        if mini_map_enemies[i]:
            mini_map_enemies[i].x = (enemy.x / world_border) * (map_size / 2)
            mini_map_enemies[i].y = (enemy.z / world_border) * (map_size / 2)

def input(key):
    if key == "left mouse down" and player.enabled:
        shoot()

def shoot():
    mouse_point = mouse.world_point
    if not mouse_point:
        return

    direction = (Vec3(mouse_point.x, 0, mouse_point.z) - player.position).normalized()

    bullet = Entity(
        model="sphere",
        color=color.green,
        scale=0.2,
        position=player.position + Vec3(0, 0.5, 0),
        collider="sphere",
    )
    bullet.speed = 8
    bullet.direction = direction
    bullets.append(bullet)

app.run()
