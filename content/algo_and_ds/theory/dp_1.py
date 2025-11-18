import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from PIL import Image  # Import Pillow for image manipulation


# --- find_all_paths function (from previous response) ---
def find_all_paths(m, n):
    all_paths = []

    def backtrack(row, col, current_path):
        current_path.append((row, col))
        if row == m - 1 and col == n - 1:
            all_paths.append(list(current_path))
            current_path.pop()
            return
        if row + 1 < m:
            backtrack(row + 1, col, current_path)
        if col + 1 < n:
            backtrack(row, col + 1, current_path)
        current_path.pop()

    backtrack(0, 0, [])
    return all_paths


# --- visualize_path_and_save function (unchanged, as it's needed for individual images) ---
def visualize_path_and_save(m, n, path, path_number, total_paths, output_dir="grid_paths"):
    """
    Uses Matplotlib to draw a grid and highlight a specific path, then saves it.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fig, ax = plt.subplots(figsize=(n, m))

    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(m - 0.5, -0.5)

    for r in range(m):
        for c in range(n):
            ax.add_patch(patches.Rectangle(
                (c - 0.5, r - 0.5), 1, 1,
                fill=False, edgecolor='black', lw=0.5
            ))

    ax.add_patch(patches.Rectangle((-0.5, -0.5), 1, 1, facecolor='lightgreen', alpha=0.6))
    ax.text(0, 0, "START", ha='center', va='center', fontsize=12, color='darkgreen', weight='bold')

    ax.add_patch(patches.Rectangle((n - 1.5, m - 1.5), 1, 1, facecolor='salmon', alpha=0.6))
    ax.text(n - 1, m - 1, "END", ha='center', va='center', fontsize=12, color='darkred', weight='bold')

    path_rows = [r for r, c in path]
    path_cols = [c for r, c in path]

    ax.plot(path_cols, path_rows,
            marker='o',
            markersize=8,
            linestyle='-',
            lw=3,
            color='blue')

    ax.set_title(f"Path {path_number} of {total_paths}", fontsize=16)
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(m))
    ax.set_xticklabels([f'Col {i}' for i in range(n)])
    ax.set_yticklabels([f'Row {i}' for i in range(m)])
    ax.grid(which='major', linestyle=':', lw=1, color='gray')
    ax.set_aspect('equal')

    filename = os.path.join(output_dir, f"path_{path_number:02d}.png")
    plt.savefig(filename, bbox_inches='tight', dpi=100)  # Lower DPI for collage might be fine
    plt.close(fig)


# --- NEW: Function to create a collage from individual images ---
def create_collage(image_files, output_filename, rows, cols):
    """
    Stitches multiple image files into a single collage.
    """
    if not image_files:
        print("No images to create a collage.")
        return

    # Open all images to get their dimensions
    images = [Image.open(f) for f in image_files]

    # Assuming all images are the same size
    img_width, img_height = images[0].size

    # Calculate the size of the final collage
    collage_width = cols * img_width
    collage_height = rows * img_height

    # Create a new blank image for the collage
    collage_image = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))  # White background

    # Paste each image into the collage
    for index, img in enumerate(images):
        r = index // cols
        c = index % cols
        x_offset = c * img_width
        y_offset = r * img_height
        collage_image.paste(img, (x_offset, y_offset))

    collage_image.save(output_filename)
    print(f"Collage saved as '{output_filename}'")


# --- Main code to generate all images and then the collage ---
m_rows = 4
n_cols = 4

print(f"Finding all paths for a {m_rows}x{n_cols} grid...")
all_paths = find_all_paths(m_rows, n_cols)
num_paths = len(all_paths)
print(f"Total paths found: {num_paths}")

output_directory = "grid_paths_4x4"
collage_filename = "all_20_paths_collage.png"

# 1. Generate individual path images
print(f"Generating and saving {num_paths} individual images to '{output_directory}' directory...")
for i, path in enumerate(all_paths):
    visualize_path_and_save(m_rows, n_cols, path, i + 1, num_paths, output_directory)
    if (i + 1) % 5 == 0:
        print(f"  Saved {i + 1}/{num_paths} paths...")
print(f"All individual path images saved successfully in the '{output_directory}' directory!")

# 2. Create the collage
print(f"\nCreating the collage image '{collage_filename}'...")
# Determine optimal rows and columns for the collage grid
# For 20 images, 4 rows x 5 columns or 5 rows x 4 columns are good options
collage_rows = 4
collage_cols = 5
# Ensure the number of images matches the grid size for simplicity, or adjust logic
if collage_rows * collage_cols < num_paths:
    print(f"Warning: Collage grid {collage_rows}x{collage_cols} is too small for {num_paths} images. Adjusting to fit.")
    # A simple adjustment, might not be perfectly square
    collage_cols = int(np.ceil(np.sqrt(num_paths)))
    collage_rows = int(np.ceil(num_paths / collage_cols))

# Get list of all generated image files
image_files_to_collage = [
    os.path.join(output_directory, f"path_{i + 1:02d}.png")
    for i in range(num_paths)
]

create_collage(image_files_to_collage, collage_filename, collage_rows, collage_cols)
print("Process completed!")