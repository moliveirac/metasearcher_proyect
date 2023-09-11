const addMoreBtn = $("#add_more");
const totalNewForms = document.getElementById("id_form-TOTAL_FORMS")

addMoreBtn.on('click', add_new_form)

function add_new_form(event) {
    if (event) {
        // Doesn't allows to submit events
        event.preventDefault()
    }
    const currentForms = document.getElementsByClassName("formset")
    const currentFormCount = Number(totalNewForms.value)
    const formCopyTarget = document.getElementById('form_set');
    const emptyFormEl = document.getElementById('empty-form').cloneNode(true);
    emptyFormEl.setAttribute('class', 'formset');
    emptyFormEl.setAttribute('id', `form-${currentFormCount}`);
    const regex = new RegExp('__prefix__', 'g')
    emptyFormEl.innerHTML = emptyFormEl.innerHTML.replace(regex, currentFormCount)

    // Adding required attr.
    const requiredField = emptyFormEl.querySelector('[name$="search_keywords"]');
    requiredField.setAttribute('required', '')

    totalNewForms.setAttribute('value', currentFormCount + 1)
    // Adding a new empty form
    formCopyTarget.append(emptyFormEl);
}

function delete_form(btn) {
    if (event) {
        // Doesn't allows to submit events
        event.preventDefault();
    }

    const formNode = btn.closest('.formset');
    // const formId = formNode.getAttribute('id');

    formNode.remove();

    const forms = document.querySelectorAll('.formset');
    for (let i = 0; i < forms.length; i++) {
        const formInputs = forms[i].querySelectorAll('input, select, textarea');
        for (let j = 0; j < formInputs.length; j++) {
            const oldName = formInputs[j].getAttribute('name');
            const newName = oldName.replace(/-\d+-/, `-${i}-`);
            formInputs[j].name = newName;
            const oldId = formInputs[j].getAttribute('id');
            const newId = oldId.replace(/_\d+_/g, `_${i}_`);
            formInputs[j].id = newId;
        }
        forms[i].setAttribute('id', `form-${i}`);
    }

    totalNewForms.setAttribute('value', totalNewForms.value - 1);
}