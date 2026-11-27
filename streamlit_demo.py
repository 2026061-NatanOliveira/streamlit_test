import pandas as pd
import streamlit as st

st.title("Dashboard Test")

ratings = pd.read_csv("rating_distribution.csv")

st.subheader("Book Ratings")
st.bar_chart(ratings, x="rating", y="count")