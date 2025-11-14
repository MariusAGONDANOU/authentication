import os

OUTPUT = "authentication.txt"

# Dossiers à exclure
EXCLUDED_DIRS = {
    "venv", "__pycache__", ".git", "node_modules",
    "staticfiles", "media", "migrations"
}

# Extensions de fichiers à exclure
EXCLUDED_EXT = {
    ".pyc", ".sqlite3", ".db", ".log"
}

def should_skip(file_path):
    # Exclure par extension
    _, ext = os.path.splitext(file_path)
    if ext in EXCLUDED_EXT:
        return True
    return False

with open(OUTPUT, "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk("."):
        # Exclure les dossiers inutiles
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            full_path = os.path.join(root, file)

            # Vérifier si on doit sauter le fichier
            if should_skip(full_path):
                continue

            out.write("\n\n" + "="*80 + "\n")
            out.write(f"FILE: {full_path}\n")
            out.write("="*80 + "\n\n")

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"[ERREUR LECTURE FICHIER: {e}]\n")

print(f"✅ Export terminé ! Le fichier généré est : {OUTPUT}")
