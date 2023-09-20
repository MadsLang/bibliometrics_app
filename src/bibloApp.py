import streamlit as st
import pandas as pd
import io
from get_data import getOAdata

st.title('Easy access to bibliometric data')

st.markdown(
    '<p style=font-style:italic;>Made by <a href=https://github.com/MadsLang>Mads Lang Sørensen</a></p>', 
    unsafe_allow_html=True
)

st.divider()

st.markdown(
    """
    Upload an Excel-sheet with a number of DOIs in the first column, 
    and this app will add bibliometric data for each of the publications. 
    You can download data from OpenAlexAPI or you can use the query to download data from Scopus. 
    """
)

uploaded_file = st.file_uploader("Choose an Excel file")
if uploaded_file is not None:
    init_df = pd.read_excel(uploaded_file)
    init_df = init_df.rename(columns={init_df.columns[0]: 'DOI' })

    scopus_query = ' OR '.join(['DOI(' + doi + ')' for doi in init_df['DOI']])

    st.divider()
    st.markdown("Here is a Scopus query to find your results:")
    st.code(scopus_query)
    st.markdown('If you have a Scopus subcription, you can use this query to find data at https://scopus.com')
    st.markdown('<br> <br>', unsafe_allow_html=True)
    st.divider()

    with st.spinner('Getting data from OpenAlex...'):
        st.session_state.df = getOAdata(init_df)
    st.success('Got data!')

    columns = st.multiselect(
        'What columns do you want in your dataset?',
        st.session_state.df.columns,
        [
            'DOI','title','publication_year','language','countries_distinct_count',
            'institutions_distinct_count','cited_by_count','referenced_works_count',
            'abstract','authors_display_names','authors_display_orcid','number_of_authors',
            'authors_unique_number_of_affiliations','authors_unique_affiliations',
        ]
    )
    st.markdown('<br> <br>', unsafe_allow_html=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state.df = st.session_state.df[columns]
        st.session_state.df.to_excel(writer, sheet_name='data', index=False)
        writer.close()

        if 'btn_clicked' not in st.session_state:
            st.session_state.btn_clicked = False

        def click_button():
            st.session_state.btn_clicked = True

        st.download_button(
            label='Download OpenAlex Data for your DOIs',
            data=buffer,
            file_name='openalex_data.xlsx',
            mime='application/vnd.ms-excel',
            use_container_width=True,
            on_click=click_button
        )

        if st.session_state.btn_clicked:
            st.balloons()