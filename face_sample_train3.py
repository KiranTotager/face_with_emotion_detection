# import os
# import json
# from deepface import DeepFace
# import numpy as np

# # Directory where face data is stored
# face_data_dir = "FaceData"

# # Function to generate and store embeddings for each person
# def generate_embeddings():
#     embeddings = {}  # Dictionary to store embeddings for each person

#     # Loop through each person's subdirectory in FaceData
#     for person_name in os.listdir(face_data_dir):
#         person_dir = os.path.join(face_data_dir, person_name)
        
#         if os.path.isdir(person_dir):
#             # Generate embeddings for each image of the person
#             person_embeddings = []
            
#             for file_name in os.listdir(person_dir):
#                 if file_name.endswith(('.jpg', '.jpeg', '.png')):  # Image file extensions
#                     image_path = os.path.join(person_dir, file_name)
#                     # Use DeepFace to generate embeddings
#                     try:
#                         representation = DeepFace.represent(image_path, model_name="Facenet", enforce_detection=False)
#                         person_embeddings.append(representation[0]['embedding'])
#                     except Exception as e:
#                         print(f"Error processing {image_path}: {e}")
            
#             # Store embeddings for the person (keyed by person name)
#             embeddings[person_name] = np.array(person_embeddings).tolist()  # Convert numpy array to list for easy saving

#     # Save embeddings to a JSON file (you could also use HDF5 for large datasets)
#     with open("face_embeddings.json", "w") as f:
#         json.dump(embeddings, f)

#     print("Embeddings generated and saved successfully.")

# # Generate embeddings
# generate_embeddings()


import os
import json
from deepface import DeepFace
import numpy as np

# Directory where face data is stored
face_data_dir = "FaceData"
embedding_file = "face_embeddings.json"

# Function to generate and store embeddings for each person
def generate_embeddings():
    # Load existing embeddings if they exist
    if os.path.exists(embedding_file):
        with open(embedding_file, "r") as f:
            embeddings = json.load(f)
    else:
        embeddings = {}  # Start with an empty dictionary if no existing file

    # Loop through each person's subdirectory in FaceData
    for person_name in os.listdir(face_data_dir):
        person_dir = os.path.join(face_data_dir, person_name)

        if os.path.isdir(person_dir):
            # Check if embeddings for this person already exist
            if person_name in embeddings:
                print(f"Embeddings already exist for {person_name}. Skipping.")
                continue  # Skip if already processed
            
            # Generate embeddings for each image of the person
            person_embeddings = []
            
            for file_name in os.listdir(person_dir):
                if file_name.endswith(('.jpg', '.jpeg', '.png')):  # Image file extensions
                    image_path = os.path.join(person_dir, file_name)
                    # Use DeepFace to generate embeddings
                    try:
                        representation = DeepFace.represent(image_path, model_name="Facenet", enforce_detection=False)
                        person_embeddings.append(representation[0]['embedding'])
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")
            
            # Store embeddings for the person (keyed by person name)
            embeddings[person_name] = np.array(person_embeddings).tolist()  # Convert numpy array to list for easy saving
            print(f"Embeddings generated for {person_name}.")

    # Save embeddings to a JSON file
    with open(embedding_file, "w") as f:
        json.dump(embeddings, f)

    print("Embeddings generated and saved successfully.")

# Generate embeddings
generate_embeddings()
