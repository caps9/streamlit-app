"""Start: python -m streamlit run app.py"""

import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


WEBSITES = Path(__file__).resolve().parent / "websites"
PAGE_HEIGHT = 900
# Click-Dummy: Die eingebetteten Websites sind reine 1-Pager-Deko.
# Kein Link navigiert irgendwohin, kein Formular wird abgeschickt –
# Hover-Animationen bleiben erhalten (daher bewusst kein pointer-events: none).
NAV_GUARD = """
<script>
(function () {
  function kill(event) { event.preventDefault(); event.stopPropagation(); }
  document.addEventListener('click', function (event) {
    var link = event.target.closest ? event.target.closest('a[href]') : null;
    if (link) { kill(event); }
  }, true);
  document.addEventListener('auxclick', function (event) {
    var link = event.target.closest ? event.target.closest('a[href]') : null;
    if (link) { kill(event); }
  }, true);
  document.addEventListener('submit', function (event) { kill(event); }, true);
})();
</script>
"""
st.set_page_config(page_title="Schulung", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """<style>
    header[data-testid="stHeader"], #MainMenu, footer {display: none;}
    .block-container {padding: 1rem 1.5rem 0; max-width: 100%;}
    </style>""",
    unsafe_allow_html=True,
)


website_folders = sorted(
    (folder for folder in WEBSITES.iterdir() if folder.is_dir()),
    key=lambda folder: [
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in re.split(r"(\d+)", folder.name)
    ],
)
pages = [folder / "index.html" for folder in website_folders if (folder / "index.html").is_file()]
if not pages:
    st.info("Lege deine erste Website unter websites/<name>/index.html ab und lade diese App neu.")
    st.stop()

page_names = [page.parent.name for page in pages]
if st.session_state.get("selected_website") not in page_names:
    st.session_state.selected_website = page_names[0]


def select_page(folder_name: str):
    st.session_state.selected_website = folder_name


# Ein Button pro Unterordner in websites/, beschriftet mit dem Ordnernamen.
columns_per_row = max(len(pages), 1)
for offset in range(0, len(pages), columns_per_row):
    columns = st.columns(columns_per_row)
    for index, page in enumerate(pages[offset : offset + columns_per_row], start=offset):
        with columns[index - offset]:
            folder_name = page.parent.name
            st.button(
                folder_name,
                key=f"website_{folder_name}",
                type="primary" if folder_name == st.session_state.selected_website else "secondary",
                use_container_width=True,
                on_click=select_page,
                args=(folder_name,),
            )

selected = pages[page_names.index(st.session_state.selected_website)]
try:
    document = selected.read_text(encoding="utf-8-sig")
except (OSError, UnicodeError) as error:
    st.error(f"Die HTML-Datei konnte nicht gelesen werden: {error}")
    st.stop()

if re.search(r"</body\s*>", document, re.IGNORECASE):
    document = re.sub(r"</body\s*>", NAV_GUARD + "\n</body>", document, count=1, flags=re.IGNORECASE)
else:
    document += NAV_GUARD

components.html(document, height=PAGE_HEIGHT, scrolling=True)