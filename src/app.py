import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load data from CSV file
df = pd.read_csv('student_data.csv')

# Get unique subjects from the data
subjects = df['Subject'].unique()

# Make sure all subjects are present in the DataFrame
missing_subjects = set(['Math', 'Science', 'English', 'History', 'Hindi', 'Marathi']) - set(subjects)
for subject in missing_subjects:
    df = df.append(pd.DataFrame({'StudentID': [], 'Grade': [], 'Subject': [subject]*len(df['Grade'].unique()), 'Marks': []}))

# Create Dash app
app = dash.Dash(__name__)

# Define color palette
colors = ['#00876c', '#f44336', '#03a9f4']

# Define layout
app.layout = html.Div([
    html.Div([
        html.H1("Student Performance Dashboard", className='header'),
        html.Div([
            dcc.Dropdown(
                id='student-dropdown',
                options=[{'label': f'Student {i}', 'value': i} for i in df['StudentID'].unique()],
                value=df['StudentID'].unique()[0],
                clearable=False,
                placeholder="Select a student",
                className='dropdown'
            ),
            dcc.Checklist(
                id='comparison-checklist',
                options=[
                    {'label': 'Top Scorer', 'value': 'top'},
                    {'label': 'Bottom Scorer', 'value': 'bottom'}
                ],
                value=[],
                inline=True,
                className='checklist'
            ),
        ], className='controls'),
        html.Div([
            html.Div([
                dcc.Graph(id='performance-graph', className='graph'),
            ], className='graph-container'),
            html.Div([
                dcc.Graph(id='performance-shift-graph', className='graph'),
            ], className='graph-container'),
        ], className='graphs'),
        html.Div([
            dcc.Graph(id='subject-performance-graph', className='full-width-graph')
        ], className='bottom-graph-container')
    ], className='container')
], className='main-container')

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
        name=f'Student {selected_student}',
        line=dict(color=colors[0], width=4, shape='spline', smoothing=0.3)
    ))

    # Comparisons
    if 'top' in comparison_options:
        topper_marks = df.groupby(['Subject'])['Marks'].max().reset_index()
        topper_values = topper_marks['Marks']
        fig1.add_trace(go.Scatterpolar(
            r=topper_values,
            theta=categories,
            fill='toself',
            name='Top Scorer',
            line=dict(color=colors[1], width=4, shape='spline', smoothing=0.3)
        ))

    if 'bottom' in comparison_options:
        bottom_marks = df.groupby(['Subject'])['Marks'].min().reset_index()
        bottom_values = bottom_marks['Marks']
        fig1.add_trace(go.Scatterpolar(
            r=bottom_values,
            theta=categories,
            fill='toself',
            name='Bottom Scorer',
            line=dict(color=colors[2], width=4, shape='spline', smoothing=0.3)
        ))

    fig1.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 110],
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],
                tickfont=dict(family='Roboto, sans-serif'),
            ),
            angularaxis=dict(
                tickfont=dict(family='Roboto, sans-serif'),
            )
        ),
        legend=dict(x=0.5, y=1, font=dict(family='Roboto, sans-serif')),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Roboto, sans-serif', color='#333333')
    )

    # Performance shift graph
    student_performance = df[df['StudentID'] == selected_student].groupby('Grade')['Marks'].mean().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=student_performance['Grade'], y=student_performance['Marks'], mode='lines+markers', name=f'Student {selected_student}', line=dict(color=colors[0], shape='spline', smoothing=0.7)))
    fig2.update_layout(title='Year-on-Year Performance Shift', xaxis_title='Grade', yaxis_title='Average Marks', margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font=dict(family='Roboto, sans-serif', color='#333333'))

    # Subject performance graph
    student_subject_performance = df[df['StudentID'] == selected_student].pivot(index='Grade', columns='Subject', values='Marks').reset_index()
    fig3 = go.Figure()
    for i, subject in enumerate(subjects):
        color = colors[i % len(colors)]  # Cycling through available colors
        fig3.add_trace(go.Scatter(x=student_subject_performance['Grade'], y=student_subject_performance[subject], mode='lines+markers', name=subject, line=dict(color=color, shape='spline', smoothing=0.7)))
    fig3.update_layout(title=f'Subject Performance for Student {selected_student}', xaxis_title='Grade', yaxis_title='Marks', margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', font=dict(family='Roboto, sans-serif', color='#333333'))

    return fig1, fig2, fig3

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
