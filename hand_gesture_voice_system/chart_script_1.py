"""
Project Timeline Visualization Script
Generates a Gantt chart for development milestones
"""

import plotly.express as px
import pandas as pd
from datetime import datetime

# Project timeline data
timeline_data = [
    {
        "Phase": "Research & Setup",
        "Start": "2023-11-01",
        "End": "2023-11-07",
        "Tasks": "Literature review, Environment setup",
        "Completion": 100,
        "Color": "#1FB8CD"
    },
    {
        "Phase": "Core Development",
        "Start": "2023-11-08",
        "End": "2023-11-21",
        "Tasks": "Gesture recognition, Voice processing",
        "Completion": 85,
        "Color": "#DB4545"
    },
    {
        "Phase": "System Integration",
        "Start": "2023-11-22",
        "End": "2023-11-28",
        "Tasks": "Controller implementation, Module linking",
        "Completion": 70,
        "Color": "#2E8B57"
    },
    {
        "Phase": "Testing & Debugging",
        "Start": "2023-11-29",
        "End": "2023-12-05",
        "Tasks": "Unit tests, Integration tests",
        "Completion": 50,
        "Color": "#5D878F"
    },
    {
        "Phase": "Documentation",
        "Start": "2023-12-06",
        "End": "2023-12-12",
        "Tasks": "User manual, Technical docs",
        "Completion": 30,
        "Color": "#D2BA4C"
    }
]

def generate_gantt_chart():
    """Create and save interactive Gantt chart"""
    # Prepare DataFrame
    df = pd.DataFrame(timeline_data)
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])
    
    # Calculate duration in days
    df['Duration'] = (df['End'] - df['Start']).dt.days
    
    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Phase",
        color="Color",
        color_discrete_map="identity",
        hover_name="Phase",
        hover_data={
            "Tasks": True,
            "Completion": ":.0f%",
            "Duration": True,
            "Color": False
        },
        title="Hand Gesture Voice System Development Timeline"
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title={
            'text': "<b>Project Development Timeline</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis=dict(
            title="Timeline",
            tickformat="%b %d",
            rangeslider_visible=True
        ),
        yaxis=dict(
            title="Development Phase",
            autorange="reversed"
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        showlegend=False
    )
    
    # Add completion percentage annotations
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row['Start'] + (row['End'] - row['Start'])/2,
            y=row['Phase'],
            text=f"{row['Completion']}%",
            showarrow=False,
            font=dict(color="white", size=12)
        )
    
    # Save outputs
    fig.write_image("docs/assets/project_timeline.png", width=1000, height=600)
    fig.write_html("docs/assets/project_timeline.html")
    print("Gantt chart saved to docs/assets/")

def generate_team_allocation():
    """Create resource allocation pie chart"""
    team_data = {
        "Role": ["Backend", "Frontend", "ML", "Testing", "Documentation"],
        "Hours": [120, 80, 150, 90, 60],
        "Color": ["#1FB8CD", "#DB4545", "#2E8B57", "#5D878F", "#D2BA4C"]
    }
    
    fig = px.pie(
        team_data,
        values="Hours",
        names="Role",
        color="Role",
        color_discrete_map=dict(zip(team_data["Role"], team_data["Color"])),
        title="Team Allocation (Person-Hours)",
        hole=0.3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial"),
        showlegend=False
    )
    
    fig.write_image("docs/assets/team_allocation.png", width=600, height=500)
    print("Team allocation chart saved to docs/assets/")

if __name__ == "__main__":
    generate_gantt_chart()
    generate_team_allocation()