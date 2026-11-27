from dash import Dash, html, dcc, dash_table, callback, Output, Input
import pandas as pd
import plotly.express as px

# --- data (same CSV files the previous dashboard used) ---
books = pd.read_csv("books_export.csv")
rating_distribution = pd.read_csv("rating_distribution.csv")
ratings_per_user = pd.read_csv("ratings_per_user.csv")
top_tags = pd.read_csv("top_tags.csv")
summary_books = pd.read_csv("summary_books.csv")
content_recs_all = pd.read_csv("content_recs_all.csv")
useruser_recs = pd.read_csv("useruser_recs.csv")
itemitem_recs = pd.read_csv("itemitem_recs.csv")
sample_users = pd.read_csv("sample_users.csv")

basket_summary = pd.read_csv("basket_summary.csv")
basket_size_distribution = pd.read_csv("basket_size_distribution.csv")
top_products = pd.read_csv("top_products.csv")
rules_apriori = pd.read_csv("rules_apriori.csv")
rules_eclat = pd.read_csv("rules_eclat.csv")

# --- colours, same pattern as the class Dash notebook (Basic Dash.ipynb), light theme ---
colors = {
    "background": "#F4F7FA",
    "text": "#1B4965",
    "body": "#333333",
    "card": "#FFFFFF",
}
chart_colors = ["#E69F00", "#56B4E9", "#009E73", "#D55E00", "#CC79A7"]

table_style = dict(
    style_header={"backgroundColor": colors["text"], "color": "white", "fontWeight": "bold"},
    style_cell={"backgroundColor": colors["card"], "color": colors["body"], "textAlign": "left", "padding": "6px"},
    style_table={"border": f"1px solid {colors['text']}"},
    page_size=10,
)

# same external stylesheet shown in class (Dash_Ex.ipynb), gives the row/columns grid
app = Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
server = app.server


def stat_card(label, value):
    return html.Div(className="two columns", children=[
        html.Div(style={"backgroundColor": colors["card"], "padding": "15px", "borderRadius": "6px",
                         "textAlign": "center", "margin": "5px", "boxShadow": "0 1px 4px rgba(0,0,0,0.15)"},
                 children=[
            html.H3(value, style={"color": colors["text"], "margin": "0"}),
            html.P(label, style={"color": colors["body"], "margin": "0"}),
        ])
    ])


# --- static figures (built once, not inside a callback) ---
fig_rating_distribution = px.bar(
    rating_distribution, x="rating", y="count",
    title="Distribution of Ratings (1 to 5)", color_discrete_sequence=[chart_colors[0]],
)
fig_ratings_per_user = px.histogram(
    ratings_per_user, x="num_ratings", nbins=40,
    title="Number of Ratings per User", color_discrete_sequence=[chart_colors[1]],
)
fig_top_tags = px.bar(
    top_tags.sort_values("count"), x="count", y="tag_name", orientation="h",
    title="20 Most Frequent Genre Tags", color_discrete_sequence=[chart_colors[2]],
)
for fig in (fig_rating_distribution, fig_ratings_per_user, fig_top_tags):
    fig.update_layout(paper_bgcolor=colors["background"], plot_bgcolor=colors["card"], font_color=colors["body"])

fig_basket_size = px.bar(
    basket_size_distribution, x="basket_size", y="count",
    title="Basket Size Distribution", color_discrete_sequence=[chart_colors[0]],
)
top_products_sorted = top_products.sort_values("basket_count").tail(20)
fig_top_products = px.bar(
    top_products_sorted, x="basket_count", y="name", orientation="h",
    title="20 Most Frequent Products", color_discrete_sequence=[chart_colors[1]],
)
for fig in (fig_basket_size, fig_top_products):
    fig.update_layout(paper_bgcolor=colors["background"], plot_bgcolor=colors["card"], font_color=colors["body"])

rules_chart = rules_apriori.sort_values("lift", ascending=False).head(20)
fig_rules_scatter = px.scatter(
    rules_chart, x="confidence", y="lift", size="support",
    title="Confidence vs Lift (Apriori, top 20 by lift)", color_discrete_sequence=[chart_colors[3]],
)
fig_rules_scatter.add_hline(y=1, line_dash="dash", line_color="grey")
fig_rules_scatter.update_layout(paper_bgcolor=colors["background"], plot_bgcolor=colors["card"], font_color=colors["body"])

# --- controls, same dcc components shown in class (Basic Dash.ipynb / Dash_Ex.ipynb) ---
genre_dropdown = dcc.Dropdown(
    options=[{"label": "All", "value": "All"}] + [{"label": g, "value": g} for g in top_tags["tag_name"]],
    value="All", id="genre-dropdown",
)
author_text = dcc.Input(id="author-text", type="text", placeholder="Author contains...", value="", style={"width": "100%"})
topn_dropdown = dcc.Dropdown(options=[5, 10, 20], value=10, id="topn-dropdown")

book_dropdown = dcc.Dropdown(
    options=sorted(books["title"].unique()),
    value="The Hunger Games (The Hunger Games, #1)",
    id="book-dropdown",
)
user_dropdown = dcc.Dropdown(options=sample_users["user_id"].tolist(), value=int(sample_users["user_id"].iloc[0]), id="user-dropdown")

algo_radio = dcc.RadioItems(options=["Apriori", "ECLAT"], value="Apriori", id="algo-radio", inline=True)
minlift_slider = dcc.Slider(min=1, max=6, step=0.5, value=1, id="minlift-slider")
maxrows_dropdown = dcc.Dropdown(options=[10, 20, 50], value=20, id="maxrows-dropdown")

app.layout = html.Div(style={"backgroundColor": colors["background"], "padding": "20px"}, children=[

    html.H1("Online Retail Analytics Dashboard", style={"textAlign": "center", "color": colors["text"]}),
    html.P(
        "I built this dashboard for adults aged 18 to 35, the core online shopping demographic "
        "for an online retail business. It summarises two retail case studies: Goodbooks-10k book "
        "ratings and Instacart grocery baskets. These are two separate datasets, not the same business.",
        style={"textAlign": "center", "color": colors["body"]},
    ),
    html.Hr(),

    html.H2("Designed for Adults Aged 18 to 35", style={"color": colors["text"]}),
    html.P(
        "Dropdown menus let a visitor explore the data without reading any code, which matches how "
        "this age group is used to interacting with apps and websites. The charts stay simple and "
        "colour-blind safe, and the key numbers are shown first as cards, since this is how a "
        "younger adult scans a page.",
        style={"color": colors["body"]},
    ),
    html.Hr(),

    html.H2("Overview", style={"color": colors["text"]}),
    html.Div(className="row", children=[
        stat_card("Total Books", f"{summary_books['total_books'][0]:,}"),
        stat_card("Book Ratings", f"{summary_books['total_ratings'][0]:,}"),
        stat_card("Readers", f"{summary_books['total_users'][0]:,}"),
        stat_card("Instacart Baskets", f"{basket_summary['total_baskets'][0]:,}"),
        stat_card("Distinct Products", f"{basket_summary['distinct_items'][0]:,}"),
    ]),
    html.Hr(),

    html.H2("Books and Recommendations", style={"color": colors["text"]}),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[dcc.Graph(figure=fig_rating_distribution)]),
        html.Div(className="four columns", children=[dcc.Graph(figure=fig_ratings_per_user)]),
        html.Div(className="four columns", children=[dcc.Graph(figure=fig_top_tags)]),
    ]),

    html.H3("Top Books", style={"color": colors["text"]}),
    html.P("Filter by genre, author and how many books to show.", style={"color": colors["body"]}),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[html.Label("Genre:", style={"color": colors["body"]}), genre_dropdown]),
        html.Div(className="four columns", children=[html.Label("Author contains:", style={"color": colors["body"]}), author_text]),
        html.Div(className="four columns", children=[html.Label("Show top:", style={"color": colors["body"]}), topn_dropdown]),
    ]),
    dcc.Graph(id="top-books-graph"),
    dash_table.DataTable(id="top-books-table", **table_style),
    html.Hr(),

    html.H3("Content-Based Recommendations", style={"color": colors["text"]}),
    html.P("Select a book to see similar books by genre tags.", style={"color": colors["body"]}),
    book_dropdown,
    dash_table.DataTable(id="content-recs-table", **table_style),
    html.Hr(),

    html.H3("User-User and Item-Item Recommendations", style={"color": colors["text"]}),
    html.P(
        "These were only precomputed for a sample of 30 readers, since recalculating them live "
        "would be too slow.",
        style={"color": colors["body"]},
    ),
    user_dropdown,
    html.Div(className="row", children=[
        html.Div(className="six columns", children=[
            html.H5("User-User Collaborative Filtering", style={"color": colors["text"]}),
            dash_table.DataTable(id="uu-table", **table_style),
        ]),
        html.Div(className="six columns", children=[
            html.H5("Item-Item Collaborative Filtering", style={"color": colors["text"]}),
            dash_table.DataTable(id="ii-table", **table_style),
        ]),
    ]),
    html.Hr(),

    html.H2("Baskets and Associations (Instacart)", style={"color": colors["text"]}),
    html.Div(className="row", children=[
        html.Div(className="six columns", children=[dcc.Graph(figure=fig_basket_size)]),
        html.Div(className="six columns", children=[dcc.Graph(figure=fig_top_products)]),
    ]),

    html.H3("Association Rules", style={"color": colors["text"]}),
    html.P(
        "Apriori and ECLAT found the exact same rules. The chart always shows the Apriori rules; "
        "use the filters below to explore either algorithm's table.",
        style={"color": colors["body"]},
    ),
    dcc.Graph(figure=fig_rules_scatter),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[html.Label("Algorithm:", style={"color": colors["body"]}), algo_radio]),
        html.Div(className="four columns", children=[html.Label("Minimum lift:", style={"color": colors["body"]}), minlift_slider]),
        html.Div(className="four columns", children=[html.Label("Rows to show:", style={"color": colors["body"]}), maxrows_dropdown]),
    ]),
    dash_table.DataTable(id="rules-table", **table_style),
    html.Hr(),

    html.H2("Why the Data Supports Machine Learning", style={"color": colors["text"]}),
    html.P(
        f"There are {summary_books['total_ratings'][0]:,} ratings linking "
        f"{summary_books['total_users'][0]:,} readers to {summary_books['total_books'][0]:,} books. "
        "A rating is a real link between one reader and one book, which is exactly what "
        "content-based and collaborative filtering need to compare books or readers to each other.",
        style={"color": colors["body"]},
    ),
    html.P(
        f"There are {basket_summary['total_baskets'][0]:,} real grocery baskets, with an average of "
        f"{basket_summary['average_basket_size'][0]} items each. A basket with only one item cannot "
        "show which products are bought together, so baskets with several items are what make "
        "Apriori and ECLAT possible.",
        style={"color": colors["body"]},
    ),
    html.Hr(),

    html.H2("Limitations", style={"color": colors["text"]}),
    html.Ul(style={"color": colors["body"]}, children=[
        html.Li("Goodreads ratings are not purchase records from a real bookshop; I use them as a stand-in for customer preference."),
        html.Li("Items in the Instacart data with no matching product name limit how clearly those rules can be interpreted."),
        html.Li("Association rules show historical co-occurrence, not proof that a recommendation or bundle will increase sales."),
    ]),
])


@callback(
    Output("top-books-graph", "figure"),
    Output("top-books-table", "data"),
    Input("genre-dropdown", "value"),
    Input("author-text", "value"),
    Input("topn-dropdown", "value"),
)
def update_top_books(genre, author, top_n):
    filtered = books
    if genre != "All":
        filtered = filtered[filtered["genres"].str.contains(genre, case=False, na=False)]
    if author and author.strip():
        filtered = filtered[filtered["authors"].str.contains(author, case=False, na=False)]

    top_books = filtered.sort_values("ratings_count", ascending=False).head(top_n)

    fig = px.bar(
        top_books, x="ratings_count", y="title", orientation="h",
        hover_data=["average_rating"], title="Top Books by Number of Ratings",
        color_discrete_sequence=[chart_colors[0]],
    )
    fig.update_layout(
        paper_bgcolor=colors["background"], plot_bgcolor=colors["card"], font_color=colors["body"],
        yaxis={"categoryorder": "total ascending"},
    )

    table_cols = ["title", "authors", "original_publication_year", "average_rating", "ratings_count"]
    return fig, top_books[table_cols].to_dict("records")


@callback(
    Output("content-recs-table", "data"),
    Input("book-dropdown", "value"),
)
def update_content_recs(title):
    seed_book_id = books.loc[books["title"] == title, "book_id"].iloc[0]
    recs = content_recs_all[content_recs_all["seed_book_id"] == seed_book_id].sort_values("rank").head(10)
    return recs[["rec_title", "rec_authors", "similarity_score"]].to_dict("records")


@callback(
    Output("uu-table", "data"),
    Output("ii-table", "data"),
    Input("user-dropdown", "value"),
)
def update_user_recs(user_id):
    uu = useruser_recs[useruser_recs["user_id"] == user_id].sort_values("rank")
    ii = itemitem_recs[itemitem_recs["user_id"] == user_id].sort_values("rank")
    cols = ["title", "authors", "predicted_rating"]
    return uu[cols].to_dict("records"), ii[cols].to_dict("records")


@callback(
    Output("rules-table", "data"),
    Input("algo-radio", "value"),
    Input("minlift-slider", "value"),
    Input("maxrows-dropdown", "value"),
)
def update_rules(algorithm, min_lift, max_rows):
    rules = rules_apriori if algorithm == "Apriori" else rules_eclat
    rules = rules[rules["lift"] >= min_lift].sort_values("lift", ascending=False)
    shown = rules.head(max_rows)
    cols = ["antecedent_names", "consequent_names", "support", "confidence", "lift"]
    return shown[cols].to_dict("records")


if __name__ == "__main__":
    app.run(debug=False)
