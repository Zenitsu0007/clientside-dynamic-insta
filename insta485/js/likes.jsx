import React from "react";
import PropTypes from "prop-types";

export default function Likes({ likes, handleLike, load }) {
  // Button text changes based on whether the user likes the post or not

  const buttonText = likes.lognameLikesThis ? "Unlike" : "Like";

  if (!load) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <button
        onClick={handleLike}
        data-testid="like-unlike-button"
        type="button"
      >
        {buttonText}
      </button>
    </div>
  );
}

Likes.propTypes = {
  likes: PropTypes.shape({
    lognameLikesThis: PropTypes.bool,
    numLikes: PropTypes.number,
    url: PropTypes.string,
  }).isRequired,
  handleLike: PropTypes.func.isRequired,
  load: PropTypes.bool.isRequired,
};
