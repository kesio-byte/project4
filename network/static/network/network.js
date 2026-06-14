// -------------------- MAIN SCRIPT --------------------
document.addEventListener("DOMContentLoaded", () => {
  setupEditButtons();
  setupLikeButtons();
});

// -------------------- EDIT POST --------------------
function setupEditButtons() {
  document.querySelectorAll(".edit-btn").forEach(button => {
    button.onclick = () => {

      // Get post ID and relevants elements
      const postId = button.dataset.id;
      const postDiv = button.closest(".post");
      const contentEl = postDiv.querySelector(".content");

      // Prevent multiple editors
      if (contentEl.querySelector("textarea")) return;

      const originalContent = contentEl.innerText;

      // Replace contnt with textarea + buttons
      contentEl.innerHTML = `
        <textarea class="form-control mb-2" rows="3">${originalContent}</textarea>
        <div class="btn-group mb-2">
          <button class="btn btn-sm btn-success save-btn">Save</button>
          <button class="btn btn-sm btn-secondary cancel-btn">Cancel</button>
        </div>
      `;
// Get references to new elements
      const textarea = contentEl.querySelector("textarea");
      const saveBtn = contentEl.querySelector(".save-btn");
      const cancelBtn = contentEl.querySelector(".cancel-btn");

      // SAVE HANDLER
      saveBtn.onclick = () => {
        console.log("Save clicked:", textarea.value);

        saveBtn.disabled = true; // prevent double clicks

        fetch(`/edit_post/${postId}`, { // Send the updted content to the server 
          method: "PUT",
          body: JSON.stringify({ content: textarea.value }),
          headers: { "X-CSRFToken": getCookie("csrftoken") }
        })
        .then(response => response.json())
        .then(result => {
          console.log("Server response:", result);

          if (result.message) {
            contentEl.innerHTML = `<p class="card-text content">${textarea.value}</p>`;
          } else {
            alert(result.error);
            saveBtn.disabled = false;
          }
        })
        .catch(error => {// Log any errors that occur d'ring the fetch request
          console.error("Error saving post:", error);
          saveBtn.disabled = false;
        });
      };

      // CANCEL HANDLER
      cancelBtn.onclick = () => {
        console.log("Cancel clicked");
        contentEl.innerHTML = `<p class="card-text content">${originalContent}</p>`;
      };
    };
  });
}

// -------------------- LIKE / UNLIKE --------------------
function setupLikeButtons() {
  document.querySelectorAll(".like-btn").forEach(button => {
    button.onclick = () => {
      const postId = button.dataset.id;
      const postDiv = button.closest(".post");
      const likesCountEl = postDiv.querySelector(".likes-count");

      console.log("Like clicked:", { postId, postDiv, likesCountEl });// Send the like/unlike request to the server

      fetch(`/toggle_like/${postId}`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") }
      })
      .then(response => response.json())// Log the raw response for debugging
      .then(result => {
        console.log("Server response:", result);
        likesCountEl.innerText = result.likes_count;
        button.innerText = result.liked ? "Unlike" : "Like";
      })
      .catch(error => console.error("Error toggling like:", error));
    };
  });
}

// -------------------- CSRF HELPER --------------------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {// Decode the cookie value to handle special characters
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
