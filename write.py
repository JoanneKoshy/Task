import streamlit as st
from openai import OpenAI
import statistics

# 🔑 Set your OpenAI API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Or hardcode: OpenAI(api_key="your-key")

st.set_page_config(page_title="IELTS Writing Evaluator", layout="wide")
st.title("IELTS Writing Band Score Evaluator")

# ✅ 5 Writing Tasks
writing_tasks = [
    "1. Some people think schools should group students according to academic ability, while others believe students of varying abilities should be taught together. Discuss both views and give your opinion.",
    "2. In many countries, plastic containers have become more common than ever. What problems do they cause, and how can we solve these problems?",
    "3. Some people believe that unpaid community service should be a compulsory part of high school programs. To what extent do you agree or disagree?",
    "4. Many people believe that formal 'pen and paper' exams are not the best method of assessing educational achievement. What is your view of examinations?",
    "5. Some believe that advances in technology are increasing the gap between rich and poor. Do you agree or disagree?"
]

user_responses = []
st.subheader("Answer the following 5 IELTS Writing Tasks:")

# Input fields
for idx, task in enumerate(writing_tasks):
    st.markdown(f"**{task}**")
    response = st.text_area(f"Your Answer for Task {idx + 1}", key=f"q{idx}")
    user_responses.append(response)

# 🧠 Function to call GPT for scoring
def evaluate_with_gpt(response):
    prompt = f"""
You are an IELTS examiner.Use the official IELTS Writing Task Band Desciptors. Evaluate the following IELTS writing task based on four criteria:

- Task Achievement
- Coherence and Cohesion
- Lexical Resource
- Grammatical Range and Accuracy

Give only the band scores from 0 to 9 for each. **Do not include explanations.**  
Return the result exactly in this format:

Task Achievement: [score]  
Coherence and Cohesion: [score]  
Lexical Resource: [score]  
Grammatical Range and Accuracy: [score]  




Response:
\"\"\"
{response}
\"\"\"
"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error evaluating response: {e}"

# 📤 Submit and Score
if st.button("Submit All"):
    st.success("Evaluating your responses... Please wait ⏳")

    all_scores = []
    all_outputs = []

    for i, response in enumerate(user_responses):
        if response.strip() == "":
            st.warning(f"❗ Task {i+1} response is empty. Skipping...")
            continue

        with st.spinner(f"Scoring Task {i+1}..."):
            result = evaluate_with_gpt(response)
            st.markdown(f"### Evaluation for Task {i+1}")
            st.markdown(result)
            all_outputs.append(result)

            # Extract scores from GPT response
            scores = []
            for line in result.splitlines():
                if ":" in line:
                    try:
                        score = float(line.split(":")[1].strip())
                        scores.append(score)
                    except:
                        pass
            if scores:
                all_scores.extend(scores)

    if all_scores:
        overall_band = round(statistics.mean(all_scores), 1)
        st.markdown(f"## Final IELTS Writing Band Score: **{overall_band}**")
    else:
        st.error("⚠️ No valid scores extracted. Please check your responses.")
