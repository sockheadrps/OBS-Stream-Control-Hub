from ..data.charts.generator_data import get_generator_data, calculate_fuel_metrics
from ..data.charts.gauge_chart import create_gauge_chart
from ..data.charts.fuel_bar import create_bullet_chart
from ..config import image_dir
# Get generator data
gen_data = get_generator_data()

# Calculate metrics
metrics = calculate_fuel_metrics(gen_data)

# Create charts
gauge_chart = create_gauge_chart(metrics['total_current_fuel'], metrics['total_capacity'])
bullet_chart = create_bullet_chart(gen_data)


# Save charts as images
gauge_chart.write_image(str(image_dir / "gauge_chart.png"))
bullet_chart.write_image(str(image_dir / "fuel_bar.png"))