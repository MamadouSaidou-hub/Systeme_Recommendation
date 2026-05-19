# admin.py
# ============================================================
# RÔLE : Vue admin EduReco — statistiques et supervision
#
# Pages :
#   - Tableau de bord  → KPIs + graphiques globaux
#   - Utilisateurs     → liste complète avec filtres
#   - Recommendations  → toutes les reco générées
#
# ⚠️  L'API doit tourner en parallèle :
#      python api.py  (port 5001)
#
# LANCER : python admin.py
# ACCÈS  : http://127.0.0.1:5002
#
# Dépendances :
#   pip install dash dash-bootstrap-components plotly requests
# ============================================================

import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import requests

# ─────────────────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],  # thème sombre pour l'admin
    suppress_callback_exceptions=True
)
app.title = "EduReco — Admin"

API_URL = "http://127.0.0.1:5001"


# ─────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES — appels API
# ─────────────────────────────────────────────────────────

def fetch_stats():
    """Récupérer les statistiques globales depuis l'API."""
    try:
        r = requests.get(f"{API_URL}/api/admin/stats", timeout=10)
        data = r.json()
        return data['stats'] if data['succes'] else {}
    except Exception:
        return {}


def fetch_users():
    """Récupérer tous les utilisateurs depuis l'API."""
    try:
        r = requests.get(f"{API_URL}/api/admin/users", timeout=10)
        data = r.json()
        return data['users'] if data['succes'] else []
    except Exception:
        return []


def fetch_recos():
    """Récupérer toutes les recommendations depuis l'API."""
    try:
        r = requests.get(f"{API_URL}/api/admin/recommendations", timeout=10)
        data = r.json()
        return data['recommendations'] if data['succes'] else []
    except Exception:
        return []


# ─────────────────────────────────────────────────────────
# COMPOSANTS UI RÉUTILISABLES
# ─────────────────────────────────────────────────────────

def kpi_card(titre, valeur, icone, couleur):
    """Carte KPI — affiche une statistique clé."""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H2(str(valeur),
                            className=f"text-{couleur} fw-bold mb-0"),
                    html.P(titre, className="text-muted mb-0 small")
                ], width=8),
                dbc.Col([
                    html.Span(icone, style={"fontSize": "2.5rem"})
                ], width=4, className="text-end")
            ])
        ])
    ], className="shadow-sm mb-3")


def alerte_api_down():
    """Message d'erreur si l'API ne répond pas."""
    return dbc.Alert([
        html.Strong("❌ API inaccessible. "),
        "Vérifiez que api.py tourne sur le port 5001."
    ], color="danger")


# ─────────────────────────────────────────────────────────
# FONCTIONS DE PAGE
# ─────────────────────────────────────────────────────────

def page_dashboard():
    """Tableau de bord principal — KPIs + graphiques."""
    stats = fetch_stats()

    if not stats:
        return alerte_api_down()

    # ── KPIs ─────────────────────────────────────────────
    kpis = dbc.Row([
        dbc.Col(kpi_card(
            "Utilisateurs inscrits",
            stats.get('total_users', 0),
            "👤", "primary"
        ), width=3),
        dbc.Col(kpi_card(
            "Recommendations générées",
            stats.get('total_recos', 0),
            "🤖", "success"
        ), width=3),
        dbc.Col(kpi_card(
            "Formations recommandées",
            stats.get('nb_formations_reco', 0),
            "🎓", "info"
        ), width=3),
        dbc.Col(kpi_card(
            "Bourses recommandées",
            stats.get('nb_bourses_reco', 0),
            "💰", "warning"
        ), width=3),
    ])

    # ── Graphique : répartition par domaine ──────────────
    par_domaine = stats.get('par_domaine', {})
    fig_domaine = px.pie(
        names=list(par_domaine.keys()),
        values=list(par_domaine.values()),
        title="Répartition par domaine",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_domaine.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        legend=dict(orientation="v")
    )

    # ── Graphique : répartition par niveau ───────────────
    par_niveau = stats.get('par_niveau', {})
    fig_niveau = px.bar(
        x=list(par_niveau.keys()),
        y=list(par_niveau.values()),
        title="Répartition par niveau d'études",
        labels={"x": "Niveau", "y": "Nb utilisateurs"},
        color=list(par_niveau.values()),
        color_continuous_scale="Blues"
    )
    fig_niveau.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
        coloraxis_showscale=False
    )

    # ── Graphique : répartition par pays ─────────────────
    par_pays = stats.get('par_pays', {})
    fig_pays = px.bar(
        x=list(par_pays.values()),
        y=list(par_pays.keys()),
        orientation='h',
        title="Répartition par pays",
        labels={"x": "Nb utilisateurs", "y": "Pays"},
        color=list(par_pays.values()),
        color_continuous_scale="Greens"
    )
    fig_pays.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
        coloraxis_showscale=False
    )

    # ── Gauge : score moyen NLP ───────────────────────────
    score_moyen = stats.get('score_moyen', 0)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_moyen,
        title={"text": "Score NLP moyen (%)", "font": {"color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white"},
            "bar":  {"color": "#00bc8c"},
            "steps": [
                {"range": [0,  40], "color": "#444"},
                {"range": [40, 70], "color": "#555"},
                {"range": [70, 100], "color": "#333"},
            ],
            "threshold": {
                "line":  {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        },
        number={"suffix": "%", "font": {"color": "white"}}
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=250
    )

    return html.Div([
        html.H4("📊 Tableau de bord", className="mb-4"),
        kpis,
        html.Hr(),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_domaine), width=5),
            dbc.Col(dcc.Graph(figure=fig_niveau),  width=4),
            dbc.Col(dcc.Graph(figure=fig_gauge),   width=3),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_pays), width=6),
        ])
    ])


def page_utilisateurs():
    """Liste complète des utilisateurs avec tableau interactif."""
    users = fetch_users()

    if not users:
        return alerte_api_down()

    # Colonnes à afficher dans le tableau
    colonnes = [
        {"name": "ID",       "id": "id"},
        {"name": "Nom",      "id": "nom"},
        {"name": "Prénom",   "id": "prenom"},
        {"name": "Email",    "id": "email"},
        {"name": "Pays",     "id": "pays"},
        {"name": "Niveau",   "id": "niveau_etudes"},
        {"name": "Domaine",  "id": "domaine"},
        {"name": "Objectif", "id": "objectif"},
        {"name": "Créé le",  "id": "created_at"},
    ]

    return html.Div([
        html.H4(f"👤 Utilisateurs — {len(users)} inscrits", className="mb-4"),

        # Tableau interactif avec filtre, tri et pagination
        dash_table.DataTable(
            data=users,
            columns=colonnes,
            page_size=15,
            filter_action="native",    # filtre par colonne
            sort_action="native",      # tri par colonne
            sort_mode="multi",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#375a7f",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "left",
                "padding": "10px"
            },
            style_data={
                "backgroundColor": "#303030",
                "color": "white",
                "padding": "8px"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#2b2b2b"
                }
            ],
            style_filter={
                "backgroundColor": "#444",
                "color": "white"
            },
        )
    ])


def page_recommendations():
    """Liste de toutes les recommendations générées."""
    recos = fetch_recos()

    if not recos:
        return alerte_api_down()

    # Stats rapides
    nb_formations = sum(1 for r in recos if r.get('type_item') == 'formation')
    nb_bourses    = sum(1 for r in recos if r.get('type_item') == 'bourse')

    colonnes = [
        {"name": "ID",        "id": "id"},
        {"name": "User ID",   "id": "user_id"},
        {"name": "Type",      "id": "type_item"},
        {"name": "Item ID",   "id": "item_id"},
        {"name": "Score (%)", "id": "score"},
        {"name": "Raison",    "id": "raisons"},
    ]

    return html.Div([
        html.H4(f"🤖 Recommendations — {len(recos)} générées", className="mb-3"),

        dbc.Row([
            dbc.Col(
                dbc.Alert(f"🎓 Formations : {nb_formations}", color="info"),
                width=3
            ),
            dbc.Col(
                dbc.Alert(f"💰 Bourses : {nb_bourses}", color="warning"),
                width=3
            ),
        ], className="mb-3"),

        dash_table.DataTable(
            data=recos,
            columns=colonnes,
            page_size=20,
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#375a7f",
                "color": "white",
                "fontWeight": "bold",
                "padding": "10px"
            },
            style_data={
                "backgroundColor": "#303030",
                "color": "white",
                "padding": "8px"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#2b2b2b"
                },
                {
                    "if": {
                        "filter_query": "{type_item} = 'formation'",
                        "column_id": "type_item"
                    },
                    "color": "#3498db",
                    "fontWeight": "bold"
                },
                {
                    "if": {
                        "filter_query": "{type_item} = 'bourse'",
                        "column_id": "type_item"
                    },
                    "color": "#f39c12",
                    "fontWeight": "bold"
                },
            ],
        )
    ])


# ═════════════════════════════════════════════════════════
# LAYOUT
# ═════════════════════════════════════════════════════════
app.layout = dbc.Container([

    # Navbar admin
    dbc.NavbarSimple(
        brand="🛡️ EduReco — Administration",
        color="dark",
        dark=True,
        className="mb-4"
    ),

    # Menu de navigation entre les pages admin
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("📊 Tableau de bord",
                           id="btn-dashboard",
                           color="primary",
                           outline=False),
                dbc.Button("👤 Utilisateurs",
                           id="btn-users",
                           color="primary",
                           outline=True),
                dbc.Button("🤖 Recommendations",
                           id="btn-recos",
                           color="primary",
                           outline=True),
                dbc.Button("🔄 Rafraîchir",
                           id="btn-refresh",
                           color="secondary",
                           outline=True),
            ])
        ])
    ], className="mb-4"),

    # Contenu principal
    html.Div(id="admin-contenu", children=page_dashboard()),

], fluid=True)


# ═════════════════════════════════════════════════════════
# CALLBACKS
# ═════════════════════════════════════════════════════════

@app.callback(
    Output("admin-contenu", "children"),
    [
        Input("btn-dashboard", "n_clicks"),
        Input("btn-users",     "n_clicks"),
        Input("btn-recos",     "n_clicks"),
        Input("btn-refresh",   "n_clicks"),
    ],
    prevent_initial_call=True
)
def changer_page(n_dashboard, n_users, n_recos, n_refresh):
    """
    Identifier quel bouton a été cliqué avec callback_context,
    puis afficher la page correspondante.
    """
    # ctx.triggered_id → id du bouton qui a déclenché le callback
    ctx = dash.callback_context
    if not ctx.triggered:
        return page_dashboard()

    bouton_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if bouton_id == "btn-users":
        return page_utilisateurs()
    elif bouton_id == "btn-recos":
        return page_recommendations()
    else:
        # btn-dashboard ou btn-refresh → recharger le dashboard
        return page_dashboard()


# ═════════════════════════════════════════════════════════
# DÉMARRAGE
# ═════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 45)
    print("  EduReco — Admin Dashboard")
    print("=" * 45)
    print("  Admin → http://127.0.0.1:5002")
    print("  API   → http://127.0.0.1:5001")
    print("  ⚠️  Lancer api.py en parallèle !")
    print("  Ctrl+C pour arrêter")
    print("=" * 45)
    app.run(debug=True, port=5002)