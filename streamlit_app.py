import streamlit as st
import pandas as pd
from openai import OpenAI

# Show title and description.
st.title("📄 Bilingual Terms Extractor")
st.write(
    "Upload an English-German (bilingual) document below to extract relevant terms bilingually into a structured table."
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
    
    # Let the user upload a file
    uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))
    
    if uploaded_file:
        # Read and decode the uploaded file
        document = uploaded_file.read().decode()
        
        # Define system message for structured extraction
        system_prompt = (
            "Extract bilingual terms from the provided bilingual document into a table with the following columns: "
            "Term (English), Term Language (English), Number (singular/plural), Gender (neutral), POS (NOUN/ADJ/VERB), "
            "Editable by terminologist (TRUE), Translatable (TRUE), Description (blank), Translation (German)."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Document: {document}"}
        ]
        
        # Generate response from OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # Extract content from response
        extracted_text = response.choices[0].message.content.strip()
        
        # Convert extracted text into a DataFrame (assuming CSV-like output)
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(extracted_text))
        except Exception as e:
            st.error("Failed to process extracted terms. Ensure the document is properly formatted.")
            st.stop()
        
        # Display extracted table
        st.write("### Extracted Bilingual Terms")
        st.dataframe(df)
        
        # Allow downloading as CSV
        csv = df.to_csv(index=False)
        st.download_button("Download Extracted Terms", csv, "bilingual_terms.csv", "text/csv")