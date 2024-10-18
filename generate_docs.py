import os
import nbconvert
import glob

def convert_notebook_to_md(notebook_path, output_dir):
    exporter = nbconvert.MarkdownExporter()
    output, _ = exporter.from_filename(notebook_path)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
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
    with open('mkdocs.yml', 'r') as file:
        lines = file.readlines()
    
    # Find the nav section and update it
    nav_start = -1
    for i, line in enumerate(lines):
        if line.strip() == 'nav:':
            nav_start = i
            break
    
    if nav_start != -1:
        lines = lines[:nav_start+1]  # Keep everything before nav
    else:
        lines.append('nav:\n')
    
    # Add the new nav items
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                lines.append(f'  - {key}:\n')
                for subitem in value:
                    lines.append(f'    - {subitem}\n')
        else:
            lines.append(f'  - {item}\n')
    
    # Write the updated mkdocs.yml
    with open('mkdocs.yml', 'w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    nav = generate_mkdocs_nav()
    update_mkdocs_yml(nav)
    print("Documentation structure generated and mkdocs.yml updated.")