import React, { useState } from "react";
import PropTypes from "prop-types";

export default function PostComment({ url, setComments }) {
  const [text, setText] = useState("");
  function handleText(e) {
    setText(e.target.value);
  }

  function handleComment(e) {
    e.preventDefault();
    if (text.trim() !== "") {
      // Call REST API to post comment
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw new Error("Failed to post comment");
          return response.json();
        })
        .then((newComment) => {
          setComments((prevComments) => [...prevComments, newComment]);
          setText(""); // Clear input after posting
        })
        .catch((error) => console.error(error));
    }
  }
  

  return (
    <form data-testid="comment-form" onSubmit={handleComment}>
      <input
        type="text"
        value={text}
        onChange={handleText}
        placeholder="Add a comment..."
      />
    </form>
  );
}

PostComment.propTypes = {
  url: PropTypes.string.isRequired,
  setComments: PropTypes.func.isRequired,
};
