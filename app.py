from __future__ import annotations

import csv
import io
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    Response,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from waitress import serve


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
ENV_PATH = BASE_DIR / ".env"
STATIC_DIR = BASE_DIR / "static"
DEFAULT_MEDIATOR_URL = "https://iwana.fr/share/widget/get/9093160"
LEGACY_MEDIATOR_URLS = {
    "",
    "https://reference-url-citation.invalid/0",
    "https://www.noisylegrand.fr/vos-services/solidarite-et-accompagnement/acces-au-droit/point-dinformation-mediation-multi-services",
}

RAW_DB_PATH = os.getenv("PIMMS_DB_PATH", str(INSTANCE_DIR / "pimms.sqlite3"))
DB_PATH = Path(RAW_DB_PATH)
if not DB_PATH.is_absolute():
    DB_PATH = (BASE_DIR / DB_PATH).resolve()


FORM_CITIES = [
    "Neuilly-Plaisance",
    "Champs-sur-Marne",
    "Gournay-sur-Marne",
    "Bry-sur-Marne",
    "Villiers-sur-Marne",
    "Noisiel",
    "Chelles",
    "Gagny",
    "Rosny-sous-Bois",
    "Montfermeil",
    "Clichy-sous-Bois",
    "Le Perreux-sur-Marne",
    "Fontenay-sous-Bois",
    "Autre ville",
]

FORM_DISTRICTS = [
    "Pavé Neuf",
    "Champy - Hauts-Bâtons",
    "Mont d'Est - Palacio - Arcades",
    "Centre-ville",
    "Richardets",
    "La Varenne",
    "Marnois",
    "Bords de Marne",
    "Villeflix",
    "Je ne sais pas",
]

FORM_MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]

FORM_NEEDS_GROUPS = [
    {
        "badge": "EMP",
        "title": "Emploi / Formation",
        "name": "emploiFormation",
        "items": [
            "Rechercher un emploi",
            "Faire ou modifier un CV",
            "Faire une lettre de motivation",
            "Répondre à une offre d'emploi",
            "Consulter mon compte France Travail",
            "Créer mon compte France Travail",
            "Actualiser ma situation France Travail",
            "Télécharger une attestation France Travail",
            "Trouver une formation",
            "CPF (Compte Personnel de Formation)",
        ],
    },
    {
        "badge": "CAF",
        "title": "CAF / Aides sociales",
        "name": "cafAidesSociales",
        "items": [
            "Faire ma déclaration trimestrielle CAF",
            "Télécharger une attestation CAF",
            "Consulter mon dossier CAF",
            "Créer mon compte CAF",
            "Faire une demande CAF",
            "RSA",
            "Prime d'activité",
            "Allocation logement",
            "Dossier d'aide sociale",
            "Chèque énergie",
        ],
    },
    {
        "badge": "SAN",
        "title": "Santé",
        "name": "sante",
        "items": [
            "Télécharger une attestation Assurance Maladie",
            "Consulter mon compte Ameli",
            "Créer mon compte Ameli",
            "Déclarer un changement de situation",
            "Demander une carte Vitale",
            "Complémentaire Santé Solidaire (CSS)",
            "Mutuelle",
            "AP-HP",
        ],
    },
    {
        "badge": "FIS",
        "title": "Impôts",
        "name": "impots",
        "items": [
            "Faire ma déclaration d'impôts",
            "Télécharger mon avis d'imposition",
            "Consulter mon espace impôts",
            "Payer un impôt",
            "Corriger une déclaration",
            "Obtenir un justificatif fiscal",
        ],
    },
    {
        "badge": "RET",
        "title": "Retraite",
        "name": "retraite",
        "items": [
            "Déposer un dossier retraite",
            "Préparer ma retraite",
            "Consulter ma carrière retraite",
            "Télécharger un document retraite",
            "Demander une attestation retraite",
        ],
    },
    {
        "badge": "LOG",
        "title": "Logement",
        "name": "logement",
        "items": [
            "Rechercher un logement",
            "Faire une demande de logement social",
            "Renouveler une demande de logement social",
            "Consulter mon dossier logement",
            "Payer mon loyer",
            "Contacter mon bailleur",
            "Seqens",
            "DALO",
            "Garantie Visale",
        ],
    },
    {
        "badge": "ID",
        "title": "Documents / Identité",
        "name": "documentsIdentite",
        "items": [
            "Carte grise",
            "Permis de conduire",
            "Carte d'identité",
            "Passeport",
            "Carte famille nombreuse",
            "Titre de séjour",
            "Renouvellement de document",
        ],
    },
    {
        "badge": "NUM",
        "title": "Numérique",
        "name": "numerique",
        "items": [
            "Consulter mes mails",
            "Envoyer un mail",
            "Créer une adresse mail",
            "Créer un compte sur un site",
            "Modifier un mot de passe",
            "Télécharger un document",
            "Utiliser un service en ligne",
            "Connexion à un compte",
        ],
    },
    {
        "badge": "MDP",
        "title": "Handicap",
        "name": "handicap",
        "items": ["Dossier MDPH", "AAH", "RQTH", "Handicap"],
    },
    {
        "badge": "TRP",
        "title": "Transport",
        "name": "transport",
        "items": ["Solidarité transport", "Carte Navigo", "Réduction transport"],
    },
    {
        "badge": "EDU",
        "title": "Éducation",
        "name": "education",
        "items": ["Dossier scolaire", "Inscription scolaire", "Bourse"],
    },
    {
        "badge": "BNQ",
        "title": "Banque / Assurance",
        "name": "banqueAssurance",
        "items": ["Banque", "Assurance habitation", "Assurance automobile"],
    },
    {
        "badge": "NRJ",
        "title": "Énergie / Habitat",
        "name": "energieHabitat",
        "items": ["France Rénov'", "Aides à la rénovation", "Énergie"],
    },
    {
        "badge": "AUT",
        "title": "Autre",
        "name": "autre",
        "items": ["Autre démarche"],
    },
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_or_create_secret(path: Path, env_name: str, fallback_length: int = 32) -> str:
    env_value = os.getenv(env_name)
    if env_value:
        return env_value

    if path.exists():
        return path.read_text(encoding="utf-8").strip()

    value = secrets.token_urlsafe(fallback_length)
    path.write_text(value, encoding="utf-8")
    return value


load_env_file(ENV_PATH)
ensure_directory(INSTANCE_DIR)
ensure_directory(DB_PATH.parent)

app = Flask(__name__)
app.config["SECRET_KEY"] = read_or_create_secret(INSTANCE_DIR / "secret_key.txt", "SECRET_KEY")
app.config["ADMIN_PASSWORD"] = read_or_create_secret(
    INSTANCE_DIR / "admin_password.txt",
    "ADMIN_PASSWORD",
    fallback_length=18,
)
configured_mediator_url = os.getenv("MEDIATOR_URL", "").strip()
if configured_mediator_url in LEGACY_MEDIATOR_URLS:
    configured_mediator_url = DEFAULT_MEDIATOR_URL
app.config["MEDIATOR_URL"] = configured_mediator_url
app.config["REPORTING_NAME"] = os.getenv("REPORTING_NAME", "Tableau des réponses")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submitted_at TEXT NOT NULL,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                birth_day INTEGER NOT NULL,
                birth_month TEXT NOT NULL,
                birth_year INTEGER NOT NULL,
                birth_date_display TEXT NOT NULL,
                gender TEXT NOT NULL,
                noisy_resident TEXT NOT NULL,
                city TEXT,
                district TEXT,
                first_visit TEXT,
                needs_summary TEXT NOT NULL,
                needs_json TEXT NOT NULL,
                other_request TEXT,
                need_print TEXT,
                need_scan TEXT,
                help_level TEXT NOT NULL,
                time_needed TEXT NOT NULL,
                rsa TEXT,
                phone TEXT,
                payload_json TEXT NOT NULL,
                source_ip TEXT,
                user_agent TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def get_source_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or ""


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_grouped_needs(payload: dict[str, Any]) -> tuple[dict[str, list[str]], list[str]]:
    raw_needs = payload.get("needs") or {}
    grouped: dict[str, list[str]] = {}
    flat_items: list[str] = []

    for group in FORM_NEEDS_GROUPS:
        group_values = raw_needs.get(group["name"], [])
        if not isinstance(group_values, list):
            continue
        cleaned = [normalize_text(item) for item in group_values if normalize_text(item)]
        if cleaned:
            grouped[group["title"]] = cleaned
            flat_items.extend(cleaned)

    return grouped, flat_items


def validate_payload(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, str]]:
    errors: dict[str, str] = {}

    identite = payload.get("identite") or {}
    residence = payload.get("residence") or {}
    aide = payload.get("aide") or {}
    equipement = payload.get("equipement") or {}
    facultatif = payload.get("informationsFacultatives") or {}

    last_name = normalize_text(identite.get("nom"))
    first_name = normalize_text(identite.get("prenom"))
    gender = normalize_text(identite.get("genre"))

    birth = identite.get("dateDeNaissance") or {}
    birth_day = normalize_text(birth.get("jour"))
    birth_month = normalize_text(birth.get("mois"))
    birth_year = normalize_text(birth.get("annee"))

    noisy_resident = normalize_text(residence.get("noisyLeGrand"))
    city = normalize_text(residence.get("ville"))
    district = normalize_text(residence.get("quartier"))
    first_visit = normalize_text(payload.get("premiereVisite"))

    grouped_needs, flat_needs = extract_grouped_needs(payload)
    other_request = normalize_text(payload.get("autreDemarche"))

    need_print = normalize_text(equipement.get("impression"))
    need_scan = normalize_text(equipement.get("scan"))
    help_level = normalize_text(aide.get("niveau"))
    time_needed = normalize_text(aide.get("tempsEstime"))
    rsa = normalize_text(facultatif.get("rsa"))
    phone = normalize_text(facultatif.get("telephone"))

    if not last_name:
        errors["nom"] = "Le nom est requis."
    if not first_name:
        errors["prenom"] = "Le prénom est requis."
    if not birth_day or not birth_month or not birth_year:
        errors["dateDeNaissance"] = "La date de naissance est requise."
    if not gender:
        errors["genre"] = "Le genre est requis."
    if noisy_resident not in {"Oui", "Non"}:
        errors["residence"] = "Le lieu de résidence doit être précisé."
    if noisy_resident == "Oui" and not district:
        errors["quartier"] = "Le quartier est requis pour les habitants de Noisy-le-Grand."
    if noisy_resident == "Non" and not city:
        errors["ville"] = "La ville est requise."
    if not flat_needs:
        errors["demarches"] = "Au moins une démarche doit être sélectionnée."
    if "Autre démarche" in flat_needs and not other_request:
        errors["autreDemarche"] = "La description de l'autre démarche est requise."
    if not help_level:
        errors["niveauAide"] = "Le niveau d'aide est requis."
    if not time_needed:
        errors["temps"] = "Le temps estimé est requis."

    try:
        day_int = int(birth_day)
        year_int = int(birth_year)
    except ValueError:
        errors["dateDeNaissance"] = "La date de naissance est invalide."
        day_int = 0
        year_int = 0

    if errors:
        return None, errors

    normalized = {
        "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "last_name": last_name,
        "first_name": first_name,
        "birth_day": day_int,
        "birth_month": birth_month,
        "birth_year": year_int,
        "birth_date_display": f"{day_int} {birth_month} {year_int}",
        "gender": gender,
        "noisy_resident": noisy_resident,
        "city": city,
        "district": district,
        "first_visit": first_visit,
        "needs_grouped": grouped_needs,
        "needs_summary": " | ".join(flat_needs),
        "needs_json": json.dumps(grouped_needs, ensure_ascii=False),
        "other_request": other_request,
        "need_print": need_print,
        "need_scan": need_scan,
        "help_level": help_level,
        "time_needed": time_needed,
        "rsa": rsa,
        "phone": phone,
        "payload_json": json.dumps(payload, ensure_ascii=False),
        "source_ip": get_source_ip(),
        "user_agent": request.headers.get("User-Agent", ""),
    }
    return normalized, {}


def insert_submission(submission: dict[str, Any]) -> int:
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO submissions (
            submitted_at,
            last_name,
            first_name,
            birth_day,
            birth_month,
            birth_year,
            birth_date_display,
            gender,
            noisy_resident,
            city,
            district,
            first_visit,
            needs_summary,
            needs_json,
            other_request,
            need_print,
            need_scan,
            help_level,
            time_needed,
            rsa,
            phone,
            payload_json,
            source_ip,
            user_agent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            submission["submitted_at"],
            submission["last_name"],
            submission["first_name"],
            submission["birth_day"],
            submission["birth_month"],
            submission["birth_year"],
            submission["birth_date_display"],
            submission["gender"],
            submission["noisy_resident"],
            submission["city"],
            submission["district"],
            submission["first_visit"],
            submission["needs_summary"],
            submission["needs_json"],
            submission["other_request"],
            submission["need_print"],
            submission["need_scan"],
            submission["help_level"],
            submission["time_needed"],
            submission["rsa"],
            submission["phone"],
            submission["payload_json"],
            submission["source_ip"],
            submission["user_agent"],
        ),
    )
    db.commit()
    return int(cursor.lastrowid)


def fetch_submissions(search_text: str = "") -> list[sqlite3.Row]:
    db = get_db()
    if not search_text:
        cursor = db.execute("SELECT * FROM submissions ORDER BY id DESC")
        return cursor.fetchall()

    pattern = f"%{search_text}%"
    cursor = db.execute(
        """
        SELECT * FROM submissions
        WHERE
            CAST(id AS TEXT) LIKE ?
            OR last_name LIKE ?
            OR first_name LIKE ?
            OR city LIKE ?
            OR district LIKE ?
            OR needs_summary LIKE ?
            OR help_level LIKE ?
        ORDER BY id DESC
        """,
        (pattern, pattern, pattern, pattern, pattern, pattern, pattern),
    )
    return cursor.fetchall()


def fetch_stats() -> dict[str, int]:
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    today = db.execute(
        """
        SELECT COUNT(*) FROM submissions
        WHERE substr(submitted_at, 1, 10) = ?
        """,
        (datetime.now(timezone.utc).date().isoformat(),),
    ).fetchone()[0]
    noisy = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE noisy_resident = 'Oui'"
    ).fetchone()[0]
    mediator = db.execute(
        """
        SELECT COUNT(*) FROM submissions
        WHERE help_level = ?
        """,
        ("J'ai besoin de prendre rendez-vous avec un médiateur social",),
    ).fetchone()[0]
    return {
        "total": total,
        "today": today,
        "noisy": noisy,
        "mediator": mediator,
    }


def format_submission_for_template(row: sqlite3.Row) -> dict[str, Any]:
    payload = json.loads(row["payload_json"])
    needs_grouped = json.loads(row["needs_json"])
    return {
        "id": row["id"],
        "submitted_at": row["submitted_at"],
        "last_name": row["last_name"],
        "first_name": row["first_name"],
        "birth_date_display": row["birth_date_display"],
        "gender": row["gender"],
        "noisy_resident": row["noisy_resident"],
        "city": row["city"],
        "district": row["district"],
        "first_visit": row["first_visit"],
        "needs_summary": row["needs_summary"],
        "needs_grouped": needs_grouped,
        "other_request": row["other_request"],
        "need_print": row["need_print"],
        "need_scan": row["need_scan"],
        "help_level": row["help_level"],
        "time_needed": row["time_needed"],
        "rsa": row["rsa"],
        "phone": row["phone"],
        "source_ip": row["source_ip"],
        "payload_pretty": json.dumps(payload, ensure_ascii=False, indent=2),
    }


def get_inline_asset(filename: str) -> str:
    return (STATIC_DIR / filename).read_text(encoding="utf-8")


def render_form_page() -> str:
    current_year = datetime.now().year
    years = list(range(current_year, 1919, -1))
    return render_template(
        "index.html",
        city_suggestions=FORM_CITIES,
        districts=FORM_DISTRICTS,
        months=FORM_MONTHS,
        years=years,
        needs_groups=FORM_NEEDS_GROUPS,
        mediator_url=app.config["MEDIATOR_URL"],
        admin_available=True,
    )


def render_dashboard_page(search_text: str) -> str:
    submissions = [format_submission_for_template(row) for row in fetch_submissions(search_text)]
    stats = fetch_stats()
    return render_template(
        "admin.html",
        submissions=submissions,
        stats=stats,
        search_text=search_text,
        admin_password_path=str((INSTANCE_DIR / "admin_password.txt").resolve()),
    )


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {
        "reporting_name": app.config["REPORTING_NAME"],
        "inline_styles": get_inline_asset("styles.css"),
        "inline_script": get_inline_asset("script.js"),
    }


@app.route("/", methods=["GET", "POST"])
def index() -> str | Response:
    mode = request.args.get("mode", "form")

    if mode == "tableau":
        if request.method == "POST":
            action = request.form.get("admin_action", "login")
            if action == "logout":
                session.clear()
                return redirect(url_for("index", mode="tableau"))

            password = request.form.get("password", "")
            if secrets.compare_digest(password, app.config["ADMIN_PASSWORD"]):
                session["admin_authenticated"] = True
                return redirect(url_for("index", mode="tableau"))
            flash("Mot de passe incorrect.", "error")

        if session.get("admin_authenticated"):
            search_text = request.args.get("q", "").strip()
            return render_dashboard_page(search_text)

        return render_template(
            "admin_login.html",
            next_url=url_for("index", mode="tableau"),
        )

    return render_form_page()


@app.get("/api/health")
def health() -> Response:
    return jsonify({"ok": True, "time": datetime.now(timezone.utc).isoformat(timespec="seconds")})


@app.post("/api/submissions")
def create_submission() -> Response:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "message": "Corps de requête invalide."}), 400

    normalized, errors = validate_payload(payload)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    submission_id = insert_submission(normalized)
    return (
        jsonify(
            {
                "ok": True,
                "submissionId": submission_id,
                "submittedAt": normalized["submitted_at"],
                "adminUrl": url_for("index", mode="tableau"),
            }
        ),
        201,
    )


@app.route("/tableau/connexion", methods=["GET", "POST"])
def admin_login():
    return redirect(url_for("index", mode="tableau"))


@app.post("/tableau/deconnexion")
def admin_logout():
    session.clear()
    return redirect(url_for("index", mode="tableau"))


@app.get("/tableau")
def admin_dashboard() -> str:
    query = request.args.get("q", "").strip()
    return redirect(url_for("index", mode="tableau", q=query))


@app.get("/api/reporting/export.csv")
@admin_required
def admin_export_csv() -> Response:
    rows = fetch_submissions(request.args.get("q", "").strip())
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Date d'enregistrement",
            "Nom",
            "Prénom",
            "Date de naissance",
            "Genre",
            "Habite à Noisy-le-Grand",
            "Ville",
            "Quartier",
            "Première visite",
            "Démarches",
            "Autre demande",
            "Impression",
            "Scan",
            "Niveau d'aide",
            "Temps estimé",
            "RSA",
            "Téléphone",
            "IP source",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["id"],
                row["submitted_at"],
                row["last_name"],
                row["first_name"],
                row["birth_date_display"],
                row["gender"],
                row["noisy_resident"],
                row["city"],
                row["district"],
                row["first_visit"],
                row["needs_summary"],
                row["other_request"],
                row["need_print"],
                row["need_scan"],
                row["help_level"],
                row["time_needed"],
                row["rsa"],
                row["phone"],
                row["source_ip"],
            ]
        )

    filename = f"pimms-reponses-{datetime.now().date().isoformat()}.csv"
    csv_content = "\ufeff" + output.getvalue()
    return Response(
        csv_content,
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def main() -> None:
    init_db()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"

    if debug:
        app.run(host=host, port=port, debug=True)
        return

    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
