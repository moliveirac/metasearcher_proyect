const exampleModal = document.getElementById('exampleModal')
if (exampleModal) {
    exampleModal.addEventListener('show.bs.modal', event => {
        console.log("hola?")
        // Button that triggered the modal
        const button = event.relatedTarget
        // Extract info from data-bs-* attributes
        const queryPK = button.getAttribute('data-bs-del-href')
        console.log(queryPK)

        // Update the modal's content.
        const modalFooterButton = exampleModal.querySelector('.modal-footer a')

        modalFooterButton.setAttribute("href", queryPK)
    })
}