function filefield_update_filename(form_id, name) {
  const fileInput = document.getElementById(`filefield-${form_id}-${name}`);
  const filename = fileInput.files[0].name;
  document.getElementById(`filefield-${form_id}-${name}-text`).textContent = filename;
}
