#NLP SCAPY. ===performing NLP on Short Description 
#It can answer the questions about common text patterns in Short Description column about incidents 
# Import libraries
import os
import polars as pl
import spacy  # SpaCy for text preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# Initialize a blank SpaCy language model
nlp = spacy.blank("en")  # This creates a lightweight blank English model with no preloaded data

# Define stopwords manually (common English stopwords)
CUSTOM_STOPWORDS = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'could', 'did', 'do',
    'does', 'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having',
    'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it',
    'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on',
    'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', 'she',
    'should', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then',
    'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'won', 'would', 'you', 'your',
    'yours', 'yourself', 'yourselves'
]

# File path for your CSV data
file_path = r"C:\Users\X\Downloads\synthetic_cybersecurity_bank_data.csv"    #input instead of X your user profile, your ID

# Step 1: Load and validate the data
if os.path.exists(file_path):  # Check if the file exists
    df = pl.read_csv(file_path)  # Load the dataset using Polars
    # Validate that the required column exists
    if "Short Description" not in df.columns:
        print("Error: Missing required column 'Short Description'.")
        exit()
else:
    print(f"Error: File not found at path {file_path}.")
    exit()

# Convert `Short description` column to a list for compatibility
short_descriptions = df["Short Description"].to_list()

# Step 2: Preprocessing text using SpaCy without "en_core_web_sm"
def preprocess_text_spacy(text):
    """
    Preprocess text using a blank SpaCy model:
    - Tokenizes text
    - Removes stopwords, punctuations, and short words (<= 2 letters)
    - Manages everything manually since there's no preloaded data
    """
    doc = nlp.make_doc(text.lower())  # Tokenize the text using the blank model
    filtered_words = [
        token.text for token in doc 
        if token.text not in CUSTOM_STOPWORDS and len(token.text) > 2 and token.is_alpha
    ]  # Remove stopwords, short words, and non-alphabetic tokens
    return " ".join(filtered_words)  # Return preprocessed text as a single string


# Preprocess the entire dataset
preprocessed_descriptions = [preprocess_text_spacy(desc) for desc in short_descriptions]

# Step 3: Split the dataset into train and test
X_train, X_test = train_test_split(preprocessed_descriptions, test_size=0.2, random_state=42)

print("Training Set Size:", len(X_train))
print("Testing Set Size:", len(X_test))

# Step 4: Use CountVectorizer for bigram extraction (words extraction)
vectorizer = CountVectorizer(ngram_range=(2, 2))  # Extract bigrams
X_train_bigrams = vectorizer.fit_transform(X_train)  # Fit and transform on training data
X_test_bigrams = vectorizer.transform(X_test)  # Transform on testing data

# Step 5: Get and display extracted bigram features
bigram_features = vectorizer.get_feature_names_out()
print(f"Number of bigram features: {len(bigram_features)}")
print(f"Sample bigrams: {bigram_features[:10]}")

# Step 6: Analyze bigram frequencies
bigram_freq_train = X_train_bigrams.sum(axis=0).tolist()[0]

# Pair the counts with their corresponding bigram features
bigram_frequency = list(zip(bigram_features, bigram_freq_train))

# Sort bigrams by frequency
sorted_bigrams = sorted(bigram_frequency, key=lambda x: x[1], reverse=True)

# Display the top 10 most frequent bigrams
print("\nTop 10 Most Frequent Bigrams:")
for bigram, count in sorted_bigrams[:10]:

    print(f"{bigram}: {count}")


# Save the Polars DataFrame to a CSV file
result_filepath = r"cyber_data_nlp.csv"
try:
    bigram_df.write_csv(result_filepath)
    print(f"Bigram frequency table successfully saved to {result_filepath}")
except Exception as e:
    print(f"Error while saving the CSV file: {e}")

