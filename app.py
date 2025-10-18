import os
import re
import json
from pathlib import Path

import streamlit as st
import pandas as pd

# Paths
BASE_DIR = Path(__file__).resolve().parent
MARKDOWN_DIR = BASE_DIR.parent / "markdown"  # Adjusted to ../markdown
PROGRESS_FILE = BASE_DIR / ".progress.json"

st.set_page_config(page_title="KodeKloud Progress Tracker", layout="wide")

# CSS personnalisé pour réduire l'espacement entre les cours
st.markdown("""
<style>
    /* Réduire l'espacement entre les éléments de cours */
    .stCheckbox, .stTextInput, .stMarkdown {
        margin-bottom: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    
    /* Réduire l'espacement dans les colonnes */
    .css-1lcbmhc {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    
    /* Réduire l'espacement des conteneurs */
    .css-1y4p8pa {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    
    /* Réduire les marges des éléments de formulaire */
    .stCheckbox > div, .stTextInput > div {
        margin-bottom: 0.1rem !important;
    }
    
    /* Réduire l'espacement des captions */
    .stCaption {
        margin-bottom: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Suivi KodeKloud — Paths SRE / DevOps / Cloud / MLOps")

# Liens KodeKloud
st.markdown("### Liens KodeKloud")
col1, col2 = st.columns(2)
with col1:
    st.markdown("[Learning Paths](https://kodekloud.com/learning-paths/)")
with col2:
    st.markdown("[Courses](https://kodekloud.com/courses/)")


def get_base_title(title):
    """Retire les tags [DOUBLON - ...] du titre pour obtenir le titre de base"""
    return re.sub(r'\s*\[DOUBLON\s*-\s*[^]]*\]', '', title).strip()


@st.cache_data
def load_json_files():
    paths_data = {}
    json_files = ["sre.json", "devops.json", "cloud.json", "mlops.json"]
    for filename in json_files:
        filepath = BASE_DIR / filename
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                # Extract path name from filename
                path_key = filename.replace(".json", "")
                paths_data[path_key] = data
            except Exception as e:
                st.error(f"Erreur chargement {filename}: {e}")

    # Ajoute le path global APRÈS avoir chargé tous les autres paths
    paths_data["global"] = create_global_path(paths_data)

    return paths_data


def create_global_path(paths_data):
    """Crée un path global qui regroupe tous les cours uniques (sans doublons)"""
    global_path = {
        "name": "🌍 Path Global - Tous les Cours",
        "description": "Path global regroupant tous les cours uniques des 4 paths (SRE, DevOps, Cloud, MLOps)",
        "duree_mois": "12-15",
        "cours_total": 0,
        "video_heures": 0,
        "labs_heures": 0,
        "salaires": {
            "usd": "Variable selon spécialisation",
            "chf": "Variable selon spécialisation",
            "gbp": "Variable selon spécialisation",
            "cad": "Variable selon spécialisation"
        },
        "competences": [
            "Toutes les compétences des 4 paths combinées"
        ],
        "cours": [],
        "phases": []
    }

    # Collecte tous les cours uniques (en normalisant les titres)
    all_courses = {}
    course_to_paths = {}  # Pour savoir dans quels paths chaque cours apparaît

    for path_key, data in paths_data.items():
        if path_key == "global":
            continue  # Skip the global path
        path_name = data["name"]
        courses = data.get("cours", [])

        # Ajouter les cours principaux
        for course in courses:
            if isinstance(course, dict):
                course_title = course.get("titre", "")
                base_title = get_base_title(course_title)
            elif isinstance(course, str):
                course_title = course
                base_title = course
            else:
                continue  # Skip invalid course formats

            if base_title not in all_courses:
                # Crée une copie du cours avec le titre normalisé
                if isinstance(course, dict):
                    course_copy = course.copy()
                    course_copy["titre"] = base_title
                    all_courses[base_title] = course_copy
                else:
                    all_courses[base_title] = course
                course_to_paths[base_title] = [path_name]
            else:
                if path_name not in course_to_paths[base_title]:
                    course_to_paths[base_title].append(path_name)

    # Ajoute les cours au path global avec métadonnées
    for course_key, course in all_courses.items():
        if isinstance(course, dict):
            course_copy = course.copy()
            course_copy["shared_with"] = course_to_paths[course_key]
            course_copy["is_shared"] = len(course_to_paths[course_key]) > 1
            global_path["cours"].append(course_copy)
        elif isinstance(course, str):
            # Pour les anciens formats
            global_path["cours"].append({
                "titre": course,
                "duree": "N/A",
                "lien": "",
                "shared_with": course_to_paths[course_key],
                "is_shared": len(course_to_paths[course_key]) > 1,
                "completed": False,
                "comment": ""
            })

    global_path["cours_total"] = len(global_path["cours"])

    # Organise par phases logiques
    global_path["phases"] = [
        {
            "nom": "🧱 Fondamentaux (communs à tous)",
            "cours": [c["titre"] if isinstance(c, dict) else c for c in global_path["cours"]
                     if (isinstance(c, dict) and c.get("is_shared", False) and len(c.get("shared_with", [])) >= 3) or
                        (isinstance(c, str) and len(course_to_paths.get(c, [])) >= 3)]
        },
        {
            "nom": "☸️ Kubernetes Learning Path",
            "cours": [
                "12 Factor App",
                "DevOps Prerequisite course",
                "Linux for Beginners",
                "Docker for Absolute Beginners",
                "Kubernetes for Beginners",
                "AWS EKS",
                "Helm for Beginners",
                "Istio Service Mesh",
                "Kubernetes Networking Deep Dive",
                "Kustomize",
                "EFK Stack: Enterprise-Grade Logging and Monitoring",
                "Learn By Doing: Deploying and Managing the EFK Stack on Kubernetes",
                "Learn By Doing: Kubernetes Policies with Kyverno",
                "Kubernetes Administration: Package Management with Glasskube",
                "Prometheus Certified Associate (PCA)",
                "Grafana Loki",
                "Kubernetes Troubleshooting for Application Developers",
                "Telepresence For Kubernetes",
                "Kubernetes Autoscaling",
                "Certified Kubernetes Administrator (CKA)",
                "Kubernetes and Cloud Native Security Associate (KCSA)"
            ]
        },
        {
            "nom": "🎯 Spécialisations",
            "cours": [c["titre"] if isinstance(c, dict) else c for c in global_path["cours"]
                     if not any(keyword in (c["titre"] if isinstance(c, dict) else c).lower()
                               for keyword in ["docker", "kubernetes", "terraform", "ansible", "git", "jenkins", "aws", "azure", "gcp",
                                             "prerequisite", "linux", "python", "golang", "12 factor", "helm", "istio", "efk", "prometheus", "grafana", "telepresence", "kyverno", "glasskube", "cka", "kcsa"])]
        }
    ]

    return global_path


def get_course_completion_status(course_title, current_path, progress_data):
    """Vérifie si un cours est complété dans le path actuel ou dans d'autres paths"""
    # Pour le path actuel
    current_path_data = progress_data.get(current_path, [])
    current_path_completed = any(
        task.get("task") == course_title and task.get("done", False)
        for task in current_path_data
        if isinstance(task, dict)
    )

    # Vérifie dans les autres paths
    other_paths_completed = []
    for path_key, path_tasks in progress_data.items():
        if path_key != current_path and isinstance(path_tasks, list):
            if any(
                task.get("task") == course_title and task.get("done", False)
                for task in path_tasks
                if isinstance(task, dict)
            ):
                other_paths_completed.append(path_key)

    return {
        "current_completed": current_path_completed,
        "other_completed": other_paths_completed,
        "any_completed": current_path_completed or len(other_paths_completed) > 0
    }


def extract_paths_from_text(text):
    # Find PATH headings like "# PATH #1: Site Reliability Engineer (SRE)" or "# PATH #1: Site Reliability Engineer"
    paths = {}
    # Use regex to find positions of PATH headings
    pattern = re.compile(r"(?i)PATH\s*#?\s*\d+\s*[:\-]?\s*([^\n\r]+)")
    matches = list(pattern.finditer(text))
    if not matches:
        return paths
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        paths[name] = chunk
    return paths


def extract_paths_from_text(text):
    # Find PATH headings like "# PATH #1: Site Reliability Engineer (SRE)" or "# PATH #1: Site Reliability Engineer"
    paths = {}
    # Use regex to find positions of PATH headings
    pattern = re.compile(r"(?i)PATH\s*#?\s*\d+\s*[:\-]?\s*([^\n\r]+)")
    matches = list(pattern.finditer(text))
    if not matches:
        return paths
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        paths[name] = chunk
    return paths


def extract_course_names(text):
    names = []
    if not text:
        return names
    # 1) Find bolded names like **DevOps Prerequisite** or **1. DevOps Prerequisite (6.5h)**
    bolds = re.findall(r"\*\*([^*]{3,150}?)\*\*", text)
    for b in bolds:
        # clean numbering and time markers
        b2 = re.sub(r"^\s*\d+\.\s*", "", b)
        b2 = re.sub(r"\s*\(.*?h.*?\)", "", b2)
        b2 = b2.strip()
        if len(b2) > 3:
            names.append(b2)
    # 2) Find lines that start with a number and a dot: "1. Docker (4h)"
    lines = re.findall(r"^\s*\d+\.\s*([^\n\r]+)", text, flags=re.MULTILINE)
    for l in lines:
        l2 = re.sub(r"\s*\(.*?h.*?\)", "", l).strip()
        if len(l2) > 3:
            names.append(l2)
    # 3) Find table rows that include course names wrapped in pipes and bold
    table_bolds = re.findall(r"\|\s*\*\*([^*]{3,150}?)\*\*", text)
    for t in table_bolds:
        t2 = re.sub(r"\s*\(.*?h.*?\)", "", t).strip()
        if len(t2) > 3:
            names.append(t2)
    # dedupe while preserving order
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_progress(data):
    PROGRESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def calculate_progress_percentage(courses):
    """Calcule le pourcentage de progression pour une liste de cours"""
    if not courses:
        return 0
    completed = sum(1 for course in courses if course.get('completed', False))
    return int((completed / len(courses)) * 100)


def update_course_progress(path_key, course_title, completed=None, comment=None):
    """Met à jour la progression d'un cours spécifique"""
    progress = load_progress()
    if path_key not in progress:
        progress[path_key] = []

    # Chercher la tâche existante ou en créer une nouvelle
    path_tasks = progress[path_key]
    task_found = False

    for task in path_tasks:
        if isinstance(task, dict) and task.get("task") == course_title:
            if completed is not None:
                task["done"] = completed
            # Note: comment n'est pas supporté dans la nouvelle structure
            task_found = True
            break

    # Si la tâche n'existe pas, l'ajouter
    if not task_found and completed is not None:
        path_tasks.append({"task": course_title, "done": completed})

    save_progress(progress)
    return progress


paths_data = load_json_files()
md_files = {}  # Keep for viewing raw markdown if needed - now empty since we use JSON
all_text = ""  # Not needed anymore

# Known path names (user-friendly) - allow variations
KNOWN_PATHS = ["SRE", "Site Reliability Engineer", "DevOps", "DevOps Engineer", "Cloud", "Cloud Engineer", "AI", "MLOps", "AI/MLOps", "AI/MLOps Engineer"]
# Derive available paths from markdown by looking for PATH headings
found_paths = {}
for name, content in md_files.items():
    p = extract_paths_from_text(content)
    for k, v in p.items():
        # normalize short name
        short = k
        if "SRE" in k or "Reliability" in k:
            short = "SRE"
        elif "DevOps" in k and "MLOps" not in k:
            short = "DevOps"
        elif "Cloud" in k and "AI" not in k:
            short = "Cloud"
        elif "AI" in k or "MLOps" in k:
            short = "MLOps"
        found_paths[short] = found_paths.get(short, "") + "\n\n" + v

# Merge: if no PATH headers found, fallback to searching all text for course names
paths_options = ["SRE", "DevOps", "Cloud", "MLOps"]

# Onglets
tab1, tab2, tab3 = st.tabs(["📋 Sommaire", "🌍 Path Global", "📚 Parcours Spécialisés"])

with tab1:
    st.header("📊 Dashboard de Progression KodeKloud")

    progress_data = load_progress()

    # Calcul des métriques globales
    total_courses_all_paths = 0
    completed_courses_all_paths = 0
    path_progress = []

    for path_key, data in paths_data.items():
        courses = data.get("cours", [])
        total_courses = len(courses)
        total_courses_all_paths += total_courses

        # Récupérer la progression depuis le fichier de sauvegarde
        path_progress_data = progress_data.get(path_key, [])
        completed_count = 0

        for course in courses:
            course_title = course.get("titre", course) if isinstance(course, dict) else course
            # Vérifier si le cours est marqué comme terminé dans la liste des tâches
            if isinstance(path_progress_data, list):
                course_completed = any(
                    task.get("task") == course_title and task.get("done", False)
                    for task in path_progress_data
                    if isinstance(task, dict)
                )
            else:
                # Fallback pour l'ancienne structure
                course_completed = path_progress_data.get(course_title, {}).get("completed", False)

            if course_completed:
                completed_count += 1

        completed_courses_all_paths += completed_count
        progress_percentage = int((completed_count / total_courses) * 100) if total_courses > 0 else 0

        path_progress.append({
            "Path": data["name"],
            "Progression": f"{completed_count}/{total_courses} ({progress_percentage}%)",
            "Pourcentage": progress_percentage,
            "Durée": data["duree_mois"],
            "Salaires": data["salaires"]["usd"] if "usd" in data["salaires"] else data["salaires"]["chf"],
            "Cours": total_courses
        })

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        overall_progress = int((completed_courses_all_paths / total_courses_all_paths) * 100) if total_courses_all_paths > 0 else 0
        st.metric("Progression Globale", f"{overall_progress}%")
    with col2:
        st.metric("Cours Terminés", f"{completed_courses_all_paths}/{total_courses_all_paths}")
    with col3:
        active_paths = sum(1 for p in path_progress if p["Pourcentage"] > 0)
        st.metric("Paths Actifs", active_paths)
    with col4:
        avg_progress = sum(p["Pourcentage"] for p in path_progress) / len(path_progress) if path_progress else 0
        st.metric("Moyenne Paths", f"{int(avg_progress)}%")

    # Graphique de progression par path
    st.markdown("### 📈 Progression par Path")
    progress_df = pd.DataFrame(path_progress)
    if not progress_df.empty:
        # Bar chart pour la progression
        chart_data = progress_df.set_index("Path")[["Pourcentage"]]
        st.bar_chart(chart_data)

    # Tableau des cours terminés
    st.markdown("### ✅ Cours Terminés")
    completed_courses_list = []
    
    for path_key, data in paths_data.items():
        if path_key == "global":
            continue
        courses = data.get("cours", [])
        path_progress_data = progress_data.get(path_key, [])
        
        for course in courses:
            course_title = course.get("titre", course) if isinstance(course, dict) else course
            course_duration = course.get("duree", "N/A") if isinstance(course, dict) else "N/A"
            
            # Vérifier si le cours est terminé
            if isinstance(path_progress_data, list):
                course_completed = any(
                    task.get("task") == course_title and task.get("done", False)
                    for task in path_progress_data
                    if isinstance(task, dict)
                )
            else:
                course_completed = path_progress_data.get(course_title, {}).get("completed", False)
            
            if course_completed:
                completed_courses_list.append({
                    "Path": data["name"],
                    "Cours": course_title,
                    "Durée": course_duration,
                    "path_key": path_key
                })
    
    if completed_courses_list:
        st.write(f"**Total: {len(completed_courses_list)} cours terminés**")
        
        # Afficher les cours terminés avec possibilité de décocher
        for idx, course_data in enumerate(completed_courses_list):
            col1, col2, col3, col4 = st.columns([0.08, 0.5, 0.2, 0.22])
            
            with col1:
                # Checkbox pour décocher le cours terminé
                is_still_completed = st.checkbox(
                    "Done",
                    value=True,
                    key=f"completed_course_{idx}_{course_data['path_key']}_{course_data['Cours']}",
                    label_visibility="hidden"
                )
                if not is_still_completed:
                    # Marquer comme non-terminé
                    update_course_progress(course_data['path_key'], course_data['Cours'], completed=False)
                    st.rerun()
            
            with col2:
                st.markdown(f"**{course_data['Cours']}**")
            
            with col3:
                st.caption(f"⏱️ {course_data['Durée']}")
            
            with col4:
                st.caption(f"📚 {course_data['Path']}")
    else:
        st.info("Aucun cours terminé pour le moment.")

    # Tableau détaillé
    st.markdown("### 📋 Détails des Paths")
    if path_progress:
        df = pd.DataFrame(path_progress)
        st.table(df[["Path", "Progression", "Durée", "Salaires", "Cours"]])
    else:
        st.error("Aucune donnée JSON chargée.")

    # Tableau de tous les cours avec progression
    st.markdown("### 📚 Tous les Cours et leur Progression")
    all_courses_data = []
    progress_data = load_progress()

    for path_key, data in paths_data.items():
        courses = data.get("cours", [])
        path_name = data["name"]

        for course in courses:
            if isinstance(course, dict):
                course_title = course.get("titre", "")
                course_duration = course.get("duree", "N/A")
                course_link = course.get("lien", "")
            else:
                course_title = course
                course_duration = "N/A"
                course_link = ""

            # Vérifier la progression
            path_progress_data = progress_data.get(path_key, [])
            if isinstance(path_progress_data, list):
                # Nouvelle structure: liste de tâches
                course_progress = next(
                    (task for task in path_progress_data
                     if isinstance(task, dict) and task.get("task") == course_title),
                    {}
                )
                completed = course_progress.get("done", False)
                comment = ""  # Pas de commentaires dans la nouvelle structure
            else:
                # Ancienne structure: dict de cours
                course_progress = path_progress_data.get(course_title, {})
                completed = course_progress.get("completed", False)
                comment = course_progress.get("comment", "")

            # Calculer le pourcentage de completion du path
            total_path_courses = len(courses)
            completed_path_courses = sum(1 for c in courses if (
                isinstance(c, dict) and 
                (isinstance(path_progress_data, list) and any(
                    task.get("task") == c.get("titre", "") and task.get("done", False)
                    for task in path_progress_data if isinstance(task, dict)
                )) or
                (not isinstance(path_progress_data, list) and path_progress_data.get(c.get("titre", ""), {}).get("completed", False))
            ))
            path_completion_percentage = int((completed_path_courses / total_path_courses) * 100) if total_path_courses > 0 else 0

            status = f"{path_completion_percentage}%"

            all_courses_data.append({
                "Path": path_name,
                "Cours": course_title,
                "Durée": course_duration,
                "Statut": status,
                "Lien": f"[Accéder]({course_link})" if course_link else "N/A"
            })

    if all_courses_data:
        # Au lieu d'utiliser dataframe, afficher chaque cours avec des liens cliquables
        st.markdown("#### Liste détaillée des cours :")
        
        # Grouper par path pour une meilleure organisation
        courses_by_path = {}
        for course_data in all_courses_data:
            path = course_data["Path"]
            if path not in courses_by_path:
                courses_by_path[path] = []
            courses_by_path[path].append(course_data)
        
        for path_name, path_courses in courses_by_path.items():
            with st.expander(f"📚 {path_name} - {len(path_courses)} cours", expanded=False):
                for course_data in path_courses:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                    with col1:
                        st.markdown(f"**{course_data['Cours']}**")
                    with col2:
                        st.markdown(f"⏱️ {course_data['Durée']}")
                    with col3:
                        st.markdown(f"📊 {course_data['Statut']}")
                    with col4:
                        if course_data['Lien'] != "N/A":
                            st.markdown(course_data['Lien'])
                        else:
                            st.markdown("N/A")
    else:
        st.info("Aucun cours trouvé.")

    # Liens rapides vers KodeKloud
    st.markdown("### 🔗 Liens KodeKloud")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[Learning Paths](https://kodekloud.com/learning-paths/)")
        st.markdown("[Site Reliability Engineer](https://kodekloud.com/learning-path/site-reliability-engineer/)")
        st.markdown("[DevOps Engineer](https://kodekloud.com/learning-path/devops-engineer/)")
    with col2:
        st.markdown("[Courses](https://kodekloud.com/courses/)")
        st.markdown("[Cloud Engineer](https://kodekloud.com/learning-path/cloud-engineer)")
        st.markdown("[AI Learning Path](https://kodekloud.com/learning-path/ai)")

with tab2:
    # Afficher le path global
    data = paths_data["global"]
    progress_data = load_progress()

    # Informations générales du path global
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"## {data['name']}")
        st.markdown(f"**Description:** {data['description']}")
        st.markdown(f"**Total cours:** {data['cours_total']} (regroupés depuis les 4 paths)")
        st.markdown("**Objectif:** Voir tous les cours disponibles et optimiser l'apprentissage")

    with col2:
        # Calcul de la progression globale
        courses = data.get("cours", [])
        total_courses = len(courses)
        completed_count = 0

        for course in courses:
            if isinstance(course, dict):
                course_title = course.get("titre", "")
                # Vérifier si complété dans n'importe quel path
                completion_status = get_course_completion_status(course_title, "global", progress_data)
                if completion_status["any_completed"]:
                    completed_count += 1

        progress_percentage = int((completed_count / total_courses) * 100) if total_courses > 0 else 0

        st.markdown("### 📊 Progression Globale")
        st.progress(progress_percentage / 100)
        st.markdown(f"**{completed_count}/{total_courses} cours**")
        st.markdown(f"**{progress_percentage}% terminé**")

    st.markdown("---")

    # Affichage par phases organisées
    st.markdown("## 📚 Organisation par Catégories")

    for phase in data.get("phases", []):
        phase_name = phase["nom"]
        phase_courses = phase["cours"]

        # Calculer la progression de la phase
        completed_in_phase = 0
        for course_title in phase_courses:
            completion_status = get_course_completion_status(course_title, "global", progress_data)
            if completion_status["any_completed"]:
                completed_in_phase += 1

        phase_progress = int((completed_in_phase / len(phase_courses)) * 100) if phase_courses else 0

        with st.expander(f"{phase_name} ({len(phase_courses)} cours) - {completed_in_phase} / {len(phase_courses)} : {phase_progress}%", expanded=False):
            for idx, course_title in enumerate(phase_courses):
                # Trouver le cours dans la liste complète
                course_obj = next((c for c in courses if (isinstance(c, dict) and c.get("titre") == course_title) or c == course_title), None)
                if course_obj:
                    # Vérifier le statut de completion dans tous les paths
                    completion_status = get_course_completion_status(course_title, "global", progress_data)

                    # Afficher avec mise en évidence si partagé
                    is_shared = isinstance(course_obj, dict) and course_obj.get("is_shared", False)
                    shared_with = isinstance(course_obj, dict) and course_obj.get("shared_with", [])

                    # Affichage compact pour le path global
                    with st.container():
                        col1, col2, col3, col4 = st.columns([0.08, 0.5, 0.25, 0.17])

                        with col1:
                            # Checkbox pour marquer comme fait (dans le contexte global)
                            new_completed = st.checkbox(
                                "Completed",
                                value=completion_status["any_completed"],
                                key=f"check_global_{phase_name}_{course_title}_{idx}",
                                label_visibility="hidden"
                            )
                            if new_completed != completion_status["any_completed"]:
                                # Marquer comme fait dans tous les paths où ce cours existe
                                for path_key in shared_with:
                                    update_course_progress(path_key, course_title, completed=new_completed)

                        with col2:
                            # Titre avec mise en évidence si partagé
                            if is_shared:
                                st.markdown(f"🔗 [{course_title}]({course_obj.get('lien', '#')})")
                                # Trouver les autres sections de la même spécialisation où ce cours apparaît
                                other_sections = []
                                for phase2 in data.get("phases", []):
                                    if phase2["nom"] != phase_name and course_title in phase2["cours"]:
                                        other_sections.append(phase2["nom"])
                                if shared_with or other_sections:
                                    legend = []
                                    if shared_with:
                                        legend.append(f"PARTAGÉ ({', '.join(shared_with)})")
                                    if other_sections:
                                        legend.append(f"Doublon dans: {', '.join(other_sections)}")
                                    st.caption(" | ".join(legend))
                                else:
                                    st.caption("PARTAGÉ")
                            else:
                                if course_obj.get("lien"):
                                    st.markdown(f"[{course_title}]({course_obj['lien']})")
                                else:
                                    st.markdown(f"{course_title}")

                        with col3:
                            # Informations compactes
                            info_parts = []
                            if isinstance(course_obj, dict) and course_obj.get("duree") and course_obj["duree"] != "TBD":
                                info_parts.append(f"⏱️ {course_obj['duree']}")
                            
                            if completion_status["other_completed"]:
                                info_parts.append(f"✅ {', '.join(completion_status['other_completed'])}")
                            
                            if info_parts:
                                st.caption(" • ".join(info_parts))

                        with col4:
                            # Afficher les paths où ce cours est disponible
                            if shared_with:
                                paths_display = ", ".join(shared_with[:2])  # Max 2 paths affichés
                                if len(shared_with) > 2:
                                    paths_display += f" +{len(shared_with)-2}"
                                st.caption(f"📁 {paths_display}")
                        if isinstance(course_obj, dict) and course_obj.get("lien"):
                            st.markdown(f"[🔗 Accéder]({course_obj['lien']})")

    # Section des cours communs
    st.markdown("---")
    st.markdown("## 🔗 Analyse des Cours Partagés")

    # Créer un tableau des cours partagés
    shared_courses_data = []
    for course in courses:
        if isinstance(course, dict) and course.get("is_shared", False):
            shared_with = course.get("shared_with", [])
            course_title = course.get("titre", "")
            completion_status = get_course_completion_status(course_title, "global", progress_data)

            shared_courses_data.append({
                "Cours": course_title,
                "Paths": len(shared_with),
                "Disponible dans": ", ".join(shared_with),
                "État": "✅ Fait" if completion_status["any_completed"] else "⏳ À faire",
                "Durée": course.get("duree", "N/A")
            })

    if shared_courses_data:
        st.markdown("### 📊 Cours Partagés (présents dans plusieurs paths)")
        shared_df = pd.DataFrame(shared_courses_data)
        st.dataframe(shared_df, use_container_width=True)

        # Statistiques
        total_shared = len(shared_courses_data)
        avg_paths = sum(item["Paths"] for item in shared_courses_data) / total_shared if total_shared > 0 else 0
        completed_shared = sum(1 for item in shared_courses_data if "✅ Fait" in item["État"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cours Partagés", f"{total_shared}")
        with col2:
            st.metric("Moyenne Paths/Cours", f"{avg_paths:.1f}")
        with col3:
            st.metric("Partagés Terminés", f"{completed_shared}/{total_shared}")
    else:
        st.info("Aucun cours partagé détecté.")

with tab3:
    st.header("📚 Parcours Spécialisés")

    # Sélection du path spécialisé
    specialized_paths = {k: v for k, v in paths_data.items() if k != "global"}
    path_options = list(specialized_paths.keys())
    selected_path = st.selectbox(
        "Choisir un path spécialisé pour voir les détails et suivre la progression",
        path_options,
        format_func=lambda x: specialized_paths[x]["name"],
        key="specialized_path_select"
    )

    if selected_path in specialized_paths:
        data = specialized_paths[selected_path]
        progress_data = load_progress()

        # Informations générales du parcours
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"## {data['name']}")
            st.markdown(f"**Description:** {data['description']}")
            st.markdown(f"**Durée:** {data['duree_mois']} mois | **Cours:** {data['cours_total']}")
            if 'salaires' in data and 'usd' in data['salaires']:
                st.markdown(f"**Salaire USD:** {data['salaires']['usd']}")
            st.markdown(f"**Salaires:** CHF {data['salaires'].get('chf', 'N/A')}, CAD {data['salaires'].get('cad', 'N/A')}")

        with col2:
            # Calcul de la progression
            courses = data.get("cours", [])
            total_courses = len(courses)
            completed_count = 0

            for course in courses:
                if isinstance(course, dict):
                    course_title = course.get("titre", "")
                    # Vérifier la progression avec la nouvelle structure
                    path_progress_data = progress_data.get(selected_path, [])
                    if isinstance(path_progress_data, list):
                        course_completed = any(
                            task.get("task") == course_title and task.get("done", False)
                            for task in path_progress_data
                            if isinstance(task, dict)
                        )
                    else:
                        # Fallback pour l'ancienne structure
                        course_completed = path_progress_data.get(course_title, {}).get("completed", False)

                    if course_completed:
                        completed_count += 1

            progress_percentage = int((completed_count / total_courses) * 100) if total_courses > 0 else 0

            st.markdown("### 📊 Progression")
            st.progress(progress_percentage / 100)
            st.markdown(f"**{completed_count}/{total_courses} cours**")
            st.markdown(f"**{progress_percentage}% terminé**")

        st.markdown("---")

        # Tableau des cours terminés pour cette spécialisation
        st.markdown("## ✅ Cours Terminés de cette Spécialisation")
        
        completed_courses_list = []
        for course in courses:
            course_title = course.get("titre", "")
            # Vérifier la progression avec la nouvelle structure
            path_progress_data = progress_data.get(selected_path, [])
            if isinstance(path_progress_data, list):
                course_completed = any(
                    task.get("task") == course_title and task.get("done", False)
                    for task in path_progress_data
                    if isinstance(task, dict)
                )
            else:
                # Fallback pour l'ancienne structure
                course_completed = path_progress_data.get(course_title, {}).get("completed", False)
            
            if course_completed:
                # Trouver la section/phase de ce cours
                phase_name = "Autre"
                for phase in data.get("phases", []):
                    if course_title in phase["cours"]:
                        phase_name = phase["nom"]
                        break
                
                completed_courses_list.append({
                    "cours_title": course_title,
                    "phase_name": phase_name,
                    "duree": course.get("duree", "TBD")
                })
        
        if completed_courses_list:
            st.markdown("### Décocher pour marquer comme incomplet:")
            for idx, course_info in enumerate(completed_courses_list):
                col1, col2, col3, col4 = st.columns([0.08, 0.55, 0.2, 0.17])
                
                with col1:
                    # Checkbox pour décocher
                    unchecked = st.checkbox(
                        "Marquer comme incomplet",
                        value=True,
                        key=f"completed_check_{selected_path}_{course_info['cours_title']}_{idx}",
                        label_visibility="hidden"
                    )
                    if not unchecked:
                        # L'utilisateur a décoché, donc marquer comme incomplet
                        update_course_progress(selected_path, course_info['cours_title'], completed=False)
                        st.rerun()
                
                with col2:
                    st.markdown(f"**{course_info['cours_title']}**")
                
                with col3:
                    st.caption(course_info['phase_name'])
                
                with col4:
                    st.caption(f"⏱️ {course_info['duree']}")
            
            st.caption(f"Total: {len(completed_courses_list)} cours terminés")
        else:
            st.info("Aucun cours terminé dans cette spécialisation pour le moment.")

        st.markdown("---")

        # Affichage des cours avec mise en évidence des partagés
        st.markdown("## ✅ Suivi de Progression Spécialisé")

        if courses and isinstance(courses[0], dict):
            # Créer une fonction pour vérifier si un cours est partagé
            def is_course_shared(course_title):
                for path_key, path_data in specialized_paths.items():
                    if path_key != selected_path:
                        path_courses = path_data.get("cours", [])
                        if any((isinstance(c, dict) and c.get("titre") == course_title) or c == course_title for c in path_courses):
                            return True
                return False

            # Affichage par phases
            for phase in data.get("phases", []):
                phase_name = phase["nom"]
                phase_courses = phase["cours"]

                # Calculer la progression de la phase
                completed_in_phase = 0
                for course_title in phase_courses:
                    course_obj = next((c for c in courses if c.get("titre") == course_title), None)
                    if course_obj:
                        # Récupérer la progression avec la nouvelle structure
                        path_progress_data = progress_data.get(selected_path, [])
                        if isinstance(path_progress_data, list):
                            course_progress = next(
                                (task for task in path_progress_data
                                 if isinstance(task, dict) and task.get("task") == course_title),
                                {}
                            )
                            if course_progress.get("done", False):
                                completed_in_phase += 1
                        else:
                            # Ancienne structure
                            course_progress = path_progress_data.get(course_title, {})
                            if course_progress.get("completed", False):
                                completed_in_phase += 1

                phase_progress = int((completed_in_phase / len(phase_courses)) * 100) if phase_courses else 0

                with st.expander(f"📚 {phase_name} ({len(phase_courses)} cours)", expanded=False):
                    for idx, course_title in enumerate(phase_courses):
                        # Afficher tous les doublons du cours dans la section
                        course_objs = [c for c in courses if c.get("titre") == course_title]
                        for obj_idx, course_obj in enumerate(course_objs):
                            # Récupérer la progression avec la nouvelle structure
                            path_progress_data = progress_data.get(selected_path, [])
                            if isinstance(path_progress_data, list):
                                course_progress = next(
                                    (task for task in path_progress_data
                                     if isinstance(task, dict) and task.get("task") == course_title),
                                    {}
                                )
                                completed = course_progress.get("done", False)
                                comment = ""  # Pas de commentaires dans la nouvelle structure
                            else:
                                # Ancienne structure
                                course_progress = path_progress_data.get(course_title, {})
                                completed = course_progress.get("completed", False)
                                comment = course_progress.get("comment", "")

                            # Synchroniser tous les doublons : si l'un est coché, tous le sont
                            # On regarde la progression globale du cours dans le path
                            # (déjà fait ci-dessus)

                            # Vérifier si partagé et déjà fait ailleurs
                            is_shared = is_course_shared(course_title)
                            completion_status = get_course_completion_status(course_title, selected_path, progress_data)

                            # Afficher chaque doublon de cours de manière compacte
                            with st.container():
                                col1, col2, col3 = st.columns([0.08, 0.65, 0.27])
                                with col1:
                                    new_completed = st.checkbox(
                                        "Completed",
                                        value=completed,
                                        key=f"check_{selected_path}_{phase_name}_{course_title}_{idx}_{obj_idx}",
                                        label_visibility="hidden"
                                    )
                                    if new_completed != completed:
                                        # Met à jour tous les doublons dans le path
                                        update_course_progress(selected_path, course_title, completed=new_completed)

                                with col2:
                                    # Affichage compact du titre et informations
                                    if is_shared:
                                        # Trouver tous les paths où ce cours existe
                                        shared_with = []
                                        for path_key, path_data in specialized_paths.items():
                                            if path_key != selected_path:
                                                path_courses = path_data.get("cours", [])
                                                if any((isinstance(c, dict) and get_base_title(c.get("titre", "")) == get_base_title(course_title)) or (isinstance(c, str) and get_base_title(c) == get_base_title(course_title)) for c in path_courses):
                                                    shared_with.append(path_data.get("name", path_key))
                                        # Trouver les autres sections de la même spécialisation où ce cours apparaît (en comparant les titres de base)
                                        other_sections = []
                                        base_title = get_base_title(course_title)
                                        for phase2 in data.get("phases", []):
                                            if phase2["nom"] != phase_name:
                                                for ct in phase2["cours"]:
                                                    if get_base_title(ct) == base_title:
                                                        other_sections.append(phase2["nom"])
                                                        break
                                        st.markdown(f"🔗 [{course_title}]({course_obj.get('lien', '#')})")
                                        if shared_with or other_sections:
                                            legend = []
                                            if shared_with:
                                                legend.append(f"PARTAGÉ ({', '.join(shared_with)})")
                                            if other_sections:
                                                legend.append(f"Doublon dans: {', '.join(other_sections)}")
                                            st.caption(" | ".join(legend))
                                        else:
                                            st.caption("PARTAGÉ")
                                    else:
                                        if course_obj.get("lien"):
                                            st.markdown(f"[{course_title}]({course_obj['lien']})")
                                        else:
                                            st.markdown(f"{course_title}")
                                    # Informations compactes sur une seule ligne
                                    info_parts = []
                                    if course_obj.get("duree") and course_obj["duree"] != "TBD":
                                        info_parts.append(f"⏱️ {course_obj['duree']}")
                                    if info_parts:
                                        st.caption(" • ".join(info_parts))

                                with col3:
                                    new_comment = st.text_input(
                                        "comment",
                                        value=comment,
                                        key=f"comment_{selected_path}_{course_title}_{obj_idx}",
                                        placeholder="💬",
                                        label_visibility="hidden"
                                    )
                                    if new_comment != comment:
                                        update_course_progress(selected_path, course_title, comment=new_comment)

            # Cours sans phases
            unassigned_courses = []
            assigned_courses = set()
            for phase in data.get("phases", []):
                assigned_courses.update(phase["cours"])

            for course in courses:
                course_title = course.get("titre", "")
                if course_title not in assigned_courses:
                    unassigned_courses.append(course)

            if unassigned_courses:
                # Calculer la progression des cours non assignés
                completed_unassigned = 0
                for course in unassigned_courses:
                    course_title = course.get("titre", "")
                    # Récupérer la progression avec la nouvelle structure
                    path_progress_data = progress_data.get(selected_path, [])
                    if isinstance(path_progress_data, list):
                        course_progress = next(
                            (task for task in path_progress_data
                             if isinstance(task, dict) and task.get("task") == course_title),
                            {}
                        )
                        if course_progress.get("done", False):
                            completed_unassigned += 1
                    else:
                        # Ancienne structure
                        course_progress = path_progress_data.get(course_title, {})
                        if course_progress.get("completed", False):
                            completed_unassigned += 1

                unassigned_progress = int((completed_unassigned / len(unassigned_courses)) * 100) if unassigned_courses else 0

                with st.expander(f"📚 Autres Cours Spécialisés ({len(unassigned_courses)} cours) - {completed_unassigned} / {len(unassigned_courses)} : {unassigned_progress}%", expanded=False):
                    for course in unassigned_courses:
                        course_title = course.get("titre", "")
                        # Récupérer la progression avec la nouvelle structure
                        path_progress_data = progress_data.get(selected_path, [])
                        if isinstance(path_progress_data, list):
                            course_progress = next(
                                (task for task in path_progress_data
                                 if isinstance(task, dict) and task.get("task") == course_title),
                                {}
                            )
                            completed = course_progress.get("done", False)
                            comment = ""  # Pas de commentaires dans la nouvelle structure
                        else:
                            # Ancienne structure
                            course_progress = path_progress_data.get(course_title, {})
                            completed = course_progress.get("completed", False)
                            comment = course_progress.get("comment", "")

                        is_shared = is_course_shared(course_title)
                        completion_status = get_course_completion_status(course_title, selected_path, progress_data)

                        # Affichage compact pour les cours hors phase
                        with st.container():
                            col1, col2, col3 = st.columns([0.08, 0.65, 0.27])

                            with col1:
                                new_completed = st.checkbox(
                                    "Completed",
                                    value=completed,
                                    key=f"check_{selected_path}_{course_title}_other",
                                    label_visibility="hidden"
                                )
                                if new_completed != completed:
                                    update_course_progress(selected_path, course_title, completed=new_completed)

                            with col2:
                                if is_shared:
                                    st.markdown(f"🔗 [{course_title}]({course.get('lien', '#')})")
                                    st.caption(f"📚 PARTAGÉ ({', '.join(completion_status['other_completed'])})", help=f"Ce cours est présent dans: {', '.join(completion_status['other_completed'])}" if completion_status['other_completed'] else "📚 PARTAGÉ")
                                else:
                                    if course.get("lien"):
                                        st.markdown(f"[{course_title}]({course['lien']})")
                                    else:
                                        st.markdown(f"{course_title}")

                                # Informations compactes
                                info_parts = []
                                if course.get("duree") and course["duree"] != "TBD":
                                    info_parts.append(f"⏱️ {course['duree']}")
                                
                                if info_parts:
                                    st.caption(" • ".join(info_parts))

                            with col3:
                                new_comment = st.text_input(
                                    "comment",
                                    value=comment,
                                    key=f"comment_{selected_path}_{course_title}_other",
                                    placeholder="💬",
                                    label_visibility="hidden"
                                )
                                if new_comment != comment:
                                    update_course_progress(selected_path, course_title, comment=new_comment)

        # Bouton d'export pour ce path
        st.markdown("---")
        if st.button(f"📥 Exporter progression {selected_path}"):
            prog = load_progress()
            st.download_button(
                label="Télécharger JSON",
                data=json.dumps(prog, ensure_ascii=False, indent=2),
                file_name=f"kodekloud_progress_{selected_path}.json"
            )

# Footer
st.markdown('---')
st.caption('Prototype — extraits automatiquement depuis les fichiers Markdown fournis. Améliorations possibles: parsing plus fin, filtres par durée, import/export CSV, authentification.')
