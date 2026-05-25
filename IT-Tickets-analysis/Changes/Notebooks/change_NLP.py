# NLP for cause of changes based on short descriptions

# Import libraries
import os
import polars as pl  
import spacy 
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# Start Spacy language model
nlp = spacy.blank("en")  # Create a blank SpaCy model

# Define stopwords manually
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

# Filepath for input CSV file
filepath = r"synthetic_changes_data_2025.csv"

# Check if the file exists
if os.path.exists(filepath):
    df = pl.read_csv(filepath)
    # Check if required column exists
    if "Short Description" not in df.columns:
        print("Error: Missing required column 'Short Description'.")
        exit()
else:
    print(f"Error: File not found at path {filepath}.")
    exit()

# Convert 'Short Description' column to a list
short_descriptions = df["Short Description"].to_list()

# Preprocess text manually with SpaCy
preprocessed_descriptions = []
for text in short_descriptions:
    # Convert text to lowercase and tokenize
    doc = nlp.make_doc(text.lower())  # Tokenize the text
    # Filter tokens based on criteria: stopwords, short words (<3 characters), and non-alphabetic tokens
    filtered_words = [
        token.text for token in doc
        if token.text not in CUSTOM_STOPWORDS and len(token.text) > 2 and token.is_alpha
    ]
    # Join filtered tokens and add to preprocessed descriptions
    preprocessed_descriptions.append(" ".join(filtered_words))

# Split dataset into training and testing sets
X_train, X_test = train_test_split(preprocessed_descriptions, test_size=0.2, random_state=42)
print("Training set size:", len(X_train))
print("Testing set size:", len(X_test))

# Extract bigrams using CountVectorizer
vectorizer = CountVectorizer(ngram_range=(2, 2))  # Bigrams extraction
X_train_bigrams = vectorizer.fit_transform(X_train)  # Fit and transform training data
X_test_bigrams = vectorizer.transform(X_test)  # Transform testing data

# Get bigrams and corresponding frequencies
bigram_features = vectorizer.get_feature_names_out()  # Extract bigram features
bigram_freq_train = X_train_bigrams.sum(axis=0).tolist()[0]  # Count frequencies of bigrams in training data

# Combine bigrams with their frequencies
bigram_frequency = list(zip(bigram_features, bigram_freq_train))

# Sort bigrams by frequency in descending order
sorted_bigrams = sorted(bigram_frequency, key=lambda x: x[1], reverse=True)

# Display the top 10 bigrams with their frequencies
print("\nTop 10 most frequent bigrams:")
for bigram, count in sorted_bigrams[:10]:
    print(f"{bigram}: {count}")
    

#saving data into dataframe and then to csv file
# Convert bigram frequency data into a Polars DataFrame
bigram_df = pl.DataFrame({
    "words": [bigram for bigram, count in sorted_bigrams],  # Extract bigram phrases
    "amount": [count for bigram, count in sorted_bigrams]   # Extract counts of bigrams
})

# Save the Polars DataFrame to a CSV file
result_filepath = r"change__nlp.csv"
try:
    bigram_df.write_csv(result_filepath)
    print(f"Bigram frequency table successfully saved to {result_filepath}")
except Exception as e:
    print(f"Error while saving the CSV file: {e}")
    
