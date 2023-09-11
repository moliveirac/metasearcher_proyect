var http_request = false;
        
function makeRequest(url) {

    http_request = false;

    if (window.XMLHttpRequest) { // Mozilla, Safari,...
        http_request = new XMLHttpRequest();
        if (http_request.overrideMimeType) {
            http_request.overrideMimeType('text/xml');
            // Ver nota sobre esta linea al final
        }
    } else if (window.ActiveXObject) { // IE
        try {
            http_request = new ActiveXObject("Msxml2.XMLHTTP");
        } catch (e) {
            try {
                http_request = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) {}
        }
    }

    if (!http_request) {
        alert('Falla :( No es posible crear una instancia XMLHTTP');
        return false;
    }
    http_request.onreadystatechange = alertContents;
    http_request.open('GET', url, true);
    http_request.send();

}

function updateObjectWithResponse(response) {
    // Aquí puedes realizar las operaciones necesarias para actualizar el objeto HTML
    // con la respuesta de la petición
    var html_p = document.getElementById("makeRequestObject").parentNode
    var obj = html_p.parentNode;

    obj.removeChild(html_p)

    obj.innerHTML += response;
}

function alertContents() {

    if (http_request.readyState == 4) {
        if (http_request.status == 200) {
            updateObjectWithResponse(http_request.responseText);
        } else {
            alert('Hubo problemas con la petición.');
        }
    }

}