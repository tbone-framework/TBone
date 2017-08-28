import _ from 'lodash';
import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

import SearchBar from './components/search_bar';
import MovieList from './components/movie_list';
import MovieDetail from './components/movie_detail';


// create a new component that produces HTML

class App extends Component {
    constructor(props){
        super(props);
        this.state = {
            movies: [],
            selectedMovie: null
        }

      // this.movieSearch('Robert De Niro');
    }

    movieSearch(term){  
        var self = this;
        axios.get(`http://localhost:8000/api/movies/movie/?q=${term}`).then(function(response){
            self.setState({
                movies: response.data.objects,
                selectedMovie: null
            });
        });
    }

    render(){
        const movieSearch = _.debounce((term) => {this.movieSearch(term)}, 300);
        return (
            <div>
                <h2>Movie Database</h2>
                <hr/>
                <SearchBar onSearchTermChange={movieSearch} />
                <MovieDetail movie={this.state.selectedMovie} />
                <MovieList
                  onMovieSelect={selectedMovie => this.setState({selectedMovie}) }
                  movies={this.state.movies}
                />
            </div>
        );
    }
}
// Take this component generated HTML and put it on the page (in the DOM)


ReactDOM.render(<App />, document.querySelector('.container'));
