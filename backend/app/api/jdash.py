from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from ..config import image_dir

def generate_html(data, template_file, output_file):
    # Create output directory if it doesn't exist
    output_path = image_dir / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use templates directory relative to current file
    template_dir = Path(__file__).parent.parent / "data/templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    html_content = template.render(data=data)
    
    with open(output_path, "w") as f:
        f.write(html_content)

# Example usage
data = {
    "title": "Generator Report", 
    "headers": ["Name", "Fuel Input (%)", "Estimated Current Fuel (gal)", "Fuel Delta"],
    "rows": [
        ["Generator A", 50, 5000, 10000 - 5000],
        ["Generator B", 20, 9600, 10000 - 9600],
    ]
}
generate_html(data, "template.html", "output.html")
