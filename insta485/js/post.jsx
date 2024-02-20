import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import PostComment from "./post_comment";
import DeleteComment from "./delete_comment";
import Likes from "./likes";


dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url, postid }) {
  /* Display image and post owner of a single post */

  const [comments, setComments] = useState([]);
  const [commentsUrl, setCommentsUrl] = useState("");
  const [created, setCreated] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [likes, setLikes] = useState({
    lognameLikesThis: false,
    numLikes: 0,
    url: null,
  });

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setComments(data.comments);
          setCommentsUrl(data.comments_url);
          setCreated(data.created);
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setOwnerShowUrl(data.ownerShowUrl);
          setPostShowUrl(data.postShowUrl); 
          if (data.likes.lognameLikesThis) {
            setLikes(data.likes);
          } else {
            setLikes({
              lognameLikesThis: data.likes.lognameLikesThis,
              numLikes: data.likes.numLikes,
              url: `/api/v1/likes/?postid=${postid}`,
            });
          }
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url, postid]);

  const CommentList = comments.map((comment) => (
    <div key={comment.commentid} className="comment-item">
      <a href={comment.ownerShowUrl}>{comment.owner}</a>
      <span data-testid="comment-text" className="comment-text">
        {comment.text}
      </span>
      {comment.lognameOwnsThis && (
        <DeleteComment
          commentId={comment.commentid}
          setComments={setComments}
        />
      )}
    </div>
  ));

  // Handle like/unlike action
  const handleLike = () => {
    // Determine the method based on currrnt like status
    const methods = likes.lognameLikesThis ? "DELETE" : "POST";
    const actionUrl = likes.url;
    console.log(actionUrl);

    fetch(actionUrl, {
      method: methods,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
    })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok.');
      return response.json();
    })
    .then(data => {
      setLikes(prevLikes => {
        // Toggle the like status
        const updatedLognameLikesThis = !prevLikes.lognameLikesThis;
    
        // Determine the new number of likes
        const updatedNumLikes = updatedLognameLikesThis ? prevLikes.numLikes + 1 : prevLikes.numLikes - 1;
    
        // Update the URL for the next action
        // For a like action, use the URL from the response
        // For an unlike action, you might revert to a generic URL or handle differently based on your API
        let updatedUrl = prevLikes.url;
        if (updatedLognameLikesThis) { // If it's now liked, the server's response should provide the next action's URL
          updatedUrl = data.url; // Assuming this is the URL for the unlike action
        } else {
          // For an unlike action, prepare the URL for the next like action.
          // This might involve setting a generic URL or constructing it based on known patterns.
          updatedUrl = `/api/v1/likes/?postid=${postid}`; // Example, adjust based on your API
        }
    
        return {
          ...prevLikes,
          lognameLikesThis: updatedLognameLikesThis,
          numLikes: updatedNumLikes,
          url: updatedUrl,
        };
      });
    })
    .catch(error => console.error('Error:', error));

  };

  // Render post image and post owner
  return (
    <div className="post">
      <header className="post-header">
        <div className="post-user">
          <a className="profile-pic" href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="profile_picture" />
          </a>
          <a href={ownerShowUrl}>{owner}</a>
        </div>
        <div className="time">
          <a href={postShowUrl}>{dayjs.utc(created).local().fromNow()}</a>
        </div>
      </header>
      <img src={imgUrl} alt="post_image" />
      <div>
        <div className="comments">{CommentList}</div>
        <div className="comment_like">
          <Likes likes={likes} handleLike={handleLike} />
          <PostComment url={commentsUrl} setComments={setComments} />
        </div>
      </div>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
  postid: PropTypes.number.isRequired,
};
