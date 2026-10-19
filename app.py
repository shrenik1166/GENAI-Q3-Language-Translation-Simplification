import re
import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator, MyMemoryTranslator

st.set_page_config(page_title="Language Bridge | Q3", page_icon="🌐", layout="wide")

GLOSSARY = {
    "artificial intelligence": "Technology that helps computers perform tasks that usually require human intelligence.",
    "machine learning": "A method that enables computers to learn patterns from data.",
    "algorithm": "A set of steps used to solve a problem.",
    "data": "Information collected for analysis or use.",
    "dataset": "A collection of related information.",
    "neural network": "A computing model inspired by connections between brain cells.",
    "database": "An organized collection of information stored electronically.",
    "cloud computing": "Using computing services through the internet.",
    "cybersecurity": "The practice of protecting computers, networks and data from digital attacks.",
    "encryption": "Changing information into a protected form.",
    "programming": "Writing instructions that tell a computer what to do.",
    "software": "Programs and instructions used by a computer.",
    "hardware": "The physical parts of a computer.",
    "operating system": "Software that manages a computer and its applications.",
    "network": "Connected computers or devices that exchange information.",
    "internet": "A worldwide network connecting computers and devices.",
    "api": "A defined way for software applications to communicate.",
    "computer vision": "Technology that helps computers interpret images and videos.",
    "natural language processing": "Technology that helps computers process human language.",
    "deep learning": "A type of machine learning that uses multi-layered neural networks.",
    "robotics": "The field of designing and operating robots.",
    "statistics": "Methods for collecting, analyzing and interpreting data.",
    "research": "A systematic investigation of a topic or question.",
    "hypothesis": "A possible explanation that can be tested.",
    "experiment": "A test used to investigate a question or idea.",
    "analysis": "The process of examining information to understand it.",
    "renewable energy": "Energy from sources that naturally replenish.",
    "climate change": "Long-term changes in Earth's temperatures and weather patterns.",
    "biodiversity": "The variety of living organisms in an area or on Earth.",
    "agriculture": "The practice of growing crops and raising animals."
}

REPLACEMENTS = {
    "due to the fact that": "because", "in order to": "to",
    "a large number of": "many", "is capable of": "can",
    "has the ability to": "can", "subsequently": "later",
    "approximately": "about", "furthermore": "also", "moreover": "also",
    "therefore": "so", "utilize": "use", "utilizes": "uses",
    "utilized": "used", "demonstrate": "show", "demonstrates": "shows",
    "demonstrated": "showed", "commence": "begin", "commences": "begins",
    "terminate": "end", "obtain": "get", "numerous": "many",
    "individuals": "people", "individual": "person", "sufficient": "enough",
    "assistance": "help", "facilitate": "help", "methodology": "method",
    "objective": "goal", "purchase": "buy", "additional": "extra",
    "substantial": "large", "comprehend": "understand", "require": "need",
    "requires": "needs", "required": "needed", "commonly": "usually",
    "prior to": "before"
}

def simplify_text(text):
    simplified = text
    for original, replacement in sorted(REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(r"\b" + re.escape(original) + r"\b", re.IGNORECASE)
        simplified = pattern.sub(replacement, simplified)
    simplified = re.sub(r";\s*", ". ", simplified)
    return re.sub(r"\s+", " ", simplified).strip()

def generate_glossary(text, minimum_terms=5):
    lower_text = text.lower()
    found = []
    for term in sorted(GLOSSARY, key=len, reverse=True):
        if re.search(r"\b" + re.escape(term) + r"\b", lower_text):
            found.append(term)
    for term in GLOSSARY:
        if term not in found:
            found.append(term)
        if len(found) >= minimum_terms:
            break
    rows = []
    for term in found[:10]:
        present = bool(re.search(r"\b" + re.escape(term) + r"\b", lower_text))
        rows.append({
            "Technical Term": term.title(),
            "Simple Explanation": GLOSSARY[term],
            "Source": "Found in paragraph" if present else "Related glossary term"
        })
    return rows

def translate_to_marathi(text):
    """Try Google first, then MyMemory. Both require internet and may be rate-limited."""
    errors = []
    try:
        result = GoogleTranslator(source="en", target="mr").translate(text)
        if result and result.strip():
            return result.strip(), "Google Translate"
        errors.append("Google Translate returned an empty response.")
    except Exception as exc:
        errors.append(f"Google Translate: {exc}")

    # MyMemoryTranslator expects supported language names in this library version.
    try:
        result = MyMemoryTranslator(source="english", target="marathi").translate(text)
        if result and result.strip():
            return result.strip(), "MyMemory"
        errors.append("MyMemory returned an empty response.")
    except Exception as exc:
        errors.append(f"MyMemory: {exc}")

    raise RuntimeError("Both online translation attempts failed. " + " | ".join(errors))

st.title("🌐 Language Bridge")
st.subheader("AI-Powered Language Translation and Text Simplification")
st.write("Translate academic English into Marathi, simplify difficult English text, and explore technical vocabulary.")
st.info(
    "Online translation requires internet access and depends on third-party services. "
    "Simplification uses predefined Python rules, and the glossary uses a built-in collection; "
    "these features do not use a separate generative AI model."
)

with st.sidebar:
    st.header("About This Project")
    st.write("**Question:** Q3")
    st.write("**Translation:** English → Marathi")
    st.write("**Interface:** Streamlit")
    st.write("**Libraries:** deep-translator, pandas")
    st.write("**Features:** Translation, simplification, glossary and evaluation")

st.markdown("## 1. Enter an Academic Paragraph")
sample_text = (
    "Artificial intelligence is a branch of computer science that enables machines to perform "
    "tasks requiring human intelligence. Machine learning algorithms analyze data to identify "
    "patterns and improve predictions. These methods are used in healthcare, education, agriculture "
    "and many other fields."
)
academic_text = st.text_area(
    "Academic paragraph in English", value=sample_text, height=180, max_chars=5000,
    help="Enter an English paragraph of up to 5000 characters."
)

if st.button("Translate, Simplify and Analyze", type="primary"):
    text = academic_text.strip()
    if not text:
        st.error("Please enter an academic paragraph.")
    elif len(text) < 20:
        st.error("Please enter at least 20 characters for meaningful analysis.")
    else:
        st.session_state["original"] = text
        st.session_state["simplified"] = simplify_text(text)
        st.session_state["glossary"] = generate_glossary(text)
        st.session_state["marathi"] = ""
        st.session_state["provider"] = ""
        st.session_state["translation_ok"] = False
        try:
            with st.spinner("Trying online translation services..."):
                translated, provider = translate_to_marathi(text)
            st.session_state["marathi"] = translated
            st.session_state["provider"] = provider
            st.session_state["translation_ok"] = True
            st.success(f"Translation completed using {provider}.")
        except Exception as exc:
            st.error(
                "Online translation failed. Simplification and glossary are still available. "
                "Wait a while and try again; providers may enforce rate limits."
            )
            with st.expander("Technical error details"):
                st.code(str(exc))

if "original" in st.session_state:
    st.divider()
    st.header("2. Translation and Simplification Results")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Original English")
        st.write(st.session_state["original"])
    with col2:
        st.markdown("### Marathi Translation")
        if st.session_state.get("translation_ok") and st.session_state.get("marathi"):
            st.write(st.session_state["marathi"])
            st.caption("Translation provider: " + st.session_state["provider"])
        else:
            st.warning("Translation is unavailable. No fake translation is shown.")

    st.markdown("### Beginner-Friendly English")
    st.write(st.session_state["simplified"])

    translated_text = (
        st.session_state.get("marathi", "")
        if st.session_state.get("translation_ok")
        else "Translation unavailable. Please retry when an online service is available."
    )
    report = (
        "AI-POWERED LANGUAGE TRANSLATION AND TEXT SIMPLIFICATION\n\n"
        "ORIGINAL ENGLISH:\n" + st.session_state["original"] +
        "\n\nMARATHI TRANSLATION:\n" + translated_text +
        "\n\nSIMPLIFIED ENGLISH:\n" + st.session_state["simplified"] +
        "\n\nTECHNICAL GLOSSARY:\n"
    )
    for item in st.session_state["glossary"]:
        report += f"- {item['Technical Term']}: {item['Simple Explanation']} ({item['Source']})\n"

    st.download_button(
        "Download Results as TXT", data=report,
        file_name="Q3_translation_results.txt", mime="text/plain"
    )

    st.divider()
    st.header("3. Technical Glossary")
    st.dataframe(pd.DataFrame(st.session_state["glossary"]), use_container_width=True, hide_index=True)

    st.divider()
    st.header("4. Meaning, Accuracy and Completeness Evaluation")
    st.write("This is a manual evaluation checklist; the app does not automatically verify meaning.")
    if not st.session_state.get("translation_ok"):
        st.warning("Translation is unavailable. Retry it before evaluating its accuracy.")

    meaning = st.radio("Meaning: Is the main idea preserved?", ["Yes", "Partly", "No"], horizontal=True, key="meaning_assessment")
    accuracy = st.radio("Accuracy: Are facts and technical terms represented correctly?", ["Yes", "Partly", "No"], horizontal=True, key="accuracy_assessment")
    completeness = st.radio("Completeness: Are all important points included?", ["Yes", "Partly", "No"], horizontal=True, key="completeness_assessment")

    if st.button("Generate Evaluation Summary"):
        evaluation = pd.DataFrame([
            {"Criterion": "Meaning", "Assessment": meaning},
            {"Criterion": "Accuracy", "Assessment": accuracy},
            {"Criterion": "Completeness", "Assessment": completeness}
        ])
        st.dataframe(evaluation, use_container_width=True, hide_index=True)
        if not st.session_state.get("translation_ok"):
            st.warning("Translation is unavailable; its accuracy cannot be verified.")
        elif all(value == "Yes" for value in [meaning, accuracy, completeness]):
            st.success("Your manual review marked all three criteria as Yes. Human verification is still recommended.")
        else:
            st.warning("Some criteria need review. Compare the output with the original.")

st.divider()
st.caption("Q3 Practical Project | Python | Streamlit | deep-translator")
