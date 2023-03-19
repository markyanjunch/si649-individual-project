import streamlit as st

import pandas as pd
import altair as alt
from vega_datasets import data


st.set_page_config(layout="wide")

state_map = data.us_10m.url
disability = pd.read_csv('dataset/disability.csv')

state_selector=alt.selection_single(on='mouseover', clear='mouseout', fields=['state'])
opacityCondition=alt.condition(state_selector, alt.value(1), alt.value(0.2))
strokeCondition=alt.condition(state_selector, alt.value('black'), alt.value('white'))

us_map = alt.Chart(alt.topo_feature(state_map, 'states')).mark_geoshape(
).encode(
    color=alt.Color(
        'Any Disability:Q',
        scale=alt.Scale(scheme='blues'),
        legend=alt.Legend(orient='top', title='Statewide Disability Estimate (%)', format='.1f')
    ),
    tooltip=[
        alt.Tooltip('state:N', title='State'), 
        alt.Tooltip('Any Disability:Q', title='Any Disability (%)', format='.1f'),
        alt.Tooltip('Cognitive Disability:Q', title='Cognitive Disability (%)', format='.1f'),
        alt.Tooltip('Hearing Disability:Q', title='Hearing Disability (%)', format='.1f'),
        alt.Tooltip('Mobility Disability:Q', title='Mobility Disability (%)', format='.1f'),
        alt.Tooltip('Vision Disability:Q', title='Vision Disability (%)', format='.1f'),
        alt.Tooltip('Self-care Disability:Q', title='Self-care Disability (%)', format='.1f'),
        alt.Tooltip('Independent Living Disability:Q', title='Independent Living Disability (%)', format='.1f'),
        alt.Tooltip('18-44:Q', title='Age 18-44 (%)', format='.1f'),
        alt.Tooltip('45-64:Q', title='Age 45-64 (%)', format='.1f'),
        alt.Tooltip('65+:Q', title='Age 65+ (%)', format='.1f'),
        alt.Tooltip('Male:Q', title='Male (%)', format='.1f'),
        alt.Tooltip('Female:Q', title='Female (%)', format='.1f')
    ],
    opacity=opacityCondition,
    stroke=strokeCondition
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(
        disability, 
        key='id', 
        fields=[
            'state',
            'id',
            'Any Disability',
            'Cognitive Disability', 
            'Hearing Disability', 
            'Mobility Disability', 
            'Vision Disability',
            'Self-care Disability',
            'Independent Living Disability',
            '18-44',
            '45-64',
            '65+',
            'Male',
            'Female'
        ]
    )
).project(
    'albersUsa'
).properties(
    title='2020 Disability Status and Types among Adults 18 Years of Age or Older',
    width=900
).add_selection(
    state_selector
)

bar_age = alt.Chart(disability).transform_fold(
    ['18-44', '45-64', '65+'],
    as_=['age', 'value']
).transform_calculate(
    percentage=alt.datum.value/100,
).mark_bar().encode(
    y='age:O',
    x=alt.X(
        'percentage:Q', 
        scale=alt.Scale(domain=(0, 1)), 
        axis=alt.Axis(ticks=False, title=None, format='.0%')),
    color=alt.Color('age:O', scale=alt.Scale(scheme='teals'))
).properties(width=300)

text_age = bar_age.mark_text(
    align='left',
    dx=7
).encode(
    text=alt.Text('percentage:Q', format='.1%'),
    color=alt.ColorValue('black')
)

chart_age = (bar_age+text_age).facet(
    facet=alt.Facet('state:O', title=None),
    columns=1
).properties(
    title='Percentage by Age with Any Disability'
).transform_filter(
    state_selector
)

bar_gender = alt.Chart(disability).transform_fold(
    ['Male', 'Female'],
    as_=['gender', 'value']
).transform_calculate(
    percentage=alt.datum.value/100,
).mark_bar().encode(
    y='gender:O',
    x=alt.X(
        'percentage:Q', 
        scale=alt.Scale(domain=(0, 1)), 
        axis=alt.Axis(ticks=False, title=None, format='.0%')),
    color=alt.Color('gender:O', scale=alt.Scale(scheme='brownbluegreen'))
).properties(
    height=60,
    width=300
)

text_gender = bar_gender.mark_text(
    align='left',
    dx=7
).encode(
    text=alt.Text('percentage:Q', format='.1%'),
    color=alt.ColorValue('black')
)

chart_gender = (bar_gender+text_gender).facet(
    facet=alt.Facet('state:O', title=None),
    columns=1
).properties(
    title='Percentage by Gender with Any Disability'
).transform_filter(
    state_selector
)

bottom = (chart_age|chart_gender).resolve_scale(color='independent')

vis = us_map&bottom

st.altair_chart(vis, theme=None, use_container_width=True)