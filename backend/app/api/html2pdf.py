import pdfkit
from ..config import image_dir

def convert_html_to_pdf(input_html, output_pdf):
    print(image_dir / input_html)
    print(image_dir / output_pdf)
    pdfkit.from_file(str(image_dir / input_html), str(image_dir / output_pdf))

# Example usage
convert_html_to_pdf("output.html", "output.pdf")