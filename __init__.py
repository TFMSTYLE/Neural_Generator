# SPDX-FileCopyrightText: 2025-2026 The French Monkey
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Neural",
    "author": "The French Monkey",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Neural",
    "description": "Generate parametric neurals",
    "category": "Add Mesh",
    "license": "GPL-3.0-or-later",
}

import bpy
import random
from math import sin, cos, pi
from mathutils import Vector

# ------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------

def build_curve_from_branches(verts, edges, name="NeuralCurve", taper_factor=0.3):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.02
    curve_data.bevel_resolution = 4
    curve_data.fill_mode = 'FULL'
    curve_data.use_fill_caps = True
    curve_data.use_radius = True

    num_verts = len(verts)
    graph = [[] for _ in range(num_verts)]

    for a, b in edges:
        if a != b:
            graph[a].append(b)
            graph[b].append(a)

    vertex_depth = [-1] * num_verts
    vertex_depth[0] = 0
    max_depth = 0
    queue = [0]

    while queue:
        current = queue.pop(0)
        current_depth = vertex_depth[current]
        for neighbor in graph[current]:
            if vertex_depth[neighbor] == -1:
                vertex_depth[neighbor] = current_depth + 1
                max_depth = max(max_depth, current_depth + 1)
                queue.append(neighbor)

    if max_depth > 0:
        inv_max_depth = 1.0 / max_depth
        taper_range = 1.0 - taper_factor
        radii = [1.0 - (depth * inv_max_depth * taper_range) for depth in vertex_depth]
    else:
        radii = [1.0] * num_verts

    visited_edges = set()

    def create_spline_from_path(path, start_idx, neighbor_idx):
        if not path:
            return

        start_pos = Vector(verts[start_idx])
        neighbor_pos = Vector(verts[neighbor_idx])
        offset_vec = (neighbor_pos - start_pos) * 0.05
        offset_point = start_pos + offset_vec

        total_points = 2 + len(path)
        spline = curve_data.splines.new('POLY')
        spline.points.add(total_points - 1)
        spline.use_smooth = True

        points = spline.points
        points[0].co = (*verts[start_idx], 1.0)
        points[0].radius = radii[start_idx]
        points[1].co = (offset_point.x, offset_point.y, offset_point.z, 1.0)
        points[1].radius = radii[start_idx]

        for i, v_idx in enumerate(path, start=2):
            points[i].co = (*verts[v_idx], 1.0)
            points[i].radius = radii[v_idx]

    def trace_all_paths_from_node(start_idx, parent_idx=-1):
        neighbors = [n for n in graph[start_idx] if n != parent_idx]

        for neighbor in neighbors:
            edge_key = (min(start_idx, neighbor), max(start_idx, neighbor))
            if edge_key in visited_edges:
                continue

            path = [neighbor]
            visited_edges.add(edge_key)
            current = neighbor
            previous = start_idx

            while True:
                next_nodes = [n for n in graph[current] if n != previous]
                if len(next_nodes) != 1:
                    break

                next_node = next_nodes[0]
                edge_key = (min(current, next_node), max(current, next_node))

                if edge_key in visited_edges:
                    break

                visited_edges.add(edge_key)
                path.append(next_node)
                previous = current
                current = next_node

            create_spline_from_path(path, start_idx, neighbor)

            end_node = path[-1]
            unvisited = any(
                (min(end_node, n), max(end_node, n)) not in visited_edges
                for n in graph[end_node]
            )

            if unvisited:
                trace_all_paths_from_node(end_node, previous)

    trace_all_paths_from_node(0)
    return curve_data

# ------------------------------------------------------------------------
# Neural Graph Generation Algorithms
# ------------------------------------------------------------------------

def generate_radial_pattern(branches=20, depth=4, spread=0.5, seed=1, 
                           branch_angle=45, length_decay=0.7, twist=0.0):
    rng = random.Random(int(seed))
    verts = [(0.0, 0.0, 0.0)]
    edges = []
    angle_rad = branch_angle * (pi / 180)
    for i in range(branches):
        base_angle = (2 * pi * i / branches)
        angle = base_angle + (twist * (i / branches))
        length = rng.uniform(0.5, 1.0)
        x = length * cos(angle)
        y = length * sin(angle)
        z = rng.uniform(-spread, spread)
        verts.append((x, y, z))
        edges.append((0, len(verts) - 1))
        _generate_branch_advanced(verts, edges, len(verts) - 1, depth, spread, 
                                 rng, length_decay, angle_rad, angle)
    return verts, edges

def generate_organic_pattern(branches=20, depth=4, spread=0.5, seed=1,
                            branch_angle=45, length_decay=0.7, attraction_strength=0.3):
    rng = random.Random(int(seed))
    verts = [(0.0, 0.0, 0.0)]
    edges = []
    angle_rad = branch_angle * (pi / 180)
    for i in range(branches):
        angle = rng.uniform(0, 2 * pi)
        elevation = rng.uniform(-pi/4, pi/4)
        length = rng.uniform(0.5, 1.0)
        x = length * cos(angle) * cos(elevation)
        y = length * sin(angle) * cos(elevation)
        z = length * sin(elevation) + rng.uniform(-spread, spread)
        verts.append((x, y, z))
        edges.append((0, len(verts) - 1))
        _generate_organic_branch(verts, edges, len(verts) - 1, depth, spread,
                                rng, length_decay, angle_rad, attraction_strength)
    return verts, edges

def generate_neural_tree(branches=20, depth=4, spread=0.5, seed=1,
                        branch_angle=45, length_decay=0.7, tropism=(0, 0, 1)):
    rng = random.Random(int(seed))
    verts = [(0.0, 0.0, 0.0)]
    edges = []
    angle_rad = branch_angle * (pi / 180)
    tropism_vec = Vector(tropism).normalized()
    trunk_height = rng.uniform(1.0, 2.0)
    verts.append((0.0, 0.0, trunk_height))
    edges.append((0, 1))
    for i in range(branches):
        z_pos = trunk_height * (0.3 + 0.7 * (i / branches))
        angle = rng.uniform(0, 2 * pi)
        length = rng.uniform(0.4, 0.8)
        x = length * cos(angle)
        y = length * sin(angle)
        z = z_pos + rng.uniform(-spread, spread)
        verts.append((x, y, z))
        parent_idx = 1 if z_pos < trunk_height * 0.7 else 0
        edges.append((parent_idx, len(verts) - 1))
        _generate_tropism_branch(verts, edges, len(verts) - 1, depth, spread,
                                rng, length_decay, angle_rad, tropism_vec)
    return verts, edges

def _generate_branch_advanced(verts, edges, parent, depth, spread, rng, 
                              length_decay, branch_angle, base_rotation=0):
    if depth <= 0:
        return
    num_children = rng.randint(1, 3)
    px, py, pz = verts[parent]
    spread_half = spread * 0.5
    spread_reduced = spread * 0.8
    for _ in range(num_children):
        angle = base_rotation + rng.uniform(-branch_angle, branch_angle)
        length = rng.uniform(0.3, 0.7) * length_decay
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        x = px + length * cos_angle
        y = py + length * sin_angle
        z = pz + rng.uniform(-spread_half, spread_half)
        verts.append((x, y, z))
        child = len(verts) - 1
        edges.append((parent, child))
        _generate_branch_advanced(verts, edges, child, depth - 1, spread_reduced, 
                                 rng, length_decay, branch_angle, angle)

def _generate_organic_branch(verts, edges, parent, depth, spread, rng,
                            length_decay, branch_angle, attraction):
    if depth <= 0:
        return
    num_children = rng.randint(1, 2)
    px, py, pz = verts[parent]
    parent_pos = Vector((px, py, pz))
    pi_sixth = pi / 6
    spread_third = spread * 0.3
    spread_reduced = spread * 0.85
    for _ in range(num_children):
        angle = rng.uniform(0, 2 * pi)
        elevation = rng.uniform(-pi_sixth, pi_sixth)
        length = rng.uniform(0.3, 0.6) * length_decay
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        cos_elev = cos(elevation)
        sin_elev = sin(elevation)
        attraction_vec = parent_pos.normalized() * (-attraction * length)
        x = px + length * cos_angle * cos_elev + attraction_vec.x
        y = py + length * sin_angle * cos_elev + attraction_vec.y
        z = pz + length * sin_elev + attraction_vec.z + rng.uniform(-spread_third, spread_third)
        verts.append((x, y, z))
        child = len(verts) - 1
        edges.append((parent, child))
        _generate_organic_branch(verts, edges, child, depth - 1, spread_reduced,
                                rng, length_decay, branch_angle, attraction)

def _generate_tropism_branch(verts, edges, parent, depth, spread, rng,
                             length_decay, branch_angle, tropism_vec):
    if depth <= 0:
        return
    num_children = rng.randint(1, 2)
    px, py, pz = verts[parent]
    spread_third = spread * 0.3
    spread_reduced = spread * 0.85
    for _ in range(num_children):
        angle = rng.uniform(0, 2 * pi)
        length = rng.uniform(0.3, 0.6) * length_decay
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        tropism_influence = tropism_vec * (length * 0.3)
        x = px + length * cos_angle + tropism_influence.x
        y = py + length * sin_angle + tropism_influence.y
        z = pz + rng.uniform(-spread_third, spread_third) + tropism_influence.z
        verts.append((x, y, z))
        child = len(verts) - 1
        edges.append((parent, child))
        _generate_tropism_branch(verts, edges, child, depth - 1, spread_reduced,
                                rng, length_decay, branch_angle, tropism_vec)

# ------------------------------------------------------------------------
# Generation Logic
# ------------------------------------------------------------------------

def rebuild_neural(obj):
    if not obj or obj.type != "CURVE":
        return False
    p = obj.get("neural_props")
    if not p:
        return False
    pattern_type = p.get("pattern_type", "RADIAL")
    if pattern_type == "RADIAL":
        verts, edges = generate_radial_pattern(
            branches=p["branches"],
            depth=p["depth"],
            spread=p["spread"],
            seed=p["seed"],
            branch_angle=p.get("branch_angle", 45),
            length_decay=p.get("length_decay", 0.7),
            twist=p.get("twist", 0.0)
        )
    elif pattern_type == "ORGANIC":
        verts, edges = generate_organic_pattern(
            branches=p["branches"],
            depth=p["depth"],
            spread=p["spread"],
            seed=p["seed"],
            branch_angle=p.get("branch_angle", 45),
            length_decay=p.get("length_decay", 0.7),
            attraction_strength=p.get("attraction_strength", 0.3)
        )
    elif pattern_type == "TREE":
        verts, edges = generate_neural_tree(
            branches=p["branches"],
            depth=p["depth"],
            spread=p["spread"],
            seed=p["seed"],
            branch_angle=p.get("branch_angle", 45),
            length_decay=p.get("length_decay", 0.7),
            tropism=p.get("tropism", (0, 0, 1))
        )
    else:
        return False
    taper_factor = p.get("taper_factor", 0.3)
    curve_data = build_curve_from_branches(verts, edges, "Neural_Network", taper_factor)
    curve_data.bevel_depth = p.get("bevel_depth", 0.02)
    curve_data.bevel_resolution = p.get("bevel_resolution", 4)
    curve_data.use_fill_caps = True
    old = obj.data
    obj.data = curve_data
    if old and old.users == 0:
        bpy.data.curves.remove(old)
    obj.name = obj.data.name = "Neural_Network"
    return True

def generate_neural(context):
    p = context.scene.neuralgen_props
    obj = context.active_object
    keys = ("branches", "depth", "spread", "seed", "pattern_type", 
            "branch_angle", "length_decay", "twist", "attraction_strength",
            "bevel_depth", "bevel_resolution", "taper_factor")
    if obj and obj.type == "CURVE" and "neural_generator" in obj and obj.select_get():
        props = obj.get("neural_props", {})
        for k in keys:
            props[k] = getattr(p, k)
        obj["neural_props"] = props
        rebuild_neural(obj)
        return obj
    curve_data = bpy.data.curves.new("NeuralCurve", type='CURVE')
    new_obj = bpy.data.objects.new("NeuralNetwork", curve_data)
    context.collection.objects.link(new_obj)
    context.view_layer.objects.active = new_obj
    new_obj.select_set(True)
    new_obj["neural_generator"] = True
    new_obj["neural_props"] = {k: getattr(p, k) for k in keys}
    rebuild_neural(new_obj)
    return new_obj

# ------------------------------------------------------------------------
# Live Update
# ------------------------------------------------------------------------

def update_neural(self, context):
    p = context.scene.neuralgen_props
    if not p.live_update:
        return
    
    obj = context.active_object
    if not obj or obj.type != "CURVE" or "neural_generator" not in obj or not obj.select_get():
        return
    
    props = obj.get("neural_props", {})
    props["branches"] = p.branches
    props["depth"] = p.depth
    props["spread"] = p.spread
    props["seed"] = p.seed
    props["pattern_type"] = p.pattern_type
    props["branch_angle"] = p.branch_angle
    props["length_decay"] = p.length_decay
    props["twist"] = p.twist
    props["attraction_strength"] = p.attraction_strength
    props["bevel_depth"] = p.bevel_depth
    props["bevel_resolution"] = p.bevel_resolution
    props["taper_factor"] = p.taper_factor
    
    obj["neural_props"] = props
    rebuild_neural(obj)

# ------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------

class NeuralGenProperties(bpy.types.PropertyGroup):
    live_update: bpy.props.BoolProperty(name="Live Update", default=False)
    pattern_type: bpy.props.EnumProperty(
        name="Pattern",
        items=[("RADIAL", "Radial", ""), ("ORGANIC", "Organic", ""), ("TREE", "Tree", "")],
        default="RADIAL", update=update_neural
    )
    branches: bpy.props.IntProperty(name="Branches", default=20, min=1, max=200, subtype='FACTOR', update=update_neural)
    depth: bpy.props.IntProperty(name="Depth", default=4, min=1, max=10, subtype='FACTOR', update=update_neural)
    spread: bpy.props.FloatProperty(name="Spread", default=0.5, min=0.0, max=5.0, subtype='FACTOR', update=update_neural)
    seed: bpy.props.IntProperty(name="Seed", default=1, min=0, max=10000, subtype='FACTOR', update=update_neural)
    branch_angle: bpy.props.FloatProperty(name="Branch Angle", default=45.0, min=0.0, max=180.0, subtype='FACTOR', update=update_neural)
    length_decay: bpy.props.FloatProperty(name="Length Decay", default=0.7, min=0.1, max=1.0, subtype='FACTOR', update=update_neural)
    twist: bpy.props.FloatProperty(name="Twist", default=0.0, min=-3.14, max=3.14, subtype='FACTOR', update=update_neural)
    attraction_strength: bpy.props.FloatProperty(name="Attraction", default=0.3, min=0.0, max=1.0, subtype='FACTOR', update=update_neural)
    bevel_depth: bpy.props.FloatProperty(name="Thickness", default=0.02, min=0.001, max=1.0, subtype='FACTOR', update=update_neural)
    bevel_resolution: bpy.props.IntProperty(name="Resolution", default=4, min=0, max=32, subtype='FACTOR', update=update_neural)
    taper_factor: bpy.props.FloatProperty(name="Tip Taper", default=0.3, min=0.0, max=1.0, subtype='FACTOR', update=update_neural)

# ------------------------------------------------------------------------
# Operator
# ------------------------------------------------------------------------

class NEURALGEN_OT_generate(bpy.types.Operator):
    bl_idname = "neural.generate"
    bl_label = "Generate Neural"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = generate_neural(context)
        if obj:
            self.report({'INFO'}, f"Generated neural network: {obj.name}")
        return {"FINISHED"}

# ------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------

class VIEW3D_PT_neural_generator(bpy.types.Panel):
    bl_label = "Neural"
    bl_idname = "VIEW3D_PT_neural_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Neural" 

    def draw(self, context):
        layout = self.layout
        p = context.scene.neuralgen_props
        o = context.object

        layout.operator("neural.generate", text="Generate Neural Network", icon="FREEZE")

        layout.prop(p, "live_update", toggle=True)
        layout.separator(factor=0.5)

        layout.prop(p, "pattern_type")

        layout.prop(p, "branches")
        layout.prop(p, "depth")
        layout.prop(p, "spread")
        layout.prop(p, "seed")

        layout.separator(factor=0.5)

        layout.prop(p, "branch_angle")
        layout.prop(p, "length_decay")

        if p.pattern_type == "RADIAL":
            layout.prop(p, "twist")
        elif p.pattern_type == "ORGANIC":
            layout.prop(p, "attraction_strength")

        layout.separator(factor=0.5)

        layout.prop(p, "bevel_depth")
        layout.prop(p, "bevel_resolution")
        layout.prop(p, "taper_factor")

        layout.separator(factor=0.5)

        if (
            o
            and o.type == "CURVE"
            and "neural_generator" in o
            and o.select_get()
        ):
            layout.label(text=f"Editing: {o.name}", icon="FREEZE")
        else:
            layout.label(text="No neural selected", icon="INFO")

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    NeuralGenProperties,
    NEURALGEN_OT_generate,
    VIEW3D_PT_neural_generator, 
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.neuralgen_props = bpy.props.PointerProperty(type=NeuralGenProperties)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.neuralgen_props

if __name__ == "__main__":
    register()