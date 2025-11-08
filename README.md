# Neural Generator

![neural-thumb](https://github.com/user-attachments/assets/66f26c8d-ac34-4099-90e4-fab16ab1d8a3)

**Author:** The French Monkey (TFMSTYLE)  
**Version:** 1.0.0  

---

## Overview

The Neural Generator creates branching, neuron-like curve structures procedurally.  
It uses recursive algorithms to simulate organic growth, neural branching, and radial or tree-based formations.  
Each generated network is a single beveled curve with adjustable tapering and resolution, making it ideal for creating neural webs, abstract designs, or natural growth systems.  
The add-on provides multiple generation modes with fine control over branching depth, spread, and curvature style.

---

## Parameters

### Live Update
When enabled, automatically rebuilds the active neural structure whenever a parameter changes.  
Useful for iterative visual design, but may slow down for large or complex patterns.

---

### Pattern
Defines the underlying generation algorithm.  
Available types include:

- **Radial:** Produces symmetrical, starburst-like neuron networks emanating from a central root.  
- **Organic:** Creates freeform, biologically inspired branches with attraction bias and irregular flow.  
- **Tree:** Generates directional, plant-like growth patterns influenced by a vertical tropism vector.

---

### Branches
Sets the number of primary branches extending from the central origin.  
Increasing this value adds complexity and density to the generated structure.

---

### Depth
Controls how many recursive levels of branching are produced.  
Higher depth values result in more detailed, multi-tiered networks.

---

### Spread
Adjusts the spatial variation of branch positioning along each generation step.  
Larger values create looser, more chaotic networks.

---

### Seed
Defines the random number seed for the generator.  
Changing this produces different variations of the same parameters.

---

### Branch Angle
Specifies the maximum angular deviation of each branch from its parent direction.  
Larger angles create wider, more open patterns.

---

### Length Decay
Controls how quickly the length of each branch segment decreases over successive generations.  
Lower values produce faster tapering and more compact forms.

---

### Twist
Applies a rotational offset around the center for radial-style patterns.  
Useful for creating spiral or vortex-like structures.

---

### Attraction
Determines how strongly branches curve inward toward the origin.  
Higher values create more tangled, clustered networks.  
This parameter is used primarily in **Organic** mode.

---

### Thickness
Sets the bevel depth of the curve, determining the overall tube diameter.  
Increasing this makes the neural strands thicker.

---

### Resolution
Controls the bevel resolution for the curve’s cross-section.  
Higher values yield smoother, rounder strands.

---

### Tip Taper
Defines how much the strand thickness decreases toward the outermost tips.  
Higher values create more pronounced tapering, enhancing organic realism.

---

## Operators

### Generate Neural
Creates a new neural curve structure based on the current parameters, or regenerates the selected one if it was produced by the Neural Generator.  
The resulting object is a fully parametric 3D curve with adjustable bevel and tapering attributes.

---

## Usage Notes

- Choose a **Pattern Type** (Radial, Organic, or Tree) to determine the overall branching behavior.  
- Adjust **Branches**, **Depth**, and **Spread** to balance density and complexity.  
- Use **Thickness**, **Resolution**, and **Tip Taper** to refine visual quality and realism.  
- Enable **Live Update** to experiment interactively while tuning parameters.  
- Generated curves are procedural and can be converted to mesh for sculpting, rendering, or further processing.  
- The generator is designed for creative visualization — not anatomical or scientific simulation.
