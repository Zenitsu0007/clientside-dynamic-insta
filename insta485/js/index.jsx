import React, { useState } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function Index({ url }) {
  window.history.scrollRestoration = "manual";
  // Initialize the next url and posts lists (results list in json file)
  const [next, setNext] = useState(url);
  const [posts, setPosts] = useState([]);
  const fetchNext = () => {
    // For initialize
    const fetchUrl = posts.length > 0 ? next : url;
    fetch(fetchUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setNext(data.next);
        setPosts([...posts, ...data.results]);
      })
      .catch((error) => {
        console.log(error)
      });
  };

  if (posts.length === 0) fetchNext();

  return (
    <div className="scrollableDiv" style={{ overflow: "auto" }}>
      <InfiniteScroll
        dataLength={posts.length}
        hasMore={!!next && next !== ""}
        next={fetchNext}
        loader={
          next !== null && next !== "" ? (
            <h4>Loading...</h4>
          ) : (
            <h4>No more posts</h4>
          )
        }
      >
        {posts.map((result) => (
          <div key={result.postid}>
            <Post url={result.url} postid={result.postid} />
          </div>
        ))}
      </InfiniteScroll>
    </div>
  );
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};
