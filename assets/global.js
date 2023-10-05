function filefield_update_filename(form_id, name) {
  const fileInput = document.getElementById(`filefield-${form_id}-${name}`);
  const filename = fileInput.files[0].name;
  document.getElementById(`filefield-${form_id}-${name}-text`).textContent = filename;
}

async function change_language(url, csrf_token, code) {
  await fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrf_token,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `language=${code}`
  });
  location.reload();
}
