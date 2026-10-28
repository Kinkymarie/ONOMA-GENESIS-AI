async function api(path, options = {}) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || response.statusText);
  }
  return body;
}

document.querySelector("#send").addEventListener("click", async () => {
  const answer = document.querySelector("#answer");
  answer.textContent = "Planning and routing…";
  try {
    const result = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: document.querySelector("#message").value }),
    });
    answer.textContent = result.answer;
  } catch (error) {
    answer.textContent = error.message;
  }
});

document.querySelector("#upload").addEventListener("click", async () => {
  const file = document.querySelector("#file").files[0];
  const status = document.querySelector("#upload-status");
  if (!file) {
    status.textContent = "Choose a text file first.";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  try {
    const result = await api("/api/documents", { method: "POST", body: form });
    status.textContent = `Indexed ${result.name}`;
  } catch (error) {
    status.textContent = error.message;
  }
});

document.querySelector("#search").addEventListener("click", async () => {
  const results = document.querySelector("#results");
  try {
    const matches = await api("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: document.querySelector("#query").value }),
    });
    results.replaceChildren(
      ...matches.map((match) => {
        const item = document.createElement("article");
        const title = document.createElement("strong");
        title.textContent = match.name;
        const excerpt = document.createElement("p");
        excerpt.textContent = match.snippet;
        item.append(title, excerpt);
        return item;
      }),
    );
  } catch (error) {
    results.textContent = error.message;
  }
});
