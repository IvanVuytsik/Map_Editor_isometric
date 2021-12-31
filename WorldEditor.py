import pygame
import os, os.path
import csv
import pickle

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
LOWER_MARGIN = 0
SIDE_MARGIN = 300
WINDOW_SIZE = (1280, 720)

screen = pygame.display.set_mode((WINDOW_SIZE[0] + SIDE_MARGIN, WINDOW_SIZE[1] + LOWER_MARGIN))
display = pygame.Surface((1280, 720))

pygame.display.set_caption('Level Editor')
FPS = 60
clock = pygame.time.Clock()
run = True

ROWS = 64
MAX_COLS = 64
TILE_SIZE = SCREEN_HEIGHT // ROWS * 4

path, dirs, files = next(os.walk("WorldEditor/tiles"))
file_count = len(files)
TILE_TYPES = file_count

path, dirs, assets = next(os.walk("WorldEditor/assets"))
assets_count = len(assets)
ASSETS_TYPES = assets_count

path, dirs, trees = next(os.walk("WorldEditor/trees"))
trees_count = len(trees)
TREES_TYPES = trees_count

path, dirs, plants = next(os.walk("WorldEditor/plants_rocks"))
plants_count = len(plants)
PLANTS_TYPES = plants_count


scroll_left = False
scroll_right = False
scroll_up = False
scroll_down = False

mouse_scroll_up = False
mouse_scroll_down = False

scroll = [0, 0]
mouse_scroll = [0,0]
scroll_speed = 1
current_tile = 0
current_asset = 0
current_tree = 0
current_plant = 0

map = 0
layer = 0


# bg_sky = pygame.image.load("ExplorationMaps/TestMap/SkyBG0.png").convert_alpha()
# bg_sky = pygame.transform.scale(bg_sky, (int(SCREEN_WIDTH) * 2, (int(SCREEN_HEIGHT) * 2)))
# bg_mountains = pygame.image.load("ExplorationMaps/TestMap/MountainsBG0.png").convert_alpha()
# bg_mountains = pygame.transform.scale(bg_mountains, (int(SCREEN_WIDTH * 2), (int(SCREEN_HEIGHT))))
# bg_forest = pygame.image.load("ExplorationMaps/TestMap/bg_forest0.png").convert_alpha()
# bg_forest = pygame.transform.scale(bg_forest, (int(SCREEN_WIDTH * 2), (int(SCREEN_HEIGHT / 2))))

save_img = pygame.image.load("WorldEditor/save.png").convert_alpha()
save_img = pygame.transform.scale(save_img, (40, 40))
load_img = pygame.image.load("WorldEditor/load.png").convert_alpha()
load_img = pygame.transform.scale(load_img, (40, 40))


class WorldButton():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y +mouse_scroll[1]))
        return action


# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'WorldEditor/tiles/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
img_assets_list = []
for x in range(ASSETS_TYPES):
    img = pygame.image.load(f'WorldEditor/assets/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE*3, TILE_SIZE*2))
    img_assets_list.append(img)
img_trees_list = []
for x in range(TREES_TYPES):
    img = pygame.image.load(f'WorldEditor/trees/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE*2))
    img_trees_list.append(img)
img_plants_list = []
for x in range(PLANTS_TYPES):
    img = pygame.image.load(f'WorldEditor/plants_rocks/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_plants_list.append(img)


green = (144, 201, 120)
white = (255, 255, 255)
red = (200, 25, 25)
blue = (135, 206, 250)
font = pygame.font.SysFont('Futura', 30)

# world_list
world_data = []
world_constructs = []
world_trees = []
world_nature = []
for row in range(ROWS):
    r = [-1] * MAX_COLS  # -1 repeated x 150
    world_data.append(r)
    l = [-2] * MAX_COLS
    world_constructs.append(l)
    k = [-3] * MAX_COLS
    world_trees.append(k)
    f = [-4] * MAX_COLS
    world_nature.append(f)

# create with tiles
# for tile in range(0,MAX_COLS):
#     world_data[ROWS-1][tile] = 0     #[ROWS-1][tile] = last row = 0 tile
# print(world_data)

def draw_text(surface, text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    surface.blit(img, (x, y))

# def draw_bg():
#     display.fill(blue)
#     width = bg_sky.get_width()
#     for x in range(3):
#         display.blit(bg_sky, ((x * width) - scroll[0] * 0.5, 0))
#         display.blit(bg_mountains, ((x * width) - scroll[0] * 0.6, SCREEN_HEIGHT - bg_mountains.get_height()))
#         display.blit(bg_forest, ((x * width) - scroll[0] * 0.7, SCREEN_HEIGHT - bg_forest.get_height()))

def draw_grid():
    for c in range(MAX_COLS + 1):
        pygame.draw.line(display, white, (c * TILE_SIZE - scroll[0], 0 - scroll[1]),
                         (c * TILE_SIZE - scroll[0], SCREEN_HEIGHT * 4 - scroll[1]))
    for c in range(ROWS + 1):
        pygame.draw.line(display, white, (0 - scroll[0], c * TILE_SIZE - scroll[1]),
                         (SCREEN_WIDTH * 4 - scroll[0], c * TILE_SIZE - scroll[1]))

switch_rendering = False

def draw_world(render_mode):
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            standard = (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1])
            isometric = (1200 + x * 20 - y * 20 - scroll[0], x * 10 + y * 10 + 1000 - scroll[1])
            if switch_rendering == False:
                render_mode = standard
            else:
                render_mode = isometric
            if tile >= 0:
                display.blit(img_list[tile], render_mode)

def draw_surface (render_mode, world_list, images):
    for y, row in enumerate(world_list):
        for x, asset in enumerate(row):
            standard = (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1])
            isometric = (1200 + x * 15 - y * 15 - scroll[0], x * 10 + y * 10 + 1000 - scroll[1])
            if switch_rendering == False:
                render_mode = standard
            else:
                render_mode = isometric
            if asset >= 0:
                display.blit(images[asset], render_mode)

button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = WorldButton(SCREEN_WIDTH + (50 * button_col) + 30, 50 * button_row + 20, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 5:
        button_row += 1
        button_col = 0

surface_button_list = []
button_col = 0
button_row = 0
for i in range(len(img_assets_list)):
    asset_button = WorldButton(SCREEN_WIDTH + (50 * button_col) + 5, 50 * button_row + 5, img_assets_list[i], 1)
    surface_button_list.append(asset_button)
    button_col += 1
    if button_col == 2:
        button_row += 1
        button_col = 0

trees_button_list = []
button_col = 0
button_row = 0
for i in range(len(img_trees_list)):
    tree_button = WorldButton(SCREEN_WIDTH + (50 * button_col) + 5, 50 * button_row + 5, img_trees_list[i], 1)
    trees_button_list.append(tree_button)
    button_col += 1
    if button_col == 5:
        button_row += 1
        button_col = 0

plants_button_list = []
button_col = 0
button_row = 0
for i in range(len(img_plants_list)):
    plant_button = WorldButton(SCREEN_WIDTH + (50 * button_col) + 5, 50 * button_row + 5, img_plants_list[i], 1)
    plants_button_list.append(plant_button)
    button_col += 1
    if button_col == 5:
        button_row += 1
        button_col = 0

while run:
    clock.tick(FPS)
    display.fill((150,150,150))
    #draw_bg()
    draw_grid()
    draw_world(None)
    draw_surface(None,world_constructs, img_assets_list)
    draw_surface(None,world_trees, img_trees_list)
    draw_surface(None,world_nature, img_plants_list)

    # draw_text(display,f'Map: {map}', font, '#A65000',10,SCREEN_HEIGHT + LOWER_MARGIN - 40)
    # draw_text(display,'W/S switch map', font, '#A65000',10,SCREEN_HEIGHT + LOWER_MARGIN - 70)
    # draw_text(display,f'Layer: {layer}', font, '#A65000',800,SCREEN_HEIGHT + LOWER_MARGIN - 40)
    # draw_text(display,'A/D switch layer', font, '#A65000',800,SCREEN_HEIGHT + LOWER_MARGIN - 70)
    save_button = WorldButton(1290, 680 -mouse_scroll[1], save_img, 1)
    load_button = WorldButton(1530, 680 -mouse_scroll[1], load_img, 1)
    # panel
    pygame.draw.rect(screen, '#2c2d47', (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    # choosing tiles
    if layer == 0:
        button_count = 0
        for button_count, i in enumerate(button_list):
            if i.draw(screen):
                current_tile = button_count
            pygame.draw.rect(screen, red, button_list[current_tile].rect, 3)
            # highlight selected tile
    elif layer == 1:
        asset_count = 0
        for asset_count, i in enumerate(surface_button_list):
            if i.draw(screen):
                current_asset = asset_count
            pygame.draw.rect(screen, red, surface_button_list[current_asset].rect, 3)
    elif layer == 2:
        tree_count = 0
        for tree_count, i in enumerate(trees_button_list):
            if i.draw(screen):
                current_tree = tree_count
            pygame.draw.rect(screen, red, trees_button_list[current_tree].rect, 3)
    elif layer == 3:
        plant_count = 0
        for plant_count, i in enumerate(plants_button_list):
            if i.draw(screen):
                current_plant = plant_count
            pygame.draw.rect(screen, red, plants_button_list[current_plant].rect, 3)
    #--------------------------------textsrender------------------------------
    draw_text(screen, f'Map: {map}', font, (255, 225, 100), SCREEN_WIDTH + 5, SCREEN_HEIGHT - 70)
    draw_text(screen, 'W/S switch', font, (255, 225, 100), SCREEN_WIDTH + 5, SCREEN_HEIGHT - 90)
    draw_text(screen, f'Layer: {layer}', font, (255, 225, 100), SCREEN_WIDTH + 215, SCREEN_HEIGHT - 70)
    draw_text(screen, 'A/D switch', font, (255, 225, 100), SCREEN_WIDTH + 185, SCREEN_HEIGHT - 90)

    # -----------------------------Save/Load------------------------------
    tree_layer = map
    nature_layer = map
    constructs_layer = map
    if save_button.draw(screen):
        pickle_out = open(f'WorldEditor/Locations/map{map}data.csv', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out_cs = open(f'WorldEditor/Locations/constructs{constructs_layer}data.csv', 'wb')
        pickle.dump(world_constructs, pickle_out_cs)
        pickle_out_tr = open(f'WorldEditor/Locations/trees{tree_layer}data.csv', 'wb')
        pickle.dump(world_trees, pickle_out_tr)
        pickle_out_nt = open(f'WorldEditor/Locations/nature{nature_layer}data.csv', 'wb')
        pickle.dump(world_nature, pickle_out_nt)
        pickle_out.close()
        pickle_out_cs.close()
        pickle_out_tr.close()
        pickle_out_nt.close()
        # with open(f'WorldEditor/Locations/map{map}data.csv', 'w', newline ='') as csvfile:
        #     writer = csv.writer(csvfile, delimiter = ',')
        #     for row in world_data:
        #         writer.writerow(row)
    if load_button.draw(screen):
        scroll[0] = 0
        scroll[1] = 0
        world_data = []
        world_constructs = []
        world_trees = []
        world_nature = []
        pickle_in = open(f'WorldEditor/Locations/map{map}data.csv', 'rb')
        world_data = pickle.load(pickle_in)
        pickle_in_cs = open(f'WorldEditor/Locations/constructs{constructs_layer}data.csv', 'rb')
        world_constructs = pickle.load(pickle_in_cs)
        pickle_in_tr = open(f'WorldEditor/Locations/trees{tree_layer}data.csv', 'rb')
        world_trees = pickle.load(pickle_in_tr)
        pickle_in_nt = open(f'WorldEditor/Locations/nature{nature_layer}data.csv', 'rb')
        world_nature = pickle.load(pickle_in_nt)

        # with open(f'WorldEditor/Locations/map{map}data.csv', newline ='') as csvfile:
        #     reader= csv.reader(csvfile, delimiter = ',')
        #     for row in world_data:
        #         for x, row in enumerate(reader):
        #             for y, tile in enumerate(row):
        #                 world_data[x][y] = int(tile)

    if scroll_left == True and scroll[0] > 0:
        scroll[0] -= 5 * scroll_speed
    if scroll_right == True and scroll[0] < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll[0] += 5 * scroll_speed
    if scroll_up == True and scroll[1] > 0:
        scroll[1] -= 5 * scroll_speed
    if scroll_down == True and scroll[1] < (ROWS * TILE_SIZE) - SCREEN_HEIGHT:
        scroll[1] += 5 * scroll_speed

    # ------------------newtiles-------------------
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll[0]) // TILE_SIZE
    y = (pos[1] + scroll[1]) // TILE_SIZE

    # check that coordinates are within the tile grid
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if layer == 0:
            if pygame.mouse.get_pressed()[0] == 1:
                if world_data[y][x] != current_tile:
                    world_data[y][x] = current_tile
            if pygame.mouse.get_pressed()[2] == 1:
                world_data[y][x] = -1
        elif layer == 1:
            if pygame.mouse.get_pressed()[0] == 1:
                if world_constructs[y][x] != current_asset:
                    world_constructs[y][x] = current_asset
            if pygame.mouse.get_pressed()[2] == 1:
                world_constructs[y][x] = -2
        elif layer == 2:
            if pygame.mouse.get_pressed()[0] == 1:
                if world_trees[y][x] != current_tree:
                    world_trees[y][x] = current_tree
            if pygame.mouse.get_pressed()[2] == 1:
                world_trees[y][x] = -3
        elif layer == 3:
            if pygame.mouse.get_pressed()[0] == 1:
                if world_nature[y][x] != current_plant:
                    world_nature[y][x] = current_plant
            if pygame.mouse.get_pressed()[2] == 1:
                world_nature[y][x] = -4

    # print(x)
    # print(y)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and switch_rendering == False:
                switch_rendering = True
            elif event.key == pygame.K_f and switch_rendering == True:
                switch_rendering = False
            if event.key == pygame.K_w:
                map += 1
            if event.key == pygame.K_s and map > 0:
                map -= 1
            if event.key == pygame.K_d:
                layer += 1
            if event.key == pygame.K_a and layer > 0:
                layer -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_UP:
                scroll_up = True
            if event.key == pygame.K_DOWN:
                scroll_down = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_UP:
                scroll_up = False
            if event.key == pygame.K_DOWN:
                scroll_down = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and mouse_scroll[1] < 0:
                mouse_scroll[1] +=15*scroll_speed
            if event.button == 5:
                mouse_scroll[1] -=15*scroll_speed

        # if event.type == pygame.MOUSEBUTTONUP:
        #     if event.button == 4:
        #         mouse_scroll_up = False
        #     if event.button == 5:
        #         mouse_scroll_down = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    # clock.tick(60)

pygame.quit()
