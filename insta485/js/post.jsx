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
  const [likes, setLikes] = useState({});

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

    fetch(actionUrl, {
      method: methods,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
    })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok.');
      return (methods === "POST" ? response.json() : Promise.resolve()); 
      // THIS LINE IS VERY IMPORTANT!!! detele request does not return a json object
    })
    .then(data => {
      if (methods === "POST") {
        // Handle state update for a successful "Like" action
        setLikes({
          lognameLikesThis: true,
          numLikes: likes.numLikes + 1,
          url: data.url, // Assuming this is how your server responds with the "Unlike" URL
        });
      } else {
        // Handle state update for a successful "Unlike" action
        setLikes(prevLikes => ({
          lognameLikesThis: false,
          numLikes: prevLikes.numLikes > 0 ? prevLikes.numLikes - 1 : 0, // Safeguard to prevent negative likes
          url: `/api/v1/likes/?postid=${postid}`, // Reset or prepare the URL for a new "Like" action
        }));
      }
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
        <div>
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
