import streamlit as st
from bs4 import BeautifulSoup
import os
import json

# Define keywords
UNSUBSCRIBE_KEYWORDS = [
    'unsubscribe', 'optout', 'opt-out', 'remove', 'stop', 'preferences',
    'manage preferences', 'update preferences', 'change email preferences',
    'email settings', 'manage subscription', 'stop receiving emails',
    'stop notifications', 'leave mailing list', 'adjust preferences',
    'communication preferences', 'update communication settings',
    'manage my subscription', 'remove me from the list', 'update your profile',
    'end subscription', 'email opt-out', 'cancel subscription', 'pause emails',
    'change subscription options' ,  "manage your subscription settings" ," leave the list"
]

INVALID_HINTS = ['tracking', 'click', 'ad', 'promo', 'offer', 'spam', 'redirect']

# 🔹 Function to classify each link
def is_valid_unsubscribe_link(href, text):
    href = href.lower()
    text = text.lower()
    if any(kw in href for kw in INVALID_HINTS):
        return "Invalid"
    if any(kw in href for kw in UNSUBSCRIBE_KEYWORDS) or any(kw in text for kw in UNSUBSCRIBE_KEYWORDS):
        return "Unsubscribe"
    return "Valid"

# 🔹 Function to extract only valid links
def extract_links(html, filename):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    valid_links = []
    for link in links:
        href = link['href'].strip()
        text = link.get_text().strip()
        label = is_valid_unsubscribe_link(href, text)
        if label == "Valid":
            valid_links.append({
                'filename': filename,
                'text': text,
                'url': href,
                'label': label
            })
    return valid_links

# 🔹 Streamlit UI
st.title("Email Valid Link Extractor")

# Optional: Convert XML folder to JSON and process
convert_xml = st.checkbox("Convert folder of XML files to JSON")

if convert_xml:
    folder_path = st.text_input("Enter the path to the folder containing XML files")
    if folder_path and st.button("Convert to JSON and Extract Valid Links"):
        if os.path.isdir(folder_path):
            emails = []
            for filename in os.listdir(folder_path):
                if filename.endswith(".xml") or filename.endswith(".html"):
                    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                        content = f.read()
                        emails.append({'filename': filename, 'content': content})

            all_valid_links = []
            for email in emails:
                valid_links = extract_links(email['content'], email['filename'])
                all_valid_links.extend(valid_links)

            if all_valid_links:
                st.success("✅ Extracted valid links from XML folder!")
                st.write("### Valid Links")
                st.dataframe(all_valid_links)

                if st.button("Download Valid Links as JSON"):
                    st.download_button(
                        label="📄 Download JSON",
                        data=json.dumps(all_valid_links, indent=2),
                        file_name="valid_links.json",
                        mime="application/json"
                    )
            else:
                st.warning("No valid links found.")
        else:
            st.error("❌ Invalid folder path.")

# Divider
st.markdown("---")

# 🔹 Upload Files Section
uploaded_files = st.file_uploader("Upload XML/HTML/JSON files manually", type=["xml", "html", "json"], accept_multiple_files=True)

if uploaded_files:
    all_valid_links = []

    for uploaded_file in uploaded_files:
        content = uploaded_file.read().decode('utf-8')
        filename = uploaded_file.name

        if filename.endswith(".json"):
            try:
                data = json.loads(content)
                for email in data.get("emails", []):
                    valid_links = extract_links(email["content"], email.get("id", "unknown"))
                    all_valid_links.extend(valid_links)
            except Exception as e:
                st.error(f"Failed to parse JSON: {e}")
        else:
            valid_links = extract_links(content, filename)
            all_valid_links.extend(valid_links)

    if all_valid_links:
        st.success("✅ Extracted valid links!")
        st.write("### Valid Links")
        st.dataframe(all_valid_links)

        if st.button("Download Valid Links as JSON"):
            st.download_button(
                label="📄 Download JSON",
                data=json.dumps(all_valid_links, indent=2),
                file_name="valid_links.json",
                mime="application/json"
            )
    else:
        st.warning("No valid links found.")
