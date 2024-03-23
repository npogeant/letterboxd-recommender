import Link from "next/link";
import React from "react";

export const Header = () => {
  
  return (
    <header className="flex flex-col sm:flex-row sm:justify-betweenw-full max-w-5xl mb-3 gap-6 pt-4 pb- px-2 mt-3 border-b pb-7 sm:px-4 px-2 border-gray-200 gap-2">
      <Link href="/" className="flex flex-col">
        <h1 className="font-inter font-bold sm:text-xl flex items-center text-gray-1000">
          Movie Recsys
        </h1>
        <p className="font-inter font-bold text-gray-700">
          A recommender system using your Letterboxd diary
        </p>
      </Link>
    </header>
  );
};
