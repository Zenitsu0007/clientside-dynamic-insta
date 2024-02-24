import React from "react";
import PropTypes from "prop-types";

export default function DeleteComment({ commentId, setComments }) {
  function handleDelete(e) {
    e.preventDefault();
    const deleteUrl = `/api/v1/comments/${commentId}/`;
    // Call REST API to delete comment
    fetch(deleteUrl, {
      method: "DELETE",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed to delete comment");
        // Update comments state to remove the deleted comment
        setComments((prevComments) =>
          {
            prevComments.filter((comment) => comment.commentid !== commentId);
          }
        );
      })
      .catch((error) => console.error(error));
  }

  return (
    <button
      data-testid="delete-comment-button"
      type="button"
      onClick={handleDelete}
    >
      Delete
    </button>
  );
}

DeleteComment.propTypes = {
  commentId: PropTypes.number.isRequired,
  setComments: PropTypes.func.isRequired,
};
