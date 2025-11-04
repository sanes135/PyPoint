import glfw
import numpy as np
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import math
import time

def perspective_matrix(fov, aspect_ratio, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    return np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), -1],
        [0, 0, (2 * far * near) / (near - far), 0]
    ], dtype=np.float32)


class Platform:
    def __init__(self, size=5.0):
        vertices = [
            -size, 0.0, -size,
            size, 0.0, -size,
            size, 0.0, size,
            -size, 0.0, size
        ]
        indices = [0, 1, 2, 2, 3, 0]

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        self.shader = compileProgram(
            compileShader("""
            #version 330 core
            layout(location = 0) in vec3 aPos;
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            void main() {
                gl_Position = projection * view * model * vec4(aPos, 1.0);
            }
            """, GL_VERTEX_SHADER),
            compileShader("""
            #version 330 core
            out vec4 FragColor;
            uniform vec3 color;
            void main() {
                FragColor = vec4(color, 1.0);
            }
            """, GL_FRAGMENT_SHADER)
        )

    def draw(self, view, projection, color=(0.5, 0.5, 0.5)):
        glUseProgram(self.shader)
        model = np.identity(4)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(self.shader, "color"), *color)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)


class Camera:
    def __init__(self):
        self.pos = np.array([0.0, 1.0, 3.0], dtype=np.float32)
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.speed = 5.0
        self.sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = 0.0

    def get_view_matrix(self):
        return self.look_at(self.pos, self.pos + self.front, self.up)

    def look_at(self, position, target, world_up):
        zaxis = (target - position).astype(np.float32)
        zaxis /= np.linalg.norm(zaxis)

        xaxis = np.cross(zaxis, world_up).astype(np.float32)
        xaxis /= np.linalg.norm(xaxis)

        yaxis = np.cross(xaxis, zaxis).astype(np.float32)

        view = np.array([
            [xaxis[0], yaxis[0], -zaxis[0], 0],
            [xaxis[1], yaxis[1], -zaxis[1], 0],
            [xaxis[2], yaxis[2], -zaxis[2], 0],
            [-np.dot(xaxis, position), -np.dot(yaxis, position), np.dot(zaxis, position), 5]
        ], dtype=np.float32)

        return view


class ConstAnimationRenderer:
    def __init__(self, data):
        if data is not None:
            self.work = True
            self.frames = data.get('frames')
            self.delay = data.get('delay')
            self.max_frame_index = len(self.frames) - 1
            self.current_frame_index = 0
            self.start_time = 0
            self.points = None
            self.global_color = None
            self.global_color_mode = None
            self.vao = None
            self.vbo = None
            self.shader = None

            self.load_frame(self.current_frame_index)
        else:
            self.work = False

    def load_frame(self, frame_index):
        print(frame_index)
        frame_data = self.frames[frame_index]
        self.global_color_mode = 'global_color' in frame_data
        self.global_color = frame_data.get('global_color')
        self.points = frame_data['points']

        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_STATIC_DRAW)

        if self.global_color_mode:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
            glEnableVertexAttribArray(0)
        else:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, None)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glEnable(GL_PROGRAM_POINT_SIZE)
        self.reload_shaders()

    def start_timer(self):
        if self.work:
            self.start_time = time.time()

    def update(self):
        if self.work:
            if self.delay < time.time() - self.start_time:
                self.start_time = time.time()
                self.current_frame_index += 1
                if self.max_frame_index < self.current_frame_index:
                    self.current_frame_index = 0

                self.load_frame(self.current_frame_index)

    def draw(self, view_matrix, projection_matrix, point_size=5.0):
        if self.work:
            glUseProgram(self.shader)
            model = np.identity(4, dtype=np.float32)

            # Передаем матрицы и размер точки в шейдер
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view_matrix)
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection_matrix)
            glUniform1f(glGetUniformLocation(self.shader, "pointSize"), point_size)

            if self.global_color_mode:
                glUniform3f(glGetUniformLocation(self.shader, "globalColor"), self.global_color[0], self.global_color[1],
                            self.global_color[2])

            glBindVertexArray(self.vao)
            if self.global_color_mode:
                glDrawArrays(GL_POINTS, 0, len(self.points) // 3)
            else:
                glDrawArrays(GL_POINTS, 0, len(self.points) // 6)
            glBindVertexArray(0)

    def reload_shaders(self):
        if self.work:
            if self.global_color_mode:
                vertex_src_global_color = """
                       #version 330 core
                       layout(location = 0) in vec3 aPos;
                       layout(location = 1) in vec3 aColor;
    
                       uniform mat4 model;
                       uniform mat4 view;
                       uniform mat4 projection;
                       uniform float pointSize;
    
                       out vec3 fragColor;
    
                       void main()
                       {
                           gl_Position = projection * view * model * vec4(aPos, 1.0);
                           gl_PointSize = pointSize;  // Устанавливаем размер точки
                       }
                       """

                fragment_src_global_color = """
                                   #version 330 core
                                   out vec4 FragColor;
    
                                   uniform vec3 globalColor;
    
                                   void main()
                                   {
                                       FragColor = vec4(globalColor, 1.0);
                                   }
                                   """
                vertex_shader = compileShader(vertex_src_global_color, GL_VERTEX_SHADER)
                fragment_shader = compileShader(fragment_src_global_color, GL_FRAGMENT_SHADER)
            else:
                vertex_src_individual_colors = """
                                   #version 330 core
                                   layout(location = 0) in vec3 aPos;
                                   layout(location = 1) in vec3 aColor;
    
                                   uniform mat4 model;
                                   uniform mat4 view;
                                   uniform mat4 projection;
                                   uniform float pointSize;
    
                                   out vec3 fragColor;
    
                                   void main()
                                   {
                                       gl_Position = projection * view * model * vec4(aPos, 1.0);
                                       gl_PointSize = pointSize;
                                       fragColor = aColor;
                                   }
                                   """

                fragment_src_individual_colors = """
                                   #version 330 core
                                   in vec3 fragColor;
                                   out vec4 FragColor;
    
                                   void main()
                                   {
                                       FragColor = vec4(fragColor, 1.0);
                                   }
                                   """
                vertex_shader = compileShader(vertex_src_individual_colors, GL_VERTEX_SHADER)
                fragment_shader = compileShader(fragment_src_individual_colors, GL_FRAGMENT_SHADER)
            self.shader = compileProgram(vertex_shader, fragment_shader)

    def set_global_color(self, color):
        self.global_color = color


class RealTimeRenderer:
    def __init__(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.global_color_mode = None
        self.shader = None
        self.points = None
        self.global_color = None

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update_data(self, new_data):
        new_global_color_mode = 'global_color' in new_data

        if new_global_color_mode != self.global_color_mode:
            self.global_color_mode = new_global_color_mode
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])

            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            self.reload_shaders()

            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            if self.global_color_mode:
                glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
                glEnableVertexAttribArray(0)
            else:
                glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, None)
                glEnableVertexAttribArray(0)
                glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
                glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        if self.global_color_mode:
            self.global_color = new_data['global_color']
            self.points = np.array(clear_list(new_data['points']), dtype=np.float32)
        else:
            points = np.array(clear_list(new_data['points']), dtype=np.float32)
            colors = np.array(clear_list(new_data['individual_color']), dtype=np.float32)
            self.points = np.hstack((points, colors)).flatten()


        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


    def reload_shaders(self):
        if self.global_color_mode:
            vertex_src_global_color = """
                   #version 330 core
                   layout(location = 0) in vec3 aPos;
                   layout(location = 1) in vec3 aColor;

                   uniform mat4 model;
                   uniform mat4 view;
                   uniform mat4 projection;
                   uniform float pointSize;

                   out vec3 fragColor;

                   void main()
                   {
                       gl_Position = projection * view * model * vec4(aPos, 1.0);
                       gl_PointSize = pointSize;  // Устанавливаем размер точки
                   }
                   """

            fragment_src_global_color = """
                               #version 330 core
                               out vec4 FragColor;

                               uniform vec3 globalColor;

                               void main()
                               {
                                   FragColor = vec4(globalColor, 1.0);
                               }
                               """
            vertex_shader = compileShader(vertex_src_global_color, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_src_global_color, GL_FRAGMENT_SHADER)
        else:
            vertex_src_individual_colors = """
                               #version 330 core
                               layout(location = 0) in vec3 aPos;
                               layout(location = 1) in vec3 aColor;

                               uniform mat4 model;
                               uniform mat4 view;
                               uniform mat4 projection;
                               uniform float pointSize;

                               out vec3 fragColor;

                               void main()
                               {
                                   gl_Position = projection * view * model * vec4(aPos, 1.0);
                                   gl_PointSize = pointSize;
                                   fragColor = aColor;
                               }
                               """

            fragment_src_individual_colors = """
                               #version 330 core
                               in vec3 fragColor;
                               out vec4 FragColor;

                               void main()
                               {
                                   FragColor = vec4(fragColor, 1.0);
                               }
                               """
            vertex_shader = compileShader(vertex_src_individual_colors, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_src_individual_colors, GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)

        # Проверяем ошибки компиляции шейдеров
        if glGetShaderiv(vertex_shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(f"Vertex shader compilation failed: {glGetShaderInfoLog(vertex_shader)}")
        if glGetShaderiv(fragment_shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(f"Fragment shader compilation failed: {glGetShaderInfoLog(fragment_shader)}")
        if glGetProgramiv(self.shader, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(f"Shader program linking failed: {glGetProgramInfoLog(self.shader)}")

    def draw(self, view_matrix, projection_matrix, point_size=1.0):
        if self.points is None:
            return

        glUseProgram(self.shader)
        model = np.identity(4, dtype=np.float32)

        # Передаем матрицы и размер точки в шейдер
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection_matrix)
        glUniform1f(glGetUniformLocation(self.shader, "pointSize"), point_size)

        if self.global_color_mode:
            glUniform3f(glGetUniformLocation(self.shader, "globalColor"), self.global_color[0], self.global_color[1],
                        self.global_color[2])

        glBindVertexArray(self.vao)
        if self.global_color_mode:
            glDrawArrays(GL_POINTS, 0, len(self.points) // 3)
        else:
            glDrawArrays(GL_POINTS, 0, len(self.points) // 6)
        glBindVertexArray(0)


class ConstPointRenderer:
    def __init__(self, data):
        """
        data может быть либо словарем с глобальным цветом, либо словарём точек с цветами.
        Примеры:
        1. Глобальный цвет: {'global_color': (r, g, b), 'points': [(x1, y1, z1), (x2, y2, z2), ...]}
        2. Индивидуальные цвета: {'individual_color': [(r1, g1, b1), (r2, g2, b2), ...],'points': [(x1, y1, z1), (x2, y2, z2), ...]}

        data может быть трёх типов:
        1. const points: {'global_color or individual_color': (r1, g1, b1),'points': [(x1, y1, z1), (x2, y2, z2), ...]}
        2. const animation: {'delay': 1,
                             'frames': [{'global_color or individual_color': (r1, g1, b1),'points': [(x1, y1, z1), (x2, y2, z2), ...]},
                                        {'global_color or individual_color': (r1, g1, b1),'points': [(x1, y1, z1), (x2, y2, z2), ...]}]
        3. real time animation: Получает color и points через каждый отрезок времени
        """
        if data is not None:
            self.data = data
            self.work = True
            self.vbo = None
            self.vao = None
            self.points = self.data.get('points')
            self.global_color = self.data.get('global_color')
            self.global_color_mode = 'global_color' in self.data

            self.create_render()
        else:
            self.work = False


    def create_render(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_STATIC_DRAW)

        if self.global_color_mode:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
        else:
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glEnable(GL_PROGRAM_POINT_SIZE)
        self.reload_shaders()

    def draw(self, view_matrix, projection_matrix, point_size=5.0):
        if self.work:
            glUseProgram(self.shader)
            model = np.identity(4, dtype=np.float32)

            # Передаем матрицы и размер точки в шейдер
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view_matrix)
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection_matrix)
            glUniform1f(glGetUniformLocation(self.shader, "pointSize"), point_size)

            if self.global_color_mode:
                glUniform3f(glGetUniformLocation(self.shader, "globalColor"), self.global_color[0], self.global_color[1],
                            self.global_color[2])

            glBindVertexArray(self.vao)
            if self.global_color_mode:
                glDrawArrays(GL_POINTS, 0, len(self.points) // 3)
            else:
                glDrawArrays(GL_POINTS, 0, len(self.points) // 6)
            glBindVertexArray(0)

    def reload_shaders(self):
        if self.work:
            if self.global_color_mode:
                vertex_src_global_color = """
                       #version 330 core
                       layout(location = 0) in vec3 aPos;
                       layout(location = 1) in vec3 aColor;
    
                       uniform mat4 model;
                       uniform mat4 view;
                       uniform mat4 projection;
                       uniform float pointSize;
    
                       out vec3 fragColor;
    
                       void main()
                       {
                           gl_Position = projection * view * model * vec4(aPos, 1.0);
                           gl_PointSize = pointSize;  // Устанавливаем размер точки
                       }
                       """

                fragment_src_global_color = """
                                   #version 330 core
                                   out vec4 FragColor;
    
                                   uniform vec3 globalColor;
    
                                   void main()
                                   {
                                       FragColor = vec4(globalColor, 1.0);
                                   }
                                   """
                vertex_shader = compileShader(vertex_src_global_color, GL_VERTEX_SHADER)
                fragment_shader = compileShader(fragment_src_global_color, GL_FRAGMENT_SHADER)
            else:
                vertex_src_individual_colors = """
                                   #version 330 core
                                   layout(location = 0) in vec3 aPos;
                                   layout(location = 1) in vec3 aColor;
    
                                   uniform mat4 model;
                                   uniform mat4 view;
                                   uniform mat4 projection;
                                   uniform float pointSize;
    
                                   out vec3 fragColor;
    
                                   void main()
                                   {
                                       gl_Position = projection * view * model * vec4(aPos, 1.0);
                                       gl_PointSize = pointSize;
                                       fragColor = aColor;
                                   }
                                   """

                fragment_src_individual_colors = """
                                   #version 330 core
                                   in vec3 fragColor;
                                   out vec4 FragColor;
    
                                   void main()
                                   {
                                       FragColor = vec4(fragColor, 1.0);
                                   }
                                   """
                vertex_shader = compileShader(vertex_src_individual_colors, GL_VERTEX_SHADER)
                fragment_shader = compileShader(fragment_src_individual_colors, GL_FRAGMENT_SHADER)
            self.shader = compileProgram(vertex_shader, fragment_shader)

    def set_global_color(self, color):
        if self.work:
            self.global_color = color


class PointEngine():
    def __init__(self, data=None):
        self.data = data
        self.projection = None
        self.render_width = None
        self.gui_width = None
        self.window_height = None
        self.window_width = None
        if not glfw.init():
            print('ERROR WITH glfw.init()')
            return

        self.window = glfw.create_window(1600, 900, "3D Point Engine", None, None)
        if not self.window:
            glfw.terminate()
            print('ERROR WITH glfw.create_window()')
            return

        glfw.make_context_current(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        imgui.create_context()
        self.impl = GlfwRenderer(self.window)
        glEnable(GL_DEPTH_TEST)

        # Generate grid of points
        # animation = {'delay': 1, 'frames': [{'global_color': (1.0, 1.0, 1.0), 'points': [0.0, 0.0, 0.0, 0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.04, 0.04, 0.04, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.1, 0.1, 0.1, 0.11, 0.11, 0.11, 0.12, 0.12, 0.12, 0.13, 0.13, 0.13, 0.14, 0.14, 0.14, 0.15, 0.15, 0.15, 0.16, 0.16, 0.16, 0.17, 0.17, 0.17, 0.18, 0.18, 0.18, 0.19, 0.19, 0.19, 0.2, 0.2, 0.2, 0.21, 0.21, 0.21, 0.22, 0.22, 0.22, 0.23, 0.23, 0.23, 0.24, 0.24, 0.24, 0.25, 0.25, 0.25, 0.26, 0.26, 0.26, 0.27, 0.27, 0.27, 0.28, 0.28, 0.28, 0.29, 0.29, 0.29, 0.3, 0.3, 0.3, 0.31, 0.31, 0.31, 0.32, 0.32, 0.32, 0.33, 0.33, 0.33, 0.34, 0.34, 0.34, 0.35, 0.35, 0.35, 0.36, 0.36, 0.36, 0.37, 0.37, 0.37, 0.38, 0.38, 0.38, 0.39, 0.39, 0.39, 0.4, 0.4, 0.4, 0.41, 0.41, 0.41, 0.42, 0.42, 0.42, 0.43, 0.43, 0.43, 0.44, 0.44, 0.44, 0.45, 0.45, 0.45, 0.46, 0.46, 0.46, 0.47, 0.47, 0.47, 0.48, 0.48, 0.48, 0.49, 0.49, 0.49, 0.5, 0.5, 0.5, 0.51, 0.51, 0.51, 0.52, 0.52, 0.52, 0.53, 0.53, 0.53, 0.54, 0.54, 0.54, 0.55, 0.55, 0.55, 0.56, 0.56, 0.56, 0.57, 0.57, 0.57, 0.58, 0.58, 0.58, 0.59, 0.59, 0.59, 0.6, 0.6, 0.6, 0.61, 0.61, 0.61, 0.62, 0.62, 0.62, 0.63, 0.63, 0.63, 0.64, 0.64, 0.64, 0.65, 0.65, 0.65, 0.66, 0.66, 0.66, 0.67, 0.67, 0.67, 0.68, 0.68, 0.68, 0.69, 0.69, 0.69, 0.7, 0.7, 0.7, 0.71, 0.71, 0.71, 0.72, 0.72, 0.72, 0.73, 0.73, 0.73, 0.74, 0.74, 0.74, 0.75, 0.75, 0.75, 0.76, 0.76, 0.76, 0.77, 0.77, 0.77, 0.78, 0.78, 0.78, 0.79, 0.79, 0.79, 0.8, 0.8, 0.8, 0.81, 0.81, 0.81, 0.82, 0.82, 0.82, 0.83, 0.83, 0.83, 0.84, 0.84, 0.84, 0.85, 0.85, 0.85, 0.86, 0.86, 0.86, 0.87, 0.87, 0.87, 0.88, 0.88, 0.88, 0.89, 0.89, 0.89, 0.9, 0.9, 0.9, 0.91, 0.91, 0.91, 0.92, 0.92, 0.92, 0.93, 0.93, 0.93, 0.94, 0.94, 0.94, 0.95, 0.95, 0.95, 0.96, 0.96, 0.96, 0.97, 0.97, 0.97, 0.98, 0.98, 0.98, 0.99, 0.99, 0.99]},
        #             {'global_color': (1.0, 1.0, 1.0), 'points': [1, 2, 1, 2, 1, 2]}]}

        anim_video_datas = self.data.get_by_type(('animation', 'video'))
        fig_pic_datas = self.data.get_by_type(('figure', 'picture'))

        self.real_time_render = RealTimeRenderer()

        if anim_video_datas:
            for anim_video_data in anim_video_datas:
                self.animation_render = ConstAnimationRenderer(anim_video_data)
        else:
            self.animation_render = ConstAnimationRenderer(None)

        if fig_pic_datas:
            for fig_pic_data in fig_pic_datas:
                self.point_render = ConstPointRenderer(fig_pic_data)
        else:
            self.point_render = ConstPointRenderer(None)

        self.camera = Camera()

        self.last_time = glfw.get_time()
        self.last_x, self.last_y = 400, 300

        self.is_paused = False
        self.q_pressed_last_frame = False
        self.is_running = True

        self.bg_color = [1.0, 1.0, 1.0]
        self.point_size = 1.0
        self.press_ctrl = 1
        self.animation_render.start_timer()

    def update_window(self):
        current_time = glfw.get_time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # Обработка паузы
        self.check_pause()

        if not self.is_paused:
            # Обработка движения камеры только когда не на паузе
            self.processing_key(delta_time)

            # Обработка мыши только когда не на паузе
            self.processing_mouse()

        # Обработка событий ImGui
        self.impl.process_inputs()
        # Начало нового кадра ImGui
        imgui.new_frame()

        menu_open = imgui.begin("Control Panel", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        # Получение размеров окна

        # Изменение размера при закрытии меню
        self.set_size(menu_open.expanded)

        # Рендеринг точек
        self.points_rendering()

        # Рендеринг GUI
        self.gui_rendering()

        # Рендер интерфейса
        imgui.render()
        self.impl.render(imgui.get_draw_data())

        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def gui_rendering(self):
        imgui.set_next_window_position(self.render_width, 0)
        imgui.set_next_window_size(self.gui_width, self.window_height)

        # Кнопки и элементы управления
        if imgui.button("Toggle Background Color"):
            print("toggle Background Color")

        _, self.point_size = imgui.slider_float("Point Size", self.point_size, 1.0, 10.0)
        info_editbg = imgui.color_edit3("Background Color", self.bg_color[0], self.bg_color[1], self.bg_color[2])
        if info_editbg[0]:
            self.bg_color = info_editbg[1]
            self.point_render.set_global_color(self.bg_color)
            self.point_render.reload_shaders()
            self.animation_render.set_global_color(self.bg_color)

        _, self.camera.speed = imgui.slider_float("Camera speed", self.camera.speed, 1.0, 100.0)

        if imgui.button("Toggle Demo Window"):
            print("Toggle Demo Window")

        imgui.text(f"Camera Position: {self.camera.pos}")
        imgui.text(f"Camera front: {self.camera.front}")
        imgui.text(f"Camera right: {self.camera.right}")
        imgui.text(f"Camera up: {self.camera.up}")
        imgui.text(f"Camera pitch: {self.camera.pitch}")
        imgui.text(f"Camera yaw: {self.camera.yaw}")
        imgui.text(f"Camera speed: {self.camera.speed}")
        imgui.text(f"FPS: {imgui.get_io().framerate:.1f}")

        imgui.end()

    def points_rendering(self):
        if self.camera.pos[1] < 0:
            glClearColor(0.0, 0.0, 0.0, 1.0)  # Цвет в формате (R, G, B, A)
        else:
            glClearColor(0.2, 0.5, 0.7, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        view = self.camera.get_view_matrix()
        platform = Platform(size=1000.0)

        platform.draw(view, self.projection, color=(0.4, 0.4, 0.4))
        self.point_render.draw(view, self.projection, self.point_size)

        # Обновление анимации
        self.animation_render.update()
        self.animation_render.draw(view, self.projection, self.point_size)
        #
        # data = {'individual_color': [(0.0, 1.0, 1.0)], 'points': [(0+num, 2, 0), (-0.1+num, 2, 0)]}
        # num += 0.01
        # real_time_render.update_data(data)
        # real_time_render.draw(view, projection, point_size)

    def set_size(self, menu_is_open):
        self.window_width, self.window_height = glfw.get_window_size(self.window)
        self.render_width = self.window_width // 2
        self.gui_width = self.window_width - self.render_width

        if menu_is_open:
            glViewport(0, 0, self.render_width, self.window_height)
            self.projection = perspective_matrix(45, self.render_width / self.window_height, 0.001, 1000.0)
        else:
            glViewport(0, 0, self.window_width, self.window_height)
            self.projection = perspective_matrix(45, self.window_width / self.window_height, 0.001, 1000.0)

    def processing_key(self, delta_time):
        velocity = self.camera.speed * delta_time
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            self.window_close()
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.pos += velocity * self.camera.front * self.press_ctrl
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.pos -= velocity * self.camera.front * self.press_ctrl
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.pos -= velocity * self.camera.right * self.press_ctrl
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.pos += velocity * self.camera.right * self.press_ctrl
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.camera.pos += [0, 0.05 * self.press_ctrl * self.camera.speed, 0]
        if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.camera.pos -= [0, 0.05 * self.press_ctrl * self.camera.speed, 0]

        if glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS:
            self.press_ctrl = 4
        else:
            self.press_ctrl = 1

    def processing_mouse(self):
        xpos, ypos = glfw.get_cursor_pos(self.window)
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x, self.last_y = xpos, ypos

        xoffset *= self.camera.sensitivity
        yoffset *= self.camera.sensitivity

        self.camera.yaw += xoffset
        self.camera.pitch += yoffset

        if self.camera.pitch > 89.0:
            self.camera.pitch = 89.0
        if self.camera.pitch < -89.0:
            self.camera.pitch = -89.0

        front = np.array([
            math.cos(math.radians(self.camera.yaw)) * math.cos(math.radians(self.camera.pitch)),
            math.sin(math.radians(self.camera.pitch)),
            math.sin(math.radians(self.camera.yaw)) * math.cos(math.radians(self.camera.pitch))
        ], dtype=np.float32)
        self.camera.front = front / np.linalg.norm(front)
        self.camera.right = np.cross(self.camera.front, np.array([0.0, 1.0, 0.0], dtype=np.float32))
        self.camera.right /= np.linalg.norm(self.camera.right)
        self.camera.up = np.cross(self.camera.right, self.camera.front)
        self.camera.up /= np.linalg.norm(self.camera.up)

    def check_pause(self):
        q_pressed = glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS
        if q_pressed and not self.q_pressed_last_frame:
            self.is_paused = not self.is_paused

            if self.is_paused:
                glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            else:
                glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                glfw.set_cursor_pos(self.window, 400, 300)
                self.last_x, self.last_y = 400, 300

        self.q_pressed_last_frame = q_pressed
        return self.is_paused

    def check_window(self):
        return not glfw.window_should_close(self.window)

    def check_running(self):
        return self.is_running

    def window_close(self):
        glfw.terminate()
        self.is_running = False

    def get_status(self):
        return self.check_window() == self.check_running()

def main():
    pe = PointEngine()
    while pe.get_status():
        pe.update_window()

if __name__ == "__main__":
    main()
