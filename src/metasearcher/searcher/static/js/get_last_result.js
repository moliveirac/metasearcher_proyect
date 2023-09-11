let inProgress = false;
let closeWErrorButton = document.getElementById('close_w_error_btn')


async function replaceContentWithHTML(url, elementoID) {
    try {
        const controller = new AbortController();
        const signal = controller.signal;

        const timeoutId = setTimeout(() => {
            controller.abort();
        }, 10000); // Tiempo de espera de 5 segundos

        const response = await fetch(url, { signal });

        clearTimeout(timeoutId); // Limpiar el temporizador si la solicitud se resuelve antes del tiempo de espera

        if (!response.ok) {
            throw new Error('Request failed.');
        }

        const html = await response.text();
        const elemento = document.getElementById(elementoID);

        if (!elemento) {
            throw new Error(`Element with ID "${elementoID}" was not founded.`);
        }

        elemento.parentElement.innerHTML = html;
    } catch (error) {
        if (error.name === 'AbortError') {
            const errorMessage = `
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Do you want to stay up-to-date with this query?</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="spinner-id">
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        There was an error, please try again!
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="close_w_error_btn">Close</button>
                </div>
            `

            const elemento = document.getElementById(elementoID);
            elemento.parentElement.innerHTML = errorMessage;
            closeWErrorButton = document.getElementById('close_w_error_btn')
            
            closeWErrorButton.addEventListener('click', () => {
                oldHTML = `
                    <div class="modal-header">
                        <h1 class="modal-title fs-5" id="exampleModalLabel">Do you want to stay up-to-date with this query?</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="spinner-id">
                        <strong>Query:</strong> {{ query }}<br>
                        <strong>From:</strong> {{ searcher.searcher.value }}<br>
                        <div class="d-flex justify-content-center">
                            <div class="spinner-border spinner-border-sm" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    </div>
                `
                closeWErrorButton.parentElement.parentElement.innerHTML = oldHTML;
            })
        }
        console.error('There was an error:', error.message);
        inProgress = false;
        
    }
}

function fixedEncodeURIComponent(str) {
    return encodeURIComponent(str).replace(/[!'()*]/g, function(c) {
        return '%' + c.charCodeAt(0).toString(16);
    });
}

const notifyButton = document.getElementById('notify_button');
const spinnerID = 'spinner-id';

notifyButton.addEventListener('click', () => {
    if (!inProgress) {
        inProgress = true;
        const query = fixedEncodeURIComponent(notifyButton.getAttribute('data-query'))
        const source = notifyButton.getAttribute('data-source')
        let url = notifyButton.getAttribute('data-url') + '?query=' + query + '&source=' + source
        replaceContentWithHTML(url, spinnerID);
    }
});


