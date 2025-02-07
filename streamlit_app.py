import streamlit as st
import pandas as pd
from openai import OpenAI

# Show title and description.
st.title("📄 Bilingual Terms Extractor")
st.write(
    "Upload a bilingual English-German document below to extract relevant terms along with their corresponding German translations, organized into a structured table."
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
            "You are a professional linguistic analyst and your task is to extract relevant bilingual terms from a given set of Word documents into a CSV-formatted table."
            "There are several best practices, listed numerically, that you need to follow. Their order of precedence has nothing to do with priority, they are all equally important."
            "1. Extract bilingual terms from the provided bilingual document into a CSV-formatted table with the following columns:"
            "- English term"
            "- Term Language (default value: ENGLISH)"
            "- Number (singular/plural)"
            "- Gender (default value: neutral)"
            "- POS (NOUN/ADJ/VERB)"
            "- Editable by terminologist (default value: TRUE)"
            "- Translatable (default value: TRUE)"
            "- Description (leave blank)"
            "- German translation"
            "2. Extract both nouns and adjectives. Identify the word type of each term as either noun or adjective"
            "3. Extract compound words (e.g., ‘tax reduction measures’) as well as single words."
            "4. For nouns and adjectives, generate inflections:"
            "- if a singular form is extracted, also add its plural in a separate row right below the respective extracted term."
            "- if a plural form is extracted, also add its singular in a separate row right below the respective extracted term."
            "5. For nouns, also generate genitive forms:"
            "- add singular genitive form in a separate row right below the respective extracted term."
            "- add plural genitive form in a separate row right below the respective extracted term."
            "- Example: you extracted the term 'company', then generate the singular genitive ' company's ' and plural genitive ' companies' " 
            "6. Doublecheck that each term and its number are correct."
            "Example: if extracted term ‘window’ is labeled as 'Plural', change term to its actual plural form ‘windows’."
            "7. For terms with alternative spellings, generate all possible alternative spellings for them by adding a line below the respective extracted term."
            "Example: you extracted the term ‘chargeoff’, it has the alternative spelling ‘charge-off’, so you should also generate ‘charge-off’ in a separate row below the original term."
            "8. Ensure the output is strictly in CSV format with commas separating values."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Document: {document}"}
        ]
        
        # Generate response from OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        # Extract content from response
        extracted_text = response.choices[0].message.content.strip()
        
        # Convert extracted text into a DataFrame (assuming CSV format output)
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
