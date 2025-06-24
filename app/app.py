import streamlit as st
from io import StringIO
import difflib
from docx import Document

st.set_page_config(page_title="Contract Comparator")

st.title("Contract Comparator")

st.markdown(
    """Upload one reference contract and up to 20 documents to compare.\n"
    "Results are shown in a grid where each cell links to the specific clause text."""
)


def read_file(upload):
    if upload.name.endswith(".docx"):
        doc = Document(upload)
        return "\n".join([p.text for p in doc.paragraphs])
    content = StringIO(upload.getvalue().decode("utf-8")).read()
    return content

reference_upload = st.file_uploader("Reference contract", type=["txt", "docx"], key="ref")

other_uploads = st.file_uploader(
    "Documents to compare (max 20)",
    type=["txt", "docx"],
    accept_multiple_files=True,
    key="docs",
)

if reference_upload and other_uploads:
    ref_text = read_file(reference_upload)
    ref_clauses = [c.strip() for c in ref_text.split("\n") if c.strip()]

    results = []
    for upload in other_uploads[:20]:
        doc_text = read_file(upload)
        doc_clauses = [c.strip() for c in doc_text.split("\n") if c.strip()]
        max_len = max(len(ref_clauses), len(doc_clauses))
        summary = []
        for i in range(max_len):
            ref_clause = ref_clauses[i] if i < len(ref_clauses) else ""
            doc_clause = doc_clauses[i] if i < len(doc_clauses) else ""
            diff = difflib.SequenceMatcher(None, ref_clause, doc_clause)
            ratio = diff.ratio()
            summary.append(ratio)
        results.append({"name": upload.name, "ratios": summary, "clauses": doc_clauses})

    num_clauses = max(len(r["ratios"]) for r in results)
    header = [f"Clause {i+1}" for i in range(num_clauses)]

    grid = {}
    for r in results:
        row = []
        for ratio in r["ratios"]:
            row.append(f"{ratio:.2f}")
        # pad
        for _ in range(num_clauses - len(row)):
            row.append("")
        grid[r["name"]] = row
    st.subheader("Similarity ratios")
    st.dataframe(grid)

    st.subheader("Clause details")
    for idx in range(num_clauses):
        with st.expander(f"Clause {idx+1}"):
            st.write("**Reference**")
            ref_clause = ref_clauses[idx] if idx < len(ref_clauses) else ""
            st.write(ref_clause)
            for r in results:
                clause = r["clauses"][idx] if idx < len(r["clauses"]) else ""
                st.write(f"**{r['name']}**")
                st.write(clause)
