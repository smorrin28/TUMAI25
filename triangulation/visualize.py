import json
import plotly.graph_objects as go

# Load data from JSON file
with open('result.json', 'r') as f:
    data = json.load(f)

special_point = data['result']
points = data['points']

# Combine all points (normal + special) into one list
all_points = points + [special_point]
special_point_idx = len(points)  # it's the last one

# Create figure
fig = go.Figure()

# Add all points
for idx, point in enumerate(all_points):
    fig.add_trace(go.Scattermapbox(
        lat=[point["latitude"]],
        lon=[point["longitude"]],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color='red' if idx == special_point_idx else 'blue'
        ),
        name=point["name"] + (" (Special)" if idx == special_point_idx else ""),
        text=f'{point["name"]}<br>Altitude: {point["altitude"]} m',
        hoverinfo='text'
    ))

# Add lines between all pairs of points
for i in range(len(all_points)):
    for j in range(i + 1, len(all_points)):
        fig.add_trace(go.Scattermapbox(
            lat=[all_points[i]["latitude"], all_points[j]["latitude"]],
            lon=[all_points[i]["longitude"], all_points[j]["longitude"]],
            mode='lines',
            line=dict(width=2, color='green'),
            showlegend=False
        ))

# Set layout
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        zoom=1.5,
        center=dict(
            lat=sum(p['latitude'] for p in all_points) / len(all_points),
            lon=sum(p['longitude'] for p in all_points) / len(all_points)
        )
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    title="Points Visualization with Special Highlight"
)

# Show the figure
fig.show()
