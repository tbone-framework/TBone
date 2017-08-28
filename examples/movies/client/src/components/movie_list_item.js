import React from 'react';
import StarRating from 'react-star-rating';

const MovieListItem = ({movie, onMovieSelect}) => {
    return (
        <li onClick={() => onMovieSelect(movie)} className='list-group-item'>
            <div className='movie-item media'>
                <div className='media-left'>
                    <img className='media-object' src={movie.poster}/>
                </div>

                <div className='media-body'>
                    <h4 className='media-heading'>{movie.title}</h4>
                    <StarRating
                        name="movie-rating"
                        totalStars={5}
                        size={20}
                        editing={false}
                        rating={Math.floor(Math.random()*5+1)}
                    />
                    <div className='media-heading'>{movie.plot}</div>
                </div>
            </div>
        </li>
    );
};

export default MovieListItem;
