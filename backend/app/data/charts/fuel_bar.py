import plotly.graph_objects as go
from .generator_data import FUEL_CAPACITY


def create_bullet_chart(gen_data):
    fig = go.Figure()
    sorted_generators = reversed(sorted(gen_data, key=lambda gen: (
        gen.fuelInput / 100) * gen.capacity))

    for gen in sorted_generators:
        # Add the range bar (background)
        fig.add_trace(go.Bar(
            y=[gen.capacity],
            x=[gen.name],
            orientation='v',
            marker=dict(color='rgb(211,211,211)'),
            width=0.5,
        ))

        # Add the measure bar (fuel level)
        fig.add_trace(go.Bar(
            y=[gen.estimatedFill],
            x=[gen.name],
            orientation='v',
            marker=dict(color=gen.fuel_color),
            width=0.5,
        ))

    fig.update_layout(
        barmode='overlay',
        yaxis=dict(
            tickvals=[0, FUEL_CAPACITY * 0.25, FUEL_CAPACITY *
                      0.5, FUEL_CAPACITY * 0.75, FUEL_CAPACITY],
            ticktext=['0%', '25%', '50%', '75%', '100%']
        ),
        margin=dict(t=25, b=25, l=36, r=36),  # Match PDF margins
        paper_bgcolor='#f8f9fa',
        plot_bgcolor='#ffffff',
        showlegend=False,
        bargap=0.2,
        autosize=True,
        width=544,  # Matches the portrait letter page width
        height=400,  # Adjust height as needed
    )

    # Add target line and annotation
    fig.add_shape(
        type='line',
        y0=(FUEL_CAPACITY * 0.8),
        y1=(FUEL_CAPACITY * 0.8),
        x0=0,
        x1=1,
        xref='paper',
        line=dict(color='rgba(255, 0, 0, 0.5)', width=2),
    )

    fig.add_annotation(
        y=(FUEL_CAPACITY * 0.8),
        x=1,  # Moved annotation closer to chart
        xref='paper',
        text='(80%)',
        showarrow=True,
        arrowhead=2,
        ax=20,
        ay=25,
        font=dict(
            family='Arial, sans-serif',
            size=12,  # Reduced font size
            color='rgba(255, 0, 0, 1)',
        ),
        xshift=-5
    )

    return fig
