import os
import nbconvert
import glob
import shutil

def copy_images(notebook_dir, output_dir):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
    for ext in image_extensions:
        for img_file in glob.glob(os.path.join(notebook_dir, f'*{ext}')):
            dest_path = os.path.join(output_dir, os.path.basename(img_file))
            shutil.copy2(img_file, dest_path)
            print(f"Copied image: {img_file} to {dest_path}")

def update_image_paths(md_content, notebook_dir, output_dir):
    lines = md_content.split('\n')
    for i, line in enumerate(lines):
        if '![' in line and '](' in line:
            start = line.index('](') + 2
            end = line.index(')', start)
            img_path = line[start:end]
            if not img_path.startswith(('http://', 'https://', '/')):
                new_path = os.path.basename(img_path)
                lines[i] = line[:start] + new_path + line[end:]
    return '\n'.join(lines)



def convert_notebook_to_md(notebook_path, output_dir):
    exporter = nbconvert.MarkdownExporter()
    output, _ = exporter.from_filename(notebook_path)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy images
    notebook_dir = os.path.dirname(notebook_path)
    copy_images(notebook_dir, output_dir)
    
    # Update image paths in the markdown content
    output = update_image_paths(output, notebook_dir, output_dir)
    
    # Write the markdown file
    md_filename = os.path.splitext(os.path.basename(notebook_path))[0] + '.md'
    md_path = os.path.join(output_dir, md_filename)
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(output)
    
    return md_path
    

def generate_mkdocs_nav():
    nav = []
    
    # Convert root notebooks
    root_notebooks = glob.glob('*.ipynb')
    for notebook in root_notebooks:
        md_path = convert_notebook_to_md(notebook, 'docs')
        nav.append(f"{os.path.splitext(notebook)[0]}: {os.path.relpath(md_path, 'docs')}")
    
    # Convert notebooks in lab folders
    lab_folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.startswith('lab')]
    for lab_folder in lab_folders:
        lab_nav = []
        notebooks = glob.glob(f'{lab_folder}/*.ipynb')
        for notebook in notebooks:
            md_path = convert_notebook_to_md(notebook, f'docs/{lab_folder}')
            lab_nav.append(f"{os.path.splitext(os.path.basename(notebook))[0]}: {os.path.relpath(md_path, 'docs')}")
        nav.append({lab_folder: lab_nav})
    
    return nav

def update_mkdocs_yml(nav):
    # Start with the basic configuration
    config = [
        "site_name: zt lab notebooks docs\n",
        "theme:\n",
        "  name: material\n",
        "plugins:\n",
        "  - search\n",
        "nav:\n"
    ]
    
    # Add the nav items
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                config.append(f"  - {key}:\n")
                for subitem in value:
                    config.append(f"    - {subitem}\n")
        else:
            config.append(f"  - {item}\n")
    
    # Write the updated mkdocs.yml
    with open('mkdocs.yml', 'w') as file:
        file.writelines(config)

if __name__ == "__main__":
    nav = generate_mkdocs_nav()
    update_mkdocs_yml(nav)
    print("Documentation structure generated and mkdocs.yml updated.")