#----------------------------------------------------------
# File blender_mesh.py
#----------------------------------------------------------
#
# How to execute script
#
# blender --background --python image_to_mesh.py -- ./grid.bmp
#
import bpy
import sys
import numpy as np


def load_image(path):
    """Load image, convert to grayscale, and save into numpy array"""
    # Load image in DB
    bpy_img = bpy.data.images.load(path)
    width, height = bpy_img.size[0], bpy_img.size[1]
    arr = np.array(bpy_img.pixels[:])
    
    # Blender store images as a list containing the RGBA components
    # of each pixel, Here they are converted into grayscale, and then
    # reshaped into a 2D array
    grid = np.zeros(len(arr)/4)
    for x in range(0, len(arr), 4):
        grid[x/4] = (arr[x]+arr[x+1]+arr[x+2])/3

    return np.reshape(grid, (width, height))

def grid_to_mesh(grid, cell_width, cell_height, hole_func=None):
    """
    Generate mesh from 

    Arguments:
        grid (numpy array):
        cell_width (number):
        cell_width (number):
        hole_func (callable): Function that determines if a cell is a hole
            in the grid or solid

    Returns:
        vertices (list):
        faces (list):
    """
    width, height = grid.shape
    width += 1
    height += 1

    vertex_dict = {}

    vertices = []
    faces = []

    if hole_func is None:
        hole_func = lambda x: x==0

    def vertex_id(vertex):
        """
        Returns vertex id, or assigns a new unique one if there was None.
        """
        vid = vertex_dict.get(vertex, None)

        if vid is None:
            vertices.append(vertex)
            vid = len(vertices)-1
            vertex_dict[vertex] = vid

        return vid

    # Create faces
    for cell, value in np.ndenumerate(grid):
        if hole_func(value):
            continue

        x, y = cell
        top_left = vertex_id((x, y+1))
        top_right = vertex_id((x+1, y+1))
        bottom_left = vertex_id((x, y))
        bottom_right = vertex_id((x+1, y))
        faces.append((bottom_left, bottom_right, top_right, top_left))


    # Convert vertices to real dimmensions using cell width and cell height
    vertices = [(x*cell_width, y*cell_height) for x, y in vertices]

    return vertices, faces


def createMesh(name, origin, verts, edges, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
    # Link object to scene
    bpy.context.scene.objects.link(ob)
 
    # Create mesh from given verts, edges, faces. Either edges or
    # faces should be [], or you ask for problems
    me.from_pydata(verts, edges, faces)
 
    # Update mesh with new data
    me.update(calc_edges=True)
    return ob


def run(origin, imgpath):
    threshold = 0.5

    # Load image into blender and then into numpy array
    img = load_image(imgpath)

    # Use threshold to determine what pixels are holes
    low_values_indices = img < threshold  # Where values are low
    img[img<threshold] = 0
    img[img>threshold] = 255
    # Create 2D hole grid
    verts, faces = grid_to_mesh(img, 0.1, 0.1)

    # Add third dimmension
    d_verts = [(x, y, 0.) for x, y in verts]
    d_faces = faces

    # Create mesh inside blender
    ob = createMesh('Image_mesh', origin, d_verts, [], d_faces)
    
    # Save result as output.blend
    bpy.ops.wm.save_as_mainfile(filepath="output.blend")
 
if __name__ == "__main__":

    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    path = argv[0]

    run((0,0,0), path)
