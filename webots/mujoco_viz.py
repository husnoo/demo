# This one started life as part of this course: https://pab47.github.io/mujocopy.html
# I've converted it into a reusable object and added the multi-sim version

import mujoco as mj
from mujoco.glfw import glfw
import numpy as np
import os
from scipy.spatial.transform import Rotation as R


def quat2euler(quat_mujoco):
    #mujocoy quat is constant,x,y,z,
    #scipy quaut is x,y,z,constant
    quat_scipy = np.array([quat_mujoco[3],quat_mujoco[0],quat_mujoco[1],quat_mujoco[2]])

    r = R.from_quat(quat_scipy)
    euler = r.as_euler('xyz', degrees=True)

    return euler


class Visualiser:
    def __init__(self, model, data):
        self.model = model
        self.data = data

        self.button_left = False
        self.button_middle = False
        self.button_right = False
        self.lastx = 0
        self.lasty = 0
        self.cam = mj.MjvCamera()                        # Abstract camera
        self.opt = mj.MjvOption()                        # visualization options
        glfw.init()
        self.window = glfw.create_window(1200, 900, "Demo", None, None)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        mj.mjv_defaultCamera(self.cam)
        mj.mjv_defaultOption(self.opt)
        self.scene = mj.MjvScene(self.model, maxgeom=10000)
        self.context = mj.MjrContext(self.model, mj.mjtFontScale.mjFONTSCALE_150.value)
        glfw.set_key_callback(self.window, self.keyboard)
        glfw.set_cursor_pos_callback(self.window, self.mouse_move)
        glfw.set_mouse_button_callback(self.window, self.mouse_button)
        glfw.set_scroll_callback(self.window, self.scroll)

        self.cam.azimuth = 90
        self.cam.elevation = -45
        self.cam.distance =  13
        self.cam.lookat = np.array([ 0.0 , 0.0 , 0.0 ])

    def keyboard(self, window, key, scancode, act, mods):
        if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
            mj.mj_resetData(self.model, self.data)
            mj.mj_forward(self.model, self.data)
        elif act == glfw.PRESS and key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self.window, True)

    def mouse_button(self, window, button, act, mods):
        self.button_left = (glfw.get_mouse_button(
            window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS)
        self.button_middle = (glfw.get_mouse_button(
            window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS)
        self.button_right = (glfw.get_mouse_button(
            window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS)
        # update mouse position
        glfw.get_cursor_pos(self.window)

    def mouse_move(self, window, xpos, ypos):
        # compute mouse displacement, save
        dx = xpos - self.lastx
        dy = ypos - self.lasty
        self.lastx = xpos
        self.lasty = ypos
        
        # no buttons down: nothing to do
        if (not self.button_left) and (not self.button_middle) and (not self.button_right):
            return

        # get current window size
        width, height = glfw.get_window_size(self.window)

        # get shift key state
        PRESS_LEFT_SHIFT = glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        PRESS_RIGHT_SHIFT = glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
        mod_shift = (PRESS_LEFT_SHIFT or PRESS_RIGHT_SHIFT)

        # determine action based on mouse button
        if self.button_right:
            if mod_shift:
                action = mj.mjtMouse.mjMOUSE_MOVE_H
            else:
                action = mj.mjtMouse.mjMOUSE_MOVE_V
        elif self.button_left:
            if mod_shift:
                action = mj.mjtMouse.mjMOUSE_ROTATE_H
            else:
                action = mj.mjtMouse.mjMOUSE_ROTATE_V
        else:
            action = mj.mjtMouse.mjMOUSE_ZOOM

        mj.mjv_moveCamera(self.model, action, dx/height, dy/height, self.scene, self.cam)

    def scroll(self, window, xoffset, yoffset):
        action = mj.mjtMouse.mjMOUSE_ZOOM
        mj.mjv_moveCamera(self.model, action, 0.0, -0.05 * yoffset, self.scene, self.cam)


    #def __del__(self):
    #    glfw.terminate()


    def should_continue(self):
        return (not glfw.window_should_close(self.window))


    def update_scene(self):
        # get framebuffer viewport
        viewport_width, viewport_height = glfw.get_framebuffer_size(self.window)
        viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

        # frame = np.zeros((viewport_height, viewport_width, 3), dtype=np.uint8)
        
        # Update scene and render
        mj.mjv_updateScene(self.model, self.data, self.opt, None, self.cam,
                           mj.mjtCatBit.mjCAT_ALL.value, self.scene)
        mj.mjr_render(viewport, self.scene, self.context)
        mj.mjr_overlay(mj.mjtFontScale.mjFONTSCALE_150, mj.mjtGridPos.mjGRID_TOPLEFT,
                       viewport, "Time {:.2f}".format(self.data.time),"", self.context)

        # swap OpenGL buffers (blocking call due to v-sync)
        glfw.swap_buffers(self.window)
        # process pending GUI events, call GLFW callbacks
        glfw.poll_events()

        # mj.mjr_readPixels(frame.ctypes.data, viewport, self.context)
        # cv2.imwrite('frame_1.png', frame)

        #from PIL import Image
        #im = Image.fromarray(arr)
        # image.save("tmp1.png", compress_level=1) # PIL

        #import scipy.misc
        #scipy.misc.imsave('outfile.jpg', image_array)

        # subprocess.run(['ffmpeg', '-framerate', '30', '-i', 'frame_%d.png', '-c:v', 'mpeg2video', '-q:v', '5', 'output_video.mpg'])






def divide_viewport(viewport_width, viewport_height, nmodels):
    # Determine the grid size (rows and cols)
    import math
    rows = int(math.sqrt(nmodels))
    cols = nmodels // rows

    # Adjust for non-square grids if necessary
    if rows * cols < nmodels:
        rows += 1

    # Box dimensions
    box_width = viewport_width / cols
    box_height = viewport_height / rows

    # Compute box coordinates
    boxes = []
    for i in range(nmodels):
        row = i // cols
        col = i % cols
        x0 = col * box_width
        y0 = row * box_height
        x1 = x0 + box_width
        y1 = y0 + box_height
        boxes.append((x0, y0, x1, y1))
    return boxes


class VisualiserMulti:
    def __init__(self, models, data):
        # pass as many pairs of models and data as we want (but maybe stick to 2,4,8,16)
        self.models = models
        self.data = data
        self.scenes = []
        self.contexts = []
        self.nmodels = len(models)

        self.cam = mj.MjvCamera()
        self.opt = mj.MjvOption()
        glfw.init()
        self.window = glfw.create_window(1200, 900, "Demo", None, None)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        mj.mjv_defaultCamera(self.cam)
        mj.mjv_defaultOption(self.opt)
        glfw.set_key_callback(self.window, self.keyboard)

        for i in range(self.nmodels):        
            self.scenes.append(mj.MjvScene(self.models[i], maxgeom=10000))
            self.contexts.append(mj.MjrContext(self.models[i], mj.mjtFontScale.mjFONTSCALE_150.value))

        self.cam.azimuth = 90
        self.cam.elevation = -45
        self.cam.distance =  13
        self.cam.lookat = np.array([ 0.0 , 0.0 , 0.0 ])

    def keyboard(self, window, key, scancode, act, mods):
        if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
            for i in range(self.nmodels):                    
                mj.mj_resetData(self.models[i], self.data[i])
                mj.mj_forward(self.models[i], self.data[i])
        elif act == glfw.PRESS and key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self.window, True)

    #def __del__(self):
    #    glfw.terminate()

    def should_continue(self):
        return (not glfw.window_should_close(self.window))

    def update_scene(self):
        # get framebuffer viewport
        viewport_width, viewport_height = glfw.get_framebuffer_size(self.window)





        # Divide up the window and loop over the models
        boxes = divide_viewport(viewport_width, viewport_height, self.nmodels)
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            #print(f"nmodels={self.nmodels} Box {i}: x0={x0}, y0={y0}, x1={x1}, y1={y1}") 
            viewport = mj.MjrRect(int(x0), int(y0), int(x1-x0), int(y1-y0))
            mj.mjv_updateScene(self.models[i], self.data[i], self.opt, None, self.cam,
                               mj.mjtCatBit.mjCAT_ALL.value, self.scenes[i])
            mj.mjr_render(viewport, self.scenes[i], self.contexts[i])
            mj.mjr_overlay(mj.mjtFontScale.mjFONTSCALE_150, mj.mjtGridPos.mjGRID_TOPLEFT,
                           viewport, "Time {:.2f}".format(self.data[i].time),"", self.contexts[i])
        
        # swap OpenGL buffers (blocking call due to v-sync)
        glfw.swap_buffers(self.window)
        # process pending GUI events, call GLFW callbacks
        glfw.poll_events()





# Example usage
#viewport_width = 1920
#viewport_height = 1080
#for nmodels in [1,2,4,8,16,32]:
#    boxes = divide_viewport(viewport_width, viewport_height, nmodels)
#    for i, (x0, y0, x1, y1) in enumerate(boxes):
#        print(f"nmodels={nmodels} Box {i}: x0={x0}, y0={y0}, x1={x1}, y1={y1}")

