import React, { Component } from 'react';

class SearchBar extends Component {
    constructor(props){
        super(props);

        this.state = {term: ''};

        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
    }

    onInputChange(event){
        this.setState({term: event.target.value});
    }
    onFormSubmit(event){
        event.preventDefault();
        // this.props.fetchWeather(this.state.term);
        this.props.onSearchTermChange(this.state.term);
        // reset the term
        this.setState({term: ''});
    }
    render(){
        return (
            <form
                onSubmit={this.onFormSubmit} 
                className='input-group'>
                <input
                    placeholder='Search for movies'
                    className='form-control'
                    value={this.state.term}
                    onChange={this.onInputChange}
                />
                <span className='input-group-btn'>
                    <button type='submit' className='btn btn-secondary'>Search</button>
                </span>  
            </form>
        );
    }

    onInputChange(event){
        var term = event.target.value;
        this.setState({term});
    }
}

export default SearchBar;
