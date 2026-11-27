from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent
BLUE = "#56B4E9"
GREEN = "#009E73"
ORANGE = "#E69F00"
VERMILION = "#D55E00"


@st.cache_data
def load_csv(filename):
    return pd.read_csv(DATA_DIR / filename)


st.set_page_config(page_title="Online Retail Analytics Dashboard", layout="wide")
st.title("Online Retail Analytics Dashboard")
st.write("Explore book recommendations from Goodbooks and grocery buying patterns from Instacart.")

books = load_csv("books_export.csv")
book_summary = load_csv("summary_books.csv").iloc[0]
basket_summary = load_csv("basket_summary.csv").iloc[0]

metrics = {
    "Books": book_summary["total_books"],
    "Book ratings": book_summary["total_ratings"],
    "Readers": book_summary["total_users"],
    "Grocery baskets": basket_summary["total_baskets"],
    "Distinct products": basket_summary["distinct_items"],
}
for column, (label, value) in zip(st.columns(len(metrics)), metrics.items()):
    column.metric(label, f"{int(value):,}")

book_tab, grocery_tab = st.tabs(["Books and recommendations", "Grocery baskets"])

with book_tab:
    st.write("Reader ratings support collaborative filtering. Book tags support recommendations based on similar content.")
    tags = load_csv("top_tags.csv")
    rating_chart, reader_chart, tag_chart = st.columns(3)
    rating_chart.plotly_chart(px.bar(
        load_csv("rating_distribution.csv"), x="rating", y="count",
        title="Distribution of ratings", labels={"rating": "Rating", "count": "Ratings"},
        color_discrete_sequence=[ORANGE],
    ))
    reader_chart.plotly_chart(px.histogram(
        load_csv("ratings_per_user.csv"), x="num_ratings", nbins=40,
        title="Ratings per reader", labels={"num_ratings": "Ratings per reader"},
        color_discrete_sequence=[BLUE],
    ))
    tag_chart.plotly_chart(px.bar(
        tags.sort_values("count"), x="count", y="tag_name",
        title="Most frequent genre tags", labels={"count": "Uses", "tag_name": "Tag"},
        color_discrete_sequence=[GREEN],
    ))

    st.subheader("Top books")
    genre_col, author_col, count_col = st.columns(3)
    genre = genre_col.selectbox("Genre", ["All", *tags["tag_name"].dropna().tolist()])
    author = author_col.text_input("Author contains").strip()
    book_limit = count_col.selectbox("Books to show", [5, 10, 20], index=1)

    filtered = books
    if genre != "All":
        filtered = filtered[filtered["genres"].str.contains(genre, case=False, na=False, regex=False)]
    if author:
        filtered = filtered[filtered["authors"].str.contains(author, case=False, na=False, regex=False)]
    top_books = filtered.nlargest(book_limit, "ratings_count")
    book_labels = {
        "title": "Book Title", "authors": "Authors", "original_publication_year": "Publication Year",
        "average_rating": "Average Rating", "ratings_count": "Number of Ratings",
    }
    if top_books.empty:
        st.info("No books match these filters.")
    else:
        figure = px.bar(
            top_books.sort_values("ratings_count"), x="ratings_count", y="title",
            hover_data=["average_rating"], labels=book_labels,
            color_discrete_sequence=[ORANGE],
        )
        st.plotly_chart(figure)
        st.dataframe(top_books[list(book_labels)].rename(columns=book_labels), hide_index=True)

    st.subheader("Recommendations by book tags")
    titles = sorted(books["title"].dropna().unique())
    default_title = "The Hunger Games (The Hunger Games, #1)"
    title = st.selectbox("Choose a book", titles, index=titles.index(default_title) if default_title in titles else 0)
    book_id = books.loc[books["title"] == title, "book_id"].iloc[0]
    content = load_csv("content_recs_all.csv")
    matches = content.loc[content["seed_book_id"] == book_id].nsmallest(10, "rank")
    content_labels = {
        "rec_title": "Recommended Book", "rec_authors": "Authors", "similarity_score": "Similarity Score",
    }
    st.dataframe(matches[list(content_labels)].rename(columns=content_labels), hide_index=True)

    st.subheader("Collaborative recommendations")
    st.caption("Recommendations were calculated in advance for 30 sample readers.")
    reader = st.selectbox("Reader ID", load_csv("sample_users.csv")["user_id"].tolist())
    recommendation_labels = {"title": "Recommended Book", "authors": "Authors", "predicted_rating": "Predicted Rating"}
    for column, heading, filename in zip(
        st.columns(2),
        ("Recommendations by similar readers", "Recommendations by similar books"),
        ("useruser_recs.csv", "itemitem_recs.csv"),
    ):
        results = load_csv(filename)
        recommendations = results.loc[results["user_id"] == reader].sort_values("rank")
        column.subheader(heading)
        column.dataframe(recommendations[list(recommendation_labels)].rename(columns=recommendation_labels), hide_index=True)
    st.caption("Goodreads ratings represent reader preferences. They do not record bookshop purchases.")

with grocery_tab:
    st.write("Baskets with several items let Apriori and ECLAT identify products that customers often buy together.")
    size_chart, products_chart = st.columns(2)
    size_chart.plotly_chart(px.bar(
        load_csv("basket_size_distribution.csv"), x="basket_size", y="count",
        title="Basket size distribution", labels={"basket_size": "Items per basket", "count": "Baskets"},
        color_discrete_sequence=[ORANGE],
    ))
    products = load_csv("top_products.csv").nlargest(20, "basket_count").sort_values("basket_count")
    products_chart.plotly_chart(px.bar(
        products, x="basket_count", y="name", title="Most frequent products",
        labels={"basket_count": "Baskets", "name": "Product"}, color_discrete_sequence=[BLUE],
    ))

    st.subheader("Association rules")
    algorithm_col, lift_col, rows_col = st.columns(3)
    algorithm = algorithm_col.radio("Algorithm", ["Apriori", "ECLAT"], horizontal=True)
    minimum_lift = lift_col.slider("Minimum lift", 1.0, 6.0, 1.0, step=0.5)
    row_limit = rows_col.selectbox("Rules to show", [10, 20, 50], index=1)
    rules = load_csv(f"rules_{algorithm.lower()}.csv")
    shown = rules.loc[rules["lift"] >= minimum_lift].nlargest(row_limit, "lift")
    rule_labels = {
        "antecedent_names": "If Basket Contains", "consequent_names": "Also Bought",
        "support": "Share of All Baskets", "confidence": "Likelihood of Also Buying", "lift": "Lift",
    }
    if shown.empty:
        st.info("No rules meet this minimum lift.")
    else:
        figure = px.scatter(
            shown, x="confidence", y="lift", size="support",
            hover_data=["antecedent_names", "consequent_names"],
            title=f"Confidence and lift for {algorithm} rules",
            labels=rule_labels, color_discrete_sequence=[VERMILION],
        )
        figure.add_hline(y=1, line_dash="dash", line_color="grey")
        st.plotly_chart(figure)
        st.dataframe(shown[list(rule_labels)].rename(columns=rule_labels), hide_index=True)
    st.caption("The rules describe past purchases. A separate test would show whether a recommendation increases sales.")
