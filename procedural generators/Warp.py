import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import os

# Инициализация Pygame
pygame.init()
display = (800, 600)
pygame.display.set_caption('Procedural generator maker')
pygame.display.set_mode((0, 0), FULLSCREEN | DOUBLEBUF | OPENGL)

# Инициализация камеры
gluPerspective(25, (display[0]/display[1]), 0.1, 1000.0)
glTranslatef(-15, 0.0, -150.0)  # Переместить камеру вниз и назад
glRotatef(35, 1, 0, 0)  # Повернуть камеру на 35 градусов вокруг оси X

# Параметры генерации случайных структур
min_val, max_val = -10, 10
chunk_size = 32
seed = random.randint(0, 1000)  # Генерация сид мира
chunks = {}  # Словарь для хранения чанков

# Генерация случайных вершин
def generate_random_vertices(num_vertices):
    return [(random.uniform(min_val, max_val), random.uniform(min_val, max_val), random.uniform(min_val, max_val)) for _ in range(num_vertices)]

# Генерация случайных граней
def generate_random_faces(num_vertices, num_faces):
    faces = []
    for _ in range(num_faces):
        v1, v2, v3 = random.sample(range(num_vertices), 3)
        faces.append((v1, v2, v3))
    return faces

# Создание чанка с случайной структурой
def create_random_chunk():
    num_vertices = random.randint(5, 20)  # Количество вершин
    num_faces = random.randint(5, 20)      # Количество граней
    vertices = generate_random_vertices(num_vertices)
    faces = generate_random_faces(num_vertices, num_faces)
    return vertices, faces

# Функция для отрисовки модели
def draw_model(vertices, faces):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex_index in face:
            glVertex3fv(vertices[vertex_index])
    glEnd()

# Функция для генерации чанка по координатам
def generate_chunk_at_coords(coords):
    if coords not in chunks:
        vertices, faces = create_random_chunk()
        chunks[coords] = (vertices, faces)

# Основной цикл
offset = [0, 0, 0]
clock = pygame.time.Clock()

# Поля ввода
x_input = ""
y_input = ""
z_input = ""
chunk_size_input = str(chunk_size)
seed_input = str(seed)
active_field = "x"

# Функция для рисования текста
def draw_text(position, text_string, color):
    font = pygame.font.SysFont("Arial", 20)
    text_surface = font.render(text_string, True, color, (0, 0, 0, 255))
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    glRasterPos3d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def update_chunk():
    global vertices, faces
    generate_chunk_at_coords((offset[0], offset[1], offset[2]))

# Функция для сохранения чанка в формате .obj
def save_chunk(vertices, faces, filename):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write('v {:.6f} {:.6f} {:.6f}\n'.format(v[0], v[1], v[2]))
        for face in faces:
            f.write('f {} {} {}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1))

# Генерация случайной структуры для первого кадра
vertices, faces = create_random_chunk()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Сохранить сегмент
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                file_name = os.path.join(desktop, f'chunk_{offset[0]}_{offset[1]}_{offset[2]}.obj')
                save_chunk(vertices, faces, file_name)  # Сохранить файл на рабочий стол
                print(f'Сохранено: {file_name}')
            if event.key == pygame.K_RETURN:
                # Обработка ввода в полях
                if active_field == "x":
                    try:
                        offset[0] = int(x_input) if x_input else 0
                    except ValueError:
                        pass
                    x_input = ""
                    active_field = "y"
                elif active_field == "y":
                    try:
                        offset[1] = int(y_input) if y_input else 0
                    except ValueError:
                        pass
                    y_input = ""
                    active_field = "z"
                elif active_field == "z":
                    try:
                        offset[2] = int(z_input) if z_input else 0
                    except ValueError:
                        pass
                    z_input = ""
                    active_field = "chunk_size"
                elif active_field == "chunk_size":
                    try:
                        chunk_size = int(chunk_size_input) if chunk_size_input else 32
                    except ValueError:
                        pass
                    chunk_size_input = ""
                    active_field = "seed"
                elif active_field == "seed":
                    try:
                        seed = int(seed_input) if seed_input else random.randint(0, 1000)
                        random.seed(seed)  # Обновляем сид
                    except ValueError:
                        pass
                    seed_input = ""
                    active_field = "x"

                # Обновление чанка при изменении `offset`
                update_chunk()

            if event.key == pygame.K_BACKSPACE:
                if active_field == "x" and x_input:
                    x_input = x_input[:-1]
                elif active_field == "y" and y_input:
                    y_input = y_input[:-1]
                elif active_field == "z" and z_input:
                    z_input = z_input[:-1]
                elif active_field == "chunk_size" and chunk_size_input:
                    chunk_size_input = chunk_size_input[:-1]
                elif active_field == "seed" and seed_input:
                    seed_input = seed_input[:-1]

            if event.unicode.isdigit():
                if active_field == "x":
                    x_input += event.unicode
                elif active_field == "y":
                    y_input += event.unicode
                elif active_field == "z":
                    z_input += event.unicode
                elif active_field == "chunk_size":
                    chunk_size_input += event.unicode
                elif active_field == "seed":
                    seed_input += event.unicode

            if event.key == pygame.K_TAB:  # Переключение между полями ввода
                if active_field == "x":
                    active_field = "y"
                elif active_field == "y":
                    active_field = "z"
                elif active_field == "z":
                    active_field = "chunk_size"
                elif active_field == "chunk_size":
                    active_field = "seed"
                elif active_field == "seed":
                    active_field = "x"

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Отрисовка чанка по текущим координатам
    generate_chunk_at_coords((offset[0], offset[1], offset[2]))
    draw_model(*chunks[(offset[0], offset[1], offset[2])])

    # Отрисовка интерфейса
    draw_text((-24, 20.0, 0), "Координата X: " + x_input + "_", (255, 255, 255) if active_field != "x" else (255, 0, 0))
    draw_text((-24.5, 17, 0), "Координата Y: " + y_input + "_", (255, 255, 255) if active_field != "y" else (255, 0, 0))
    draw_text((-25, 14, 0), "Координата Z: " + z_input + "_", (255, 255, 255) if active_field != "z" else (255, 0, 0))
    draw_text((-25.5, 11.0, 0), "LOD: " + chunk_size_input + "_", (255, 255, 255) if active_field != "chunk_size" else (255, 0, 0))
    draw_text((-26, 8.0, 0), "Поменять сид: " + seed_input + "_", (255, 255, 255) if active_field != "seed" else (255, 0, 0))
    draw_text((-23.5, 23.0, 0), "Сид мира: " + str(seed), (255, 255, 255))

    # Отрисовка текущих координат
    
    draw_text((-22.1, 32.0, 0), "X: " + str(offset[0]), (255, 255, 255))
    draw_text((-22.6, 29.0, 0), "Y: " + str(offset[1]), (255, 255, 255))
    draw_text((-23, 26.0, 0), "Z: " + str(offset[2]), (255, 255, 255))
    
    draw_text((-35, -45.0, 0), "Переключиться Tab/Сохранить дамп чанка R", (255, 255, 255))

    pygame.display.flip()
    clock.tick(60)
