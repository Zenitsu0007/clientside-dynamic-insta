import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function Index({ url }) {
  // Initialize the next url and postslists (results list in json file)
  const [next, setNext] = useState(url);
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;
    window.history.scrollRestoration = "manual";
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setNext(data.next);
          setPosts(data.results);
        }
      })
      .catch((error) => console.log(error));
    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render,
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const fetchNext = () => {
    // Implement infinite scrolling by keep adding posts to post data
    fetch(next, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setNext(data.next);
        setPosts([...posts, ...data.results]);
      })
      .catch((error) => console.log(error));
  };

  return (
    // Return the index.html with infinite scrolling
    <div className="scrollableDiv" style={{ overflow: "auto" }}>
      <InfiniteScroll
        dataLength={posts.length}
        hasMore={next !== null}
        next={fetchNext}
        loader={<h4>Loading...</h4>}
      >
        {posts.map((results) => (
          <div key={results.postid}>
            <Post url={results.url} postid={results.postid} />
          </div>
        ))}
      </InfiniteScroll>
    </div>
  );
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};
