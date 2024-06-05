# RAFT - Real-time Automated Fingerspelling Translator

Questo codice permette l'avvio di un'intelligenza artificiale
che riconosce l'alfabeto dattilologico.  
Il progetto include anche un'interfaccia web.  
Il codice è specifico per un raspberry.

Prima dell'avvio del programma creare un ambiente
virtuale python
```bash 
python -m venv myenv
```
dove "myenv" è il nome che si vuole dare all'ambiente
virtuale  
entrare nell'ambiente virtuale con
```bash 
source myenv/bin/activate
```
installare le librerie necessarie all'interno dell'ambiente
```bash
pip install flask
pip install mediaPipe
pip install cv2
```
far paritire il programma con
```bash
flask run --host=0.0.0.0
```