import React from "react";

export const Items = ({ movies }) => {
  return (
    <div className="bg-white">
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-4 lg:max-w-4xl lg:px-8 xl:max-w-7xl">
        <div className="mt-6 grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-3 xl:gap-x-8 justify-center">
          {movies.map((movie) => (
            <div key={movie.id} className={`group relative w-full max-w-[200px]`}>
              <div className="aspect-h-1 aspect-w-1 overflow-hidden rounded-md bg-white lg:aspect-none group-hover:opacity-75 lg:h-80">
                <img
                  src={movie.imageSrc}
                  alt={movie.imageAlt}
                  className="max-h-full h-full w-full object-contain object-center lg:h-full lg:w-full"
                />
              </div>
              <div className="mt-4 flex justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    <a href={movie.href} target="_blank" rel="noopener noreferrer">
                      <span aria-hidden="true" className="absolute inset-0" />
                      {movie.name}
                    </a>
                  </h3>
                </div>
                <p className="text-sm text-gray-500">{movie.year}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}