import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Load data from CSV file
df = pd.read_csv('student_data.csv')

# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Get unique subjects, grades, and students from the data
subjects = df['Subject'].unique()
grades = df['Grade'].unique()
students = df['StudentID'].unique()

# Define layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Student Performance Dashboard", className='my-4 text-center'),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='student-dropdown',
                options=[{'label': f'Student {i}', 'value': i} for i in students],
                value=students[0],
                clearable=False,
                searchable=True,
                placeholder="Select a student"
            ),
            width={'size': 10, 'offset': 1},
            className='mb-3'
        ),
        dbc.Col(
            dcc.Dropdown(
                id='grade-dropdown',
                options=[{'label': f'Grade {i}', 'value': i} for i in grades],
                value=grades[0],
                clearable=False,
                placeholder="Select a grade"
            ),
            width={'size': 10, 'offset': 1},
            className='mb-3'
        ),
        dbc.Col(
            dcc.Dropdown(
                id='subject-dropdown',
                options=[{'label': subject, 'value': subject} for subject in subjects],
                value=subjects[0],
                clearable=False,
                placeholder="Select a subject"
            ),
            width={'size': 10, 'offset': 1},
            className='mb-3'
        ),
        dbc.Col(
            dbc.Button(
                "Toggle Dark Mode",
                id="dark-mode-toggle",
                color="dark",
                outline=True,
                className="ml-2",
            ),
            width={'size': 10, 'offset': 1},
            className='mb-3'
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='performance-shift-graph', className='my-4'),
            width={'size': 5, 'offset': 1}
        ),
        dbc.Col(
            dcc.Graph(id='subject-performance-graph', className='my-4'),
            width={'size': 5, 'offset': 1}
        ),
        dbc.Col(
            dcc.Graph(id='comparison-graph', className='my-4'),
            width={'size': 10, 'offset': 1}
        ),
        dbc.Col(
            dcc.Graph(id='overall-comparison-graph', className='my-4'),
            width={'size': 10, 'offset': 1}
        ),
        dbc.Col(
            dcc.Graph(id='grade-comparison-graph', className='my-4'),
            width={'size': 10, 'offset': 1}
        )
    ])
], fluid=True)

# Define callback to toggle dark mode
@app.callback(
    Output('dark-mode-toggle', 'color'),
    [Input('dark-mode-toggle', 'n_clicks')]
)
def toggle_dark_mode(n):
    if n and n % 2 == 0:
        return "dark"
    else:
        return "light"

# Define callback to update graphs
@app.callback(
    [Output('performance-shift-graph', 'figure'),
     Output('subject-performance-graph', 'figure'),
     Output('comparison-graph', 'figure'),
     Output('overall-comparison-graph', 'figure'),
     Output('grade-comparison-graph', 'figure')],  # Added new Output
    [Input('student-dropdown', 'value'),
     Input('grade-dropdown', 'value'),
     Input('subject-dropdown', 'value')]
)

def update_graph(selected_student, selected_grade, selected_subject):
    if selected_student is None or selected_grade is None or selected_subject is None:
        return {}, {}, {}, {}, {}

    # Performance shift graph
    filtered_df = df[df['StudentID'] == selected_student]
    avg_marks_by_year = filtered_df.groupby('Grade')['Marks'].mean().reset_index()
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=avg_marks_by_year['Grade'], y=avg_marks_by_year['Marks'], mode='lines+markers', name=f'Student {selected_student}'))
    fig1.update_layout(title='Performance Shift by Year', xaxis_title='Grade', yaxis_title='Average Marks')

    # Subject performance graph
    filtered_df = df[(df['StudentID'] == selected_student) & (df['Grade'] == selected_grade)]
    fig2 = go.Figure()
    for subject in subjects:
        subject_data = filtered_df[filtered_df['Subject'] == subject]
        fig2.add_trace(go.Bar(x=[subject], y=subject_data['Marks'].values, name=subject))
    fig2.update_layout(title=f'Student {selected_student} Performance in Grade {selected_grade}', xaxis_title='Subject', yaxis_title='Marks')

    # Comparison graph for selected subject
    student_marks = filtered_df[filtered_df['Subject'] == selected_subject]['Marks'].values[0]
    class_avg_marks = df[(df['Grade'] == selected_grade) & (df['Subject'] == selected_subject)]['Marks'].mean()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=['Student', 'Class Average'], y=[student_marks, class_avg_marks], marker_color=['rgb(58,200,225)', 'rgb(100,145,230)']))
    fig3.update_layout(title=f'Comparison: Student {selected_student} vs. Class Average in {selected_subject} (Grade {selected_grade})', xaxis_title='', yaxis_title='Marks')

    # Overall comparison graph
    student_avg_marks = filtered_df['Marks'].mean()
    class_avg_marks = df[df['Grade'] == selected_grade]['Marks'].mean()
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=['Student', 'Class Average'], y=[student_avg_marks, class_avg_marks], mode='lines+markers', marker_color=['rgb(58,200,225)', 'rgb(100,145,230)']))
    fig4.update_layout(title=f'Overall Comparison: Student {selected_student} vs. Class Average (Grade {selected_grade})', xaxis_title='', yaxis_title='Average Marks')

    # Grade comparison graph
    filtered_df = df[df['StudentID'] == selected_student]
    fig5 = go.Figure()
    for grade in grades:
        grade_data = filtered_df[filtered_df['Grade'] == grade]
        subject_data = grade_data[grade_data['Subject'] == selected_subject]
        fig5.add_trace(go.Bar(x=[grade], y=subject_data['Marks'].values, name=f'Grade {grade}'))
    fig5.update_layout(title=f'Grade Comparison for {selected_subject} (Student {selected_student})', xaxis_title='Grade', yaxis_title='Marks')
    
    return fig5, fig3, fig2, fig4, fig1

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
