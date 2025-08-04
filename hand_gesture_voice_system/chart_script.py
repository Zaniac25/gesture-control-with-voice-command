"""
System Architecture Visualization Script
Generates an architecture diagram for the Hand Gesture Voice System
"""

import plotly.graph_objects as go
import plotly.express as px
import json
import os

# Create output directory if not exists
os.makedirs('docs/assets', exist_ok=True)

# System architecture data
architecture = {
    "components": [
        {
            "layer": "Input",
            "items": ["Camera Feed", "Microphone Input"],
            "color": "#1FB8CD",
            "position": 0
        },
        {
            "layer": "Processing",
            "items": [
                "MediaPipe Hand Tracking",
                "OpenCV Image Processing",
                "SpeechRecognition"
            ],
            "color": "#DB4545",
            "position": 1
        },
        {
            "layer": "Recognition",
            "items": [
                "Gesture Classifier (RandomForest)",
                "Voice Command Parser"
            ],
            "color": "#2E8B57",
            "position": 2
        },
        {
            "layer": "Control",
            "items": [
                "System Controller",
                "Action Dispatcher"
            ],
            "color": "#5D878F",
            "position": 3
        },
        {
            "layer": "Output",
            "items": [
                "Volume Control",
                "Browser Control",
                "Screenshot",
                "Window Management",
                "Application Launch"
            ],
            "color": "#D2BA4C",
            "position": 4
        }
    ]
}

def generate_architecture_diagram():
    """Create and save system architecture diagram"""
    # Prepare data for plotting
    x_pos = []
    y_pos = []
    text_labels = []
    colors = []
    
    for component in architecture["components"]:
        layer_pos = component["position"]
        num_items = len(component["items"])
        vertical_offset = (num_items - 1) / 2  # Center items vertically
        
        for i, item in enumerate(component["items"]):
            x_pos.append(layer_pos)
            y_pos.append(vertical_offset - i)  # Distribute items vertically
            text_labels.append(item[:18] + '...' if len(item) > 18 else item)
            colors.append(component["color"])
    
    # Create figure
    fig = go.Figure()
    
    # Add components as square markers
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='markers+text',
        marker=dict(
            size=40,
            color=colors,
            symbol='square',
            line=dict(width=2, color='white')
        ),
        text=text_labels,
        textposition='middle center',
        textfont=dict(size=10, color='white'),
        hoverinfo='text',
        hovertext=[f"<b>{label}</b>" for label in text_labels]
    ))
    
    # Add flow arrows between layers
    for i in range(len(architecture["components"]) - 1):
        fig.add_annotation(
            x=i + 0.5,
            y=0,
            ax=i + 0.2,
            ay=0,
            axref='x',
            ayref='y',
            xref='x',
            yref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor='#666666'
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "<b>Hand Gesture & Voice System Architecture</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[c["position"] for c in architecture["components"]],
            ticktext=[c["layer"] for c in architecture["components"]],
            showgrid=False,
            zeroline=False,
            title_font=dict(size=14)
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-3, 3]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        margin=dict(l=20, r=20, t=100, b=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Save files
    fig.write_image("docs/assets/system_architecture.png", width=1200, height=600, scale=2)
    fig.write_html("docs/assets/system_architecture.html")
    
    print("Architecture diagram saved to docs/assets/")

def generate_performance_chart():
    """Create sample performance comparison chart"""
    performance_data = {
        "Resolution": ["1080p", "720p", "480p"],
        "FPS": [28, 42, 55],
        "CPU Usage": [65, 45, 30],
        "Memory (MB)": [450, 380, 300]
    }
    
    fig = px.bar(
        performance_data,
        x="Resolution",
        y=["FPS", "CPU Usage"],
        barmode='group',
        title="System Performance by Resolution",
        labels={"value": "Percentage/FPS", "variable": "Metric"},
        color_discrete_sequence=['#1FB8CD', '#DB4545']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.write_image("docs/assets/performance_chart.png", width=800, height=500)
    print("Performance chart saved to docs/assets/")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_performance_chart()