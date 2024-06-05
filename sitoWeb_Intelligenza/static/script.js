//funzione che si occupa di fare l'animazione iniziale del sito e di rendere visibile il main e l'heder principali
document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById('container');
    const logoImg = document.querySelector('.logo img');

    setTimeout(function() {
        // Aggiungi la classe che applica l'animazione
        logoImg.classList.add('expand');

        // Nascondi tutto il contenitore dopo l'animazione
        logoImg.addEventListener('transitionend', function() {
            container.style.transition = "all 0.5s ease-out";
            container.style.opacity = "0";
            container.addEventListener('transitionend', function() {
                container.style.display = "none";
                document.getElementById('second-header').style.display = "block";
                document.getElementById('second-main').style.display = "block";
            }, { once: true });
        }, { once: true });
    }, 500); // Avvia l'animazione dopo mezzo second0
});

//funzione che permette di scaricare il contenuto della casella di testo
function downloadText() {
    let x = new XMLHttpRequest();

    //richiesta di apertura alla route
    x.open('GET', '/dht', true);

    x.onload = function () {
        if (x.status === 200) {
            const text = x.responseText;//salva ciò che il python le invia nella variabile text
            const blob = new Blob([text], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'testo.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            console.error('Errore durante il download del testo: ' + x.statusText);
        }
    };

    x.onerror = function () {
        console.error('Errore di rete');
    };

    x.send();
}


document.getElementById('option-select').addEventListener('change', function() {
    const selectedOption = this.value;
    console.log('Opzione selezionata:', selectedOption);
});

//funzione che aggiorna il contenuto del testo con le informazioni dategli dal python
function updateGauges(){
    let x=new XMLHttpRequest()
    x.onload=function(){
        try{
            document.getElementById("valore").innerText=x.responseText //salva ciò che il python le invia nella variabile text
        }catch(e){
            document.getElementById("valore").innerText="Errore"
        }
    }
    x.open("GET","/dht")
    x.send()
}

setInterval(updateGauges,3000)
