import streamlit as st
from pathlib import Path
import google.generativeai as genai


api = 'AIzaSyAJvyI8VLdVlkaMoeNw4nSWt253zpLWbgw'

# configure genai with api key

genai.configure(api_key= api)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 4096,
  "response_mime_type": "text/plain",
}

# model configuration

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)  # I can add safety settings

system_prompt = """

As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a renowned hospital. Your expertise is crucial in identifying anomalies, diseases, or other health issues present in the images. By providing accurate and detailed interpretations, you play a vital role in ensuring precise diagnoses and contributing to the highest standard of patient care.

Your responsibilities include:

1. Detailed Analysis: Thoroughly analyze each image, focusing on identifying any abnormal findings.
2. Findings Report: Document all observed anomalies or signs of disease, clearly articulating these findings in a structured format.
3. Recommendations and Next Steps: Based on your analysis, suggest potential next steps, including further tests or treatments as applicable.
4. Treatment Suggestions: If appropriate, recommend possible treatment options or interventions to support patient care.

Important Notes:
1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Image: In cases where the image quality impedes clear analysis, note that certain aspects are "unable to be determined based on the provided image."
3. Disclaimer: Accompany your analysis with the disclaimer: "Consult with a doctor before making any decisions."
4. Clinical Value: Your insights are invaluable in guiding clinical decisions. Please proceed with the analysis adhering to the structured approach outlined above.

Please provide me an output response with these 4 headings and try to sumarize as much as possible and only mention your resposne to the illness and no start with this: Certainly! Here's a structured analysis of the provided image, adhering to your guidelines.
and ensure to show the disclaimer that is very important

"""

st.set_page_config(page_title="VitalImage Analysis" , page_icon=":robot:")

#set the logo

#st.image('skillcurb-logo.png', width=150)

#set the title
st.title('🧑 VITAL ❤️ Image 📷 Analytics 📊 👩‍⚕️')

st.subheader('An application that can help users to identify medical images')
uploaded_file = st.file_uploader('Upload the medical image for analysis', type = ['png', 'jpg','jpeg'])
if uploaded_file:
    st.image(uploaded_file , width= 250 , caption = 'Uploaded Medical Image')

submit_button = st.button('Generate the Analysis')

if submit_button:
    image_data = uploaded_file.getvalue()
   

    # making our image ready
    image_parts = [ 
        {
            'mime_type': 'image/jpeg',
            'data': image_data
        },
    ]

    #making our prompt ready
    prompt_parts = [ 

        image_parts[0],
        system_prompt,

    ]
    # generate a responde based on prompt and image
    st.title('Here is the analysis based on your image')
    response = model.generate_content(prompt_parts)
    st.write(response.text)
