import React, { useState } from "react";
import { Items } from "./Items";

// Function to transform the API response to the desired format
function transformApiResponse(apiResponse) {
  const transformedData = [];

  // Loop through each movie entry
  apiResponse.movies.forEach((movie, index) => {
      // Replace '70-0-105' with '125-0-187' in the imageSrc
      const imageUrl = apiResponse.images[index].replace('70-0-105', '1000-0-1500');

      transformedData.push({
          id: index + 1,
          name: apiResponse.title[index],
          href: `https://letterboxd.com/film/${movie}/`,
          imageSrc: `https://a.ltrbxd.com/resized/${imageUrl}.jpg`,
          imageAlt: apiResponse.title[index],
          year: apiResponse.date[index]
      });
  });

  return transformedData;
}

export const Submit = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [showItems, setShowItems] = useState(false);
  const [movies, setMovies] = useState([]);
  const [username, setUsername] = useState(""); // State to hold the username

  const handleClick = async () => {
    setIsLoading(true);
    setShowItems(false);

    const PATH = process.env.API_PATH || 'default_path';
    const TOKEN = process.env.API_TOKEN || 'default_token';

    try {
      const response = await fetch(`${PATH}/recommend`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Authorization': TOKEN
        },
        body: JSON.stringify({ username: username}), // Pass username in the request body
      });
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      setMovies(transformApiResponse(data));
      setIsLoading(false);
      setShowItems(true);
    } catch (error) {
      console.error("Error fetching data:", error);
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setUsername(e.target.value); // Update the username state with input value
  };

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:justify-betweenw-full max-w-5xl mb-3 gap-6 pt-2 pb-1 px-2 mt-3 sm:px-4 px-2">
        <div className="relative mt-1 rounded-md shadow-sm">
          <input
            type="text"
            name="nameid"
            id="nameid"
            className="font-inter block w-full rounded-md border-0 py-1.5 pl-5 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            placeholder="martinscorcese"
            value={username} // Bind input value to username state
            onChange={handleInputChange} // Update username state on input change
          />
        </div>
      </div>
      <div className="flex flex-col sm:flex-row sm:justify-betweenw-full max-w-5xl mb-3 gap-6 pt-1 pb-1 px-2 mt-1 sm:px-4 px-2">
        <button
          onClick={handleClick}
          className="bg-black hover:bg-slate-800 text-white font-bold py-1 px-4 rounded"
          disabled={isLoading}
        >
          {isLoading ? "Loading..." : "Submit"}
        </button>
      </div>
      <div>{showItems && <Items movies={movies} />}</div>
    </>
  );
};
