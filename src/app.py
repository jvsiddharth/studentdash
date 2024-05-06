import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load data from CSV file
df = pd.read_csv('student_data.csv')

# Create Dash app
app = dash.Dash(__name__)

# Get unique subjects, grades, and students from the data
subjects = df['Subject'].unique()
grades = df['Grade'].unique()
students = df['StudentID'].unique()

# Define layout
app.layout = html.Div([
    html.H1("Student Performance Comparison"),
    html.Div([
        dcc.Dropdown(
            id='student-dropdown',
            options=[{'label': f'Student {i}', 'value': i} for i in students],
            value=students[0],
            clearable=False,
            placeholder="Select a student"
        ),
        dcc.Checklist(
            id='comparison-checklist',
            options=[
                {'label': 'Top Scorer', 'value': 'top'},
                {'label': 'Bottom Scorer', 'value': 'bottom'}
            ],
            value=[],
            inline=True,
            style={'float': 'center', 'margin-right': '30px'}
        ),
    ], style={'width': '100%', 'display': 'inline-block'}),
    dcc.Graph(id='performance-graph'),
    dcc.Graph(id='performance-shift-graph'),
    dcc.Graph(id='subject-performance-graph')
])

# Define callback to update graphs
@app.callback(
    [Output('performance-graph', 'figure'),
     Output('performance-shift-graph', 'figure'),
     Output('subject-performance-graph', 'figure')],
    [Input('student-dropdown', 'value'),
     Input('comparison-checklist', 'value')]
)
def update_graph(selected_student, comparison_options):
    if selected_student is None:
        return {}, {}, {}

    # Overall performance across subjects
    student_marks = df[df['StudentID'] == selected_student].groupby('Subject')['Marks'].mean().reset_index()
    categories = student_marks['Subject']
    student_values = student_marks['Marks']

    fig1 = go.Figure()

    fig1.add_trace(go.Scatterpolar(
        r=student_values,
        theta=categories,
        fill='toself',
        name=f'Student {selected_student}'
    ))

    # Comparisons
    if 'top' in comparison_options:
        topper_marks = df.groupby(['Subject'])['Marks'].max().reset_index()
        topper_values = topper_marks['Marks']
        fig1.add_trace(go.Scatterpolar(
            r=topper_values,
            theta=categories,
            fill='toself',
            name='Top Scorer'
        ))

    if 'bottom' in comparison_options:
        bottom_marks = df.groupby(['Subject'])['Marks'].min().reset_index()
        bottom_values = bottom_marks['Marks']
        fig1.add_trace(go.Scatterpolar(
            r=bottom_values,
            theta=categories,
            fill='toself',
            name='Bottom Scorer'
        ))

    fig1.update_layout(
        title='Overall Performance Comparison',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True
    )

    # Performance shift graph
    student_performance = df[df['StudentID'] == selected_student].groupby('Grade')['Marks'].mean().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=student_performance['Grade'], y=student_performance['Marks'], mode='lines+markers', name=f'Student {selected_student}'))
    fig2.update_layout(title='Year-on-Year Performance Shift', xaxis_title='Grade', yaxis_title='Average Marks')

    # Subject performance graph
    student_subject_performance = df[df['StudentID'] == selected_student].pivot(index='Grade', columns='Subject', values='Marks').reset_index()
    fig3 = go.Figure()
    for subject in subjects:
        fig3.add_trace(go.Scatter(x=student_subject_performance['Grade'], y=student_subject_performance[subject], mode='lines+markers', name=subject))
    fig3.update_layout(title=f'Subject Performance for Student {selected_student}', xaxis_title='Grade', yaxis_title='Marks')

    return fig1, fig2, fig3

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
