import React from 'react';


const MovieDetail = ({movie}) => {
    if(!movie){
        return <div></div>;
    }

    console.log('rendering movie', movie);
    
    return (
        <div className='MovieDetail col-md-8'>
            <div className='embed-responsive embed-responsive-16by9'>
                <iframe className='embed-responsive-item' src=''></iframe>
            </div>
            <div className='details'>
                <div>{movie.snippet.title}</div>
                <div>{movie.snippet.description}</div>
            </div>
        </div>
    );
};

export default MovieDetail;
