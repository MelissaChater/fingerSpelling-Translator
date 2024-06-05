# installazione delle librerie necessarie
!pip install --upgrade pip
!pip install mediapipe-model-maker
!pip install gdown

print("Librerie installate")

# importo le librerie richieste
from google.colab import files
import os
import tensorflow as tf
assert tf.__version__.startswith('2')
import gdown

from mediapipe_model_maker import gesture_recognizer
import matplotlib.pyplot as plt

print("Librerie importate")

# ottengo il dataSet da unn link google Drive
# SOSTITUIRE QUI IL LINK COL PROPRIO DATASET
google_drive_url = 'https://drive.google.com/file/d/1OQb-beLZsNxLWhYMKmy5q0FE5TvHmbC8/view?usp=sharing'

# Estraggo l'ID del file dal link
file_id = google_drive_url.split('/')[-2]

# Crea l'URL di download diretto
download_url = f'https://drive.google.com/uc?export=download&id={file_id}'

# Scarica il file
output = 'archivio.zip'
gdown.download(download_url, output, quiet=False)

print("Dataset scaricato")

#unzippo il file
!unzip -o archivio.zip -d myDataFolder

print("Dataset estratto")
print("Cartelle estratte:", os.listdir('myDataFolder'))

# Imposto il percorso del dataset
dataset_path = "myDataFolder/archivio"

# verifico che il dataset sia organizzato correttamente
labels = []
for i in os.listdir(dataset_path):
    if os.path.isdir(os.path.join(dataset_path, i)):
        labels.append(i)
print("Etichette trovate:", labels)

# traccio un paio di img di esempio per ogni gesto
NUM_EXAMPLES = 5

for label in labels:
    label_dir = os.path.join(dataset_path, label)
    example_filenames = os.listdir(label_dir)[:NUM_EXAMPLES]
    fig, axs = plt.subplots(1, NUM_EXAMPLES, figsize=(10, 2))
    for i in range(NUM_EXAMPLES):
        axs[i].imshow(plt.imread(os.path.join(label_dir, example_filenames[i])))
        axs[i].get_xaxis().set_visible(False)
        axs[i].get_yaxis().set_visible(False)
    fig.suptitle(f'Showing {NUM_EXAMPLES} examples for {label}')
    plt.show()
    plt.close(fig)

print("Esempi di immagini visualizzati")

#caricamento di tutti i dati (a questo punto il codice potrebbe bloccarsi anche per alcuni minuti)
print("Caricamento del dataset")
data = gesture_recognizer.Dataset.from_folder(
    dirname=dataset_path,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
)
print("Dataset caricato")

train_data, rest_data = data.split(0.8)
validation_data, test_data = rest_data.split(0.5)
print("Dataset suddiviso in training, validation e test")

#allenamento del modello
print("Inizio allenamento del modello")
hparams = gesture_recognizer.HParams(export_dir="exported_model")
options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)
print("Modello allenato")

#calcolo la perdita ed i miglioramenti stampandoli a video
print("Inizio valutazione del modello")
loss, acc = model.evaluate(test_data, batch_size=1)
print(f"Test loss: {loss}, Test accuracy: {acc}")

#esporto il modello in un file .task
print("Esportazione del modello")
model.export_model()
!ls exported_model
print("Modello esportato")

files.download('exported_model/gesture_recognizer.task')
print("File modello scaricato")