import React from 'react';
import MovieListItem from './movie_list_item';

const MovieList = (props) => {
    const movieItems = props.movies.map((movie) => {
        return (
            <MovieListItem
                onMovieSelect={props.onMovieSelect}
                key={movie._id}
                movie={movie}
            />
        );
    });
    return (
        <ul className='col-md-12 list-group'>
            {movieItems}
        </ul>
    );
}

export default MovieList;
