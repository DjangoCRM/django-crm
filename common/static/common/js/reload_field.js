// reload fields:
// 'signature preview', 
// 'owner' & 'co-owner' (depends on 'department')
window.addEventListener('load', function() {
  const scr_tag = document.querySelector('script[id="id_reload_field_js"]')
  const url = scr_tag.getAttribute('data-request-url');
  // reload 'signature' field
  const signature_id = document.getElementById("id_signature");
  if (signature_id) {
    signature_id.addEventListener("change", sigFunction);
  }
  function sigFunction() {
    const signature = document.getElementsByClassName("form-row field-signature_preview");
    if (signature_id.value === '') {
      signature[0].firstElementChild.lastElementChild.innerHTML = ' ';
    } else {
    const request = new Request(
      url + "?signature=" + signature_id.value,
      {method: 'GET', mode: 'same-origin', headers: {'x-requested-with': 'XMLHttpRequest'}}
    );
    fetch(request).then((response) => response.text()).then((text) => {
      signature[0].firstElementChild.lastElementChild.innerHTML = text;
    });}
  }
  // reload 'owner' & 'co_owner' fields depends on 'department' field
  const department_id = document.getElementById("id_department");
  if (department_id) {
    department_id.addEventListener("change", depFunction);
  }
  function depFunction() {
    if (department_id.value !== '') {
    const request = new Request(
      url + "?department=" + department_id.value,
      {method: 'GET', mode: 'same-origin', headers: {'x-requested-with': 'XMLHttpRequest'}}
    );
    const owner = document.getElementById("id_owner");
    const co_owner = document.getElementById("id_co_owner");
    fetch(request)
    .then((response) => response.json())
    .then(data => {
      if (owner) {
        owner.innerHTML = '';
        for (const choice of data.choices) {
          const option = new Option(choice.label, choice.value);
          owner.add(option);
        }
      }
      if (co_owner) {co_owner[0].lastElementChild.innerHTML = '';}
    }).catch(error => {
      console.error('Error fetching dynamic choices:', error);
    });    
  }
}});
