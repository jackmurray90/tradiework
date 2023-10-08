function filefield_update_filename(form_id, name) {
  const fileInput = document.getElementById(`filefield-${form_id}-${name}`);
  const filename = fileInput.files[0].name;
  document.getElementById(`filefield-${form_id}-${name}-text`).textContent = filename;
}

function getCsrfToken() {
  if (!document.cookie) {
    return null;
  }
  const cookies = document.cookie.split(';').map(c => c.trim()).filter(c => c.startsWith("csrftoken="));
  if (cookies.length === 0) {
    return null;
  }
  return decodeURIComponent(cookies[0].split('=')[1]);
}

window.onload = () => {
  for (const a of document.getElementsByTagName("a")) {
    if (a.getAttribute("data-post")) {
      a.addEventListener('click', () => {
        fetch(a.getAttribute("data-post"), {
          method: "POST",
          headers: {"X-CSRFToken": getCsrfToken()},
        }).then(response => {
          if (response.redirected) {
            window.location.href = response.url;
          } else {
            window.location.reload();
          }
        });
        return false;
      });
    }
  }
};
